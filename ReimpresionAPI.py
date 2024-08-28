from flask import Flask, jsonify, request, Response
import logging
from logging.handlers import RotatingFileHandler
import pyodbc
import threading
import subprocess
import os
from functools import wraps
import unicodedata
import re

app = Flask(__name__)

# Configuración del logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Decorador para requerir autenticación básica
def check_auth(username, password):
    return username == 'Fanafesa2024' and password == 's4c4nd4_2024'

def authenticate():
    return Response(
        'No se pudo verificar su nivel de acceso para esa URL.\n'
        'Tienes que iniciar sesión con las credenciales adecuadas.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/reimpresion', methods=['GET'])
def index():
    return jsonify({'message': 'El servidor está funcionando correctamente!'})

@app.route('/reimpresion/buscar_localidad', methods=['GET'])
@requires_auth
def buscar_localidad():
    nombre_localidad = request.args.get('localidad')
    cantidad = request.args.get('cantidad')
    fecha = request.args.get('fecha')

    if not nombre_localidad:
        return jsonify({'respuesta': 'Falta el parámetro "localidad"'}), 400

    if not cantidad:
        return jsonify({'respuesta': 'Falta el parámetro "cantidad"'}), 400

    if not fecha:
        return jsonify({'respuesta': 'Falta el parámetro "fecha"'}), 400

    # Convertir la localidad a mayúsculas y quitar acentos
    nombre_localidad = normalize_string(nombre_localidad.upper())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM rpa_farmacias WHERE localidad = ?"
        cursor.execute(query, (nombre_localidad,))
        row = cursor.fetchone()

        if row:
            response_data = {
                'usuario': row.usuario,
                'password': row.password,
                'correo': "sergioarmandoalzagadiaz@gmail.com",
                'cantidad': '$ ' + cantidad,
                'fecha': fecha
            }
            response_data_user = {
                'respuesta': 'El proceso se está ejecutando'
            }

            insert_query = """
            INSERT INTO rpa_info_consulta (usuario, password, correo, cantidad, fecha)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (response_data['usuario'], response_data['password'],
                                           response_data['correo'], response_data['cantidad'],
                                           response_data['fecha']))
            conn.commit()

            threading.Thread(target=ejecutar_rpa).start()  # Ejecutar RPA sin pasar parámetros

            return jsonify(response_data_user)
        else:
            return jsonify({'respuesta': 'Localidad no encontrada'}), 404
    except pyodbc.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def get_db_connection():
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "Server=fanafesadbkenos.database.windows.net;"
        "Database=fanafesadb;"
        "UID=admindbkenos;"  
        "PWD=K3n0sFanafes4!.*;"  
    )
    return pyodbc.connect(connection_string)

def ejecutar_rpa():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del directorio actual del script
    uirobot_path = "C:\\Users\\adminkenos\\AppData\\Local\\Programs\\UiPath\\Studio\\UiRobot.exe"
    process_name = "DescargaTrasaccionesSucursal.1.0.13"
    
    # Construye la ruta completa del archivo .nupkg
    nupkg_path = os.path.join(script_dir, f"{process_name}.nupkg")

    args = [
        uirobot_path,
        "execute",
        "--file", nupkg_path
    ]
    try:
        subprocess.run(args, check=True)
        app.logger.info(f"RPA executed successfully.")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"RPA execution error: {e}")

def normalize_string(s):
    # Normalizar la cadena para quitar acentos
    nfkd_form = unicodedata.normalize('NFKD', s)
    return re.sub(r'[\u0300-\u036f]', '', nfkd_form)

if __name__ == '__main__':
    app.run(debug=True)
