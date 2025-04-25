from flask import Flask, jsonify, request
from pyspark.sql import SparkSession,Window
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from pyspark.sql.functions import row_number, current_timestamp,col
import tests
from aux import create_table
import pymysql

app = Flask(__name__)
# Crear SparkSession
spark = SparkSession.builder \
    .appName("spark_api") \
    .config("spark.jars.packages", "mysql:mysql-connector-java:8.0.33") \
    .getOrCreate()

JDBC_OPTIONS = {
    "url": "jdbc:mysql://db:3306/flask_db",
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "flask_user",
    "password": "flask_pass"
}

# Conexion directa a myql para realizar querys
mysql_config = {
    'host': 'db', 
    'user': 'flask_user',
    'password': 'flask_pass',
    'database': 'flask_db'
}

# Schema de la tabla jobs
schema_jobs = StructType([
    StructField("id", IntegerType(), True),
    StructField("job", StringType(), True)
])

# Schema de la tabla departaments
schema_departments = StructType([
    StructField("id", IntegerType(), True),
    StructField("department", StringType(), True)
])

# Schema de la tabla hired_employees, agrego load_timestamp para manejar los registros actuales
schema_employees = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("datetime",StringType(), True),
    StructField("department_id",IntegerType(), True),
    StructField("job_id",IntegerType(), True),
    StructField("load_timestamp",TimestampType(), True),
])

# Diccionario con schemas para reutilizar en funciones
schemas = {
    'jobs': schema_jobs,
    'departments': schema_departments,
    'hired_employees': schema_employees
}

@app.route('/')
def route():
    html = """<h1> Hola (futuro) colega! </h1>
    <h2>Esta es mi API para el challenge, aca tenes el listado de opciones para probarla. Suerte!</h2>
    <div>1- Probar conexion a base de datos: ingresar a http://localhost:8080/db-check </div>
    <div>2- Truncar tablas <b>jobs o departments</b>: correr en terminal <i>curl -X POST -F "file=@jobs.csv" http://localhost:8080/upload-files-truncate</i> </div>
    <div>3- Ingesta tabla <b>hired_employees</b>: correr en terminal <i>curl -X POST -F "file=@hired_employees.csv" http://localhost:8080/process-employees</i> </div>"""
    return html

@app.route('/db-check')
def db_check():
    try:
        df = spark.read \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("query", "SELECT 1 AS test") \
            .load()
        
        result = df.collect()
        return jsonify({
            "status": "Conexión exitosa con Spark",
            "resultado": result
        })
    
    except Exception as e:
        return jsonify({"status": "Error de conexión", "error": str(e)}), 500
    
@app.route('/upload-files-truncate', methods=['POST'])
def upload_files_truncate():
    # Validamos que el file exista y tenga el nombre correcto
    test_result = tests.validate_file(request.files)
    if test_result is not None:
        return jsonify({"error": test_result}), 400
    
    try:
        # Creamos window function
        window_spec = Window.partitionBy("id").orderBy("id")
        # Obtenemos el archivo del request
        file = request.files['file']
        file_name = file.filename
        if file_name not in ['jobs.csv','departments.csv']:
            return jsonify({"error": 'Solo puede usar este endopoint para jobs.csv o departments.csv'}), 400
            
        table = file_name.split('.')[0]
        # Guardamos temporalmente en este path y 
        temp_path = f"/tmp/temp_{file_name}"
        file.save(temp_path)

        # Elegimos schema correcto
        schema = schemas[table]

        # Leemos la data, usando schema definido antes, y quitamos duplicados en la columna id
        df = spark.read.format("csv") \
            .option("header", "false") \
            .schema(schema) \
            .load(temp_path)  \
            .withColumn("row_number", row_number().over(window_spec)) \
            .filter("row_number = 1") \
            .drop("row_number")
        
        # Truncamos tabla (ASUMO que la tabla JOBS no se modificara seguido, es decir, se cargara una sola vez, por eso truncamos)
        df.write \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("dbtable", table) \
            .mode("overwrite") \
            .save()
        
        return jsonify({
            "message": f"Archivo {table} procesado correctamente",
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process-employees',methods=['POST'])
def bronze_employees():
    # Validamos que el file exista y tenga el nombre correcto
    test_result = tests.validate_file(request.files)
    if test_result is not None:
        return jsonify({"error": test_result}), 400
    
    try:
        
        # Obtenemos el archivo del request
        file = request.files['file']
        if file.filename != 'hired_employees.csv':
            return jsonify({"error": "Solo puede usar este endopoint para hired_employees.csv"}), 400

        # Guardamos temporalmente en este path
        temp_path = f"/tmp/temp_hired_employees.csv"
        file.save(temp_path)

        # Leemos la data
        df = spark.read.format("csv") \
            .option("header", "false") \
            .schema(schema_employees) \
            .load(temp_path)  \
            .withColumn("load_timestamp", current_timestamp())

        # Escribimos tal cual vino en batchs de 1000 registros en la tabla HISTORICA,
        df.write \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("dbtable", 'hired_employees_historical') \
            .option('batchsize',"1000") \
            .mode("append") \
            .save()
        
        result = silver_employees(df)

        return jsonify({
            "message": "Archivo hired_employees.csv procesado correctamente en batchs de 1000 registros",
            "resultado": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def silver_employees(df_last_updated):
    try:
        temp_table = 'temp_employees'
        # Creamos window function
        window_spec = Window.partitionBy("id").orderBy("load_timestamp")

        # Guardamos en tabla temporal los nuevos registros
        # Qutiamos duplicados en id dentro del mismo batch
        # Quitamos id, department_id y job_id nulos
        df_last_updated = df_last_updated.filter(col("id").isNotNull()) \
            .filter(col("department_id").isNotNull()) \
            .filter(col("job_id").isNotNull()) \
            .withColumn("row_number", row_number().over(window_spec)) \
            .filter("row_number = 1") \
            .drop("row_number")
        
        df_last_updated.write \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("dbtable", temp_table) \
            .mode("overwrite") \
            .save()
        
        connection = pymysql.connect(**mysql_config)
        cursor = connection.cursor()
        
        
        # Aplicamos UPSERT, Solo tiene en cuenta los ultimos registros agregados en el ultimo file, 
        # Si el id es nuevo, lo inserta, si ya existe, lo actualiza con el ultimo dato.
        merge_query = f"""
            INSERT INTO hired_employees 
            SELECT * FROM {temp_table}
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                department_id = VALUES(department_id),
                job_id = VALUES(job_id),
                load_timestamp = VALUES(load_timestamp)
        """
        
        cursor.execute(merge_query)
        connection.commit()
        
        # Limpiamos la tabla temporal
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
        connection.commit()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        return str(e)

@app.route('/query-1')
def query_1():
    try:
        query = """
        SELECT
            d.department as Department,
            j.job as Job,
            SUM( CASE WHEN QUARTER(STR_TO_DATE(e.datetime, '%Y-%m-%dT%H:%i:%sZ')) = 1 THEN 1 ELSE 0 END) as Q1,
            SUM( CASE WHEN QUARTER(STR_TO_DATE(e.datetime, '%Y-%m-%dT%H:%i:%sZ')) = 2 THEN 1 ELSE 0 END) as Q2,
            SUM( CASE WHEN QUARTER(STR_TO_DATE(e.datetime, '%Y-%m-%dT%H:%i:%sZ')) = 3 THEN 1 ELSE 0 END) as Q3,
            SUM( CASE WHEN QUARTER(STR_TO_DATE(e.datetime, '%Y-%m-%dT%H:%i:%sZ')) = 4 THEN 1 ELSE 0 END) as Q4
        FROM hired_employees e
        JOIN departments d ON d.id = e.department_id
        JOIN jobs j ON j.id = e.job_id
        WHERE STR_TO_DATE(e.datetime, '%Y-%m-%dT%H:%i:%sZ') BETWEEN '2021-01-01' AND '2021-12-31'
        GROUP BY 1,2
        ORDER BY 1 ASC, 2 ASC
        """
        df = spark.read \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("query", query) \
            .load()
        
        result = df.collect()
        return create_table("QUERY 1", ['Department','Job','Q1','Q2','Q3','Q4'], result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query-2')
def query_2():
    try:
        # Primero calculo el promedio de la cantidad de empleados por departmento
        # Necesito saber cuantos empleados hay por departmento
        query_count = """
        SELECT AVG(aux.cantidad)
        FROM 
            (SELECT e.department_id, count(e.id) as cantidad
            FROM hired_employees as e
            WHERE e.datetime like '2021%'
            GROUP BY 1) AS aux
        """
        promedio = spark.read \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("query", query_count) \
            .load() \
            .collect()[0][0]
        
        # Traigo los datos y filtro el count segun el promedio antes calculado.
        query = f"""SELECT d.id as id, d.department as department, count(e.id) as hired
        FROM departments as d 
        JOIN hired_employees as e ON e.department_id = d.id
        GROUP BY 1,2
        HAVING count(e.id) > {promedio}
        ORDER BY 3 DESC
        """
        df = spark.read \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("query", query) \
            .load()
        
        result = df.collect()
        return create_table(f"QUERY 2 - Promedio: {promedio}", ['id','department','hired'], result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



