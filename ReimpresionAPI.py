import subprocess
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/reimpresiontickets'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Farmacia(db.Model):
    __tablename__ = 'farmacia'
    id = db.Column(db.Integer, primary_key=True)
    localidad = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)

@app.route('/buscar_localidad', methods=['GET'])
def buscar_localidad():
    nombre_localidad = request.args.get('localidad')
    cantidad = request.args.get('cantidad')
    fecha = request.args.get('fecha')

    # Verifica que se haya proporcionado la localidad
    if not nombre_localidad:
        return jsonify({'error': 'Falta el parámetro "localidad"'}), 400

    # Verifica que se haya proporcionado la cantidad
    if not cantidad:
        return jsonify({'error': 'Falta el parámetro "cantidad"'}), 400

    # Verifica que se haya proporcionado la fecha
    if not fecha:
        return jsonify({'error': 'Falta el parámetro "fecha"'}), 400

    # Consulta la base de datos
    resultado = Farmacia.query.filter_by(localidad=nombre_localidad).first()

    if resultado:
        response_data = {
            'usuario': resultado.usuario,
            'password': resultado.password,
            'correo': resultado.correo,
            'cantidad': cantidad,
            'fecha': fecha
        }

        # Guardar la información en un archivo Excel
        guardar_informacion_excel(response_data)

        # Ejecutar el RPA de UiPath si se encuentra la localidad
        ejecutar_rpa(response_data)

        return jsonify(response_data)
    else:
        return jsonify({'error': 'Localidad no encontrada'}), 404

def guardar_informacion_excel(data):
    # Definir el nombre del archivo Excel
    file_name = "informacion.xlsx"

    # Crear un DataFrame con la información
    df = pd.DataFrame([data])

    # Guardar o sobrescribir el archivo Excel
    df.to_excel(file_name, index=False)


def ejecutar_rpa(params):
    # Define la ruta de UiRobot.exe
    uirobot_path = "C:\\Users\\sergio.alzaga\\AppData\\Local\\Programs\\UiPath\\Studio\\UiRobot.exe"

    # Define el nombre del proceso de UiPath tal como está registrado
    process_name = "ReimpresionTicket.1.0.7"

    # Construir la lista de argumentos para UiRobot.exe
    args = [
        uirobot_path,
        "execute",
        "--file", f"C:\\Users\\sergio.alzaga\\Documents\\UiPath\\{process_name}.nupkg",
        "--input", f"{{\"usuario\":\"{params['usuario']}\",\"pass\":\"{params['password']}\",\"destino\":\"{params['correo']}\",\"importe\":\"{params['cantidad']}\",\"fechaBusqueda\":\"{params['fecha']}\"}}"
    ]

    # Ejecutar el RPA
    subprocess.run(args)

if __name__ == '__main__':
    app.run(debug=True)
