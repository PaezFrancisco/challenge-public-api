from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
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
    
@app.route('/upload-jobs', methods=['POST'])
def upload_jobs():
    # Validamos que el file exista y tenga el nombre correcto
    test_result = tests.validate_file(request.files, 'jobs')
    if test_result is not None:
        return jsonify({"error": test_result}), 400
    
    try:
        # Obtenemos el archivo del request
        file = request.files['file']

        # Guardamos temporalmente en este path y leemos la data, usando schema definido antes
        temp_path = "/tmp/temp_jobs.csv"
        file.save(temp_path)
        df = spark.read.format("csv") \
            .option("header", "false") \
            .schema(schema_jobs) \
            .load(temp_path) \
        
        # Truncamos tabla (ASUMO que la tabla JOBS no se modificara seguido, es decir, se cargara una sola vez, por eso truncamos)
        df.write \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("dbtable", 'jobs') \
            .mode("overwrite") \
            .save()
            
        
        df_test = spark.read.format("jdbc").options(**JDBC_OPTIONS).option("query", "select * from jobs limit 1").load()
        result = df_test.collect()
        return jsonify({
            "message": "Archivo Jobs procesado correctamente",
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/upload-departments', methods=['POST'])
def upload_departments():
    # Validamos que el file exista y tenga el nombre correcto
    test_result = tests.validate_file(request.files, 'departments')
    if test_result is not None:
        return jsonify({"error": test_result}), 400
    
    try:
        # Obtenemos el archivo del request
        file = request.files['file']

        # Guardamos temporalmente en este path y leemos la data, usando schema definido antes
        temp_path = "/tmp/temp_departments.csv"
        file.save(temp_path)
        df = spark.read.format("csv") \
            .option("header", "false") \
            .schema(schema_departments) \
            .load(temp_path) \
        
        # Truncamos tabla (ASUMO que la tabla DEPARTMENTS no se modificara seguido, es decir, se cargara una sola vez, por eso truncamos)
        df.write \
            .format("jdbc") \
            .options(**JDBC_OPTIONS) \
            .option("dbtable", 'departments') \
            .mode("overwrite") \
            .save()
            
        
        df_test = spark.read.format("jdbc").options(**JDBC_OPTIONS).option("query", "select * from departments limit 1").load()
        result = df_test.collect()
        return jsonify({
            "message": "Archivo Departments procesado correctamente",
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



