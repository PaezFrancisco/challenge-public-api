from flask import Flask, jsonify
from pyspark.sql import SparkSession

app = Flask(__name__)

# Crear SparkSession
spark = SparkSession.builder \
    .appName("MiAPIConSpark") \
    .config("spark.jars.packages", "mysql:mysql-connector-java:8.0.33") \
    .getOrCreate()

# Opciones comunes en todas las consultas
JDBC_OPTIONS = {
    "url": "jdbc:mysql://db:3306/flask_db",
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "flask_user",
    "password": "flask_pass"
}

@app.route('/')
def route():
    html = """<h1> Hola (futuro) colega! </h1>
    <h2>Esta es mi API para el challenge, aca tenes el listado de opciones para probarla. Suerte!</h2>
    <div>1- Cargar Base de datos: </div>
    <div>2- </div>"""
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
            "resultado": [row.asDict() for row in result]
        })
    
    except Exception as e:
        return jsonify({"status": "Error de conexión", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



