import time
import pyodbc
import os
import subprocess
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conexión a la base de datos SQL Server
connection = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=Fanafesa;"
    "Trusted_Connection=yes;"
)

def ejecutar_rpa():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del directorio actual del script
    uirobot_path = r"C:\Users\sergio.alzaga\AppData\Local\Programs\UiPath\Studio\UiRobot.exe"  # Ruta completa al ejecutable UiRobot
    process_name = r"C:\Users\sergio.alzaga\Documents\Reimpresion\ReimpresionTicketFanafesa.1.0.8"  # Escapado corregido
    
    # Construye la ruta completa del archivo .nupkg
    nupkg_path = os.path.join(script_dir, f"{process_name}.nupkg")

    args = [
        uirobot_path,
        "execute",
        "--file", nupkg_path
    ]
    try:
        subprocess.run(args, check=True, shell=True)  # Agrega shell=True si es necesario
        logger.info("RPA executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"RPA execution error: {e}")
    except PermissionError as e:
        logger.error(f"Permission error: {e}")

def check_and_execute_rpa():
    cursor = connection.cursor()
    
    # Consulta para verificar registros con status = 0
    cursor.execute("SELECT TOP 1 [id] FROM [Fanafesa].[dbo].[rpa_info_consulta] WHERE [status] = 0")
    row = cursor.fetchone()
    
    if row:
        record_id = row[0]
        logger.info(f"Found record with ID {record_id} with status 0. Executing RPA...")
        
        # Ejecuta el RPA
        ejecutar_rpa()
        
        # Actualiza el registro a status = 1
        cursor.execute("UPDATE [Fanafesa].[dbo].[rpa_info_consulta] SET [status] = 1 WHERE [id] = ?", (record_id,))
        connection.commit()
        logger.info(f"Record with ID {record_id} has been updated to status 1.")
        
        # Retorna True si se encontró un registro y se ejecutó el RPA
        return True
    else:
        logger.info("No records with status 0 found.")
        return False
    
    cursor.close()

if __name__ == '__main__':
    while True:
        # Verifica y ejecuta RPA si es necesario
        rpa_executed = check_and_execute_rpa()
        
        # Si se ejecutó el RPA, espera 1 minuto y 30 segundos
        if rpa_executed:
            time.sleep(90)  # 90 segundos = 1 minuto y 30 segundos
        else:
            # Si no se ejecutó el RPA, espera 20 segundos
            time.sleep(20)
