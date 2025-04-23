from flask import Flask, jsonify, request
from pyspark.sql import SparkSession,Window
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from pyspark.sql.functions import row_number
import tests

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

# Schema de la tabla hired_employees
schema_employees = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("datetime",StringType(), True),
    StructField("departament_id",IntegerType(), True),
    StructField("job_id",IntegerType(), True),
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
    <div>2- Truncar tabla <b>jobs</b>: correr en terminal <i>curl -X POST -F "file=@jobs.csv" http://localhost:8080/upload-jobs</i> </div>"""
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



