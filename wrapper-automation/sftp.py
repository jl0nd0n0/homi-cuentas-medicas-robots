import paramiko
from dotenv import load_dotenv
import os

def sftp_send_file(archivo_local, archivo_remoto):
    # Cargar configuración
    load_dotenv()
    host = os.getenv("SFTP_HOSTNAME")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USERNAME")
    password = os.getenv("SFTP_PASSWORD")

    # Crear conexión SSH y SFTP
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    sftp = ssh.open_sftp()

    # Crear directorios remotos si no existen
    dir_remoto = os.path.dirname(archivo_remoto)
    try:
        sftp.chdir(dir_remoto)
    except IOError:
        # Si no existe, lo creamos recursivamente
        path_parts = dir_remoto.strip("/").split("/")
        current_path = ""
        for part in path_parts:
            current_path += f"/{part}"
            try:
                sftp.chdir(current_path)
            except IOError:
                sftp.mkdir(current_path)
                sftp.chdir(current_path)

    # Subir archivo
    sftp.put(archivo_local, archivo_remoto)
    print(f"✅ Archivo cargado correctamente en: {archivo_remoto}")

    sftp.close()
    ssh.close()
