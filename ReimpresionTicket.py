from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos SQL Server
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@server/database_name?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Farmacia(db.Model):
    __tablename__ = 'farmacias'
    id = db.Column(db.Integer, primary_key=True)
    localidad = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)

# Validación de usuario y contraseña
@app.before_request
def validar_credenciales():
    auth = request.authorization
    if not auth or auth.username != 'farmaciaScanda' or auth.password != 'Scanda132':
        return abort(401, description="Credenciales incorrectas")

@app.route('/buscar_localidad', methods=['GET'])
def buscar_localidad():
    nombre_localidad = request.args.get('localidad')
    cantidad = request.args.get('cantidad')  # Obtiene la cantidad
    fecha = request.args.get('fecha')  # Obtiene la fecha

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
        return jsonify({
            'usuario': resultado.usuario,
            'password': resultado.password,
            'correo': resultado.correo,
            'cantidad': cantidad,  # Incluye la cantidad en la respuesta
            'fecha': fecha  # Incluye la fecha proporcionada por el usuario
        })
    else:
        return jsonify({'error': 'Localidad no encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)
