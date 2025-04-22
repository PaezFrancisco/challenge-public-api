from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

#Configuracion app
#Conexion base de datos con app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://flask_user:flask_pass@db:3306/flask_db"
db = SQLAlchemy(app)

@app.route('/')
def route():
    html = """<h1> Hola (futuro) colega! </h1>
    <h2>Esta es mi API para el challenge, aca tenes el listado de opciones para probarla. Suerte!</h2>
    <div>1- Cargar Base de datos: </div>
    <div>2- </div>"""
    return html

@app.route('/db-check')
def db_check():
    #Testeo de conexion
    try:
        result = db.session.execute(text('SELECT 1')).fetchone()
        if result:
            return jsonify({"status": "Conexion exitosa a la base de datos"})
    except Exception as e:
        return jsonify({"status": "Error de conexion", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



