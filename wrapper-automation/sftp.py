import os
import tempfile
import shutil
import pikepdf
from dotenv import load_dotenv
import paramiko


def comprimir_pdf_pikepdf(ruta_entrada, ruta_salida):
    """
    Comprime un PDF usando pikepdf (compatible con todas las versiones).
    Elimina metadata y optimiza el contenido.
    """
    try:
        with pikepdf.open(ruta_entrada) as pdf:
            # Eliminar metadatos si existen
            if '/Info' in pdf.docinfo:
                del pdf.docinfo['/Info']

            # Opciones de guardado para máxima compresión
            pdf.save(
                ruta_salida,
                compress_streams=True,   # Comprimir flujos internos
                recompress_flate=True     # Recomprimir contenido
            )
        print(f"📎 PDF comprimido guardado: {ruta_salida}")
        return True
    except Exception as e:
        print(f"\n❌ Error al comprimir con pikepdf: {e}")
        return False


def sftp_send_file(archivo_local, archivo_remoto):
    # Cargar configuración
    load_dotenv()
    host = os.getenv("SFTP_HOSTNAME")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USERNAME")
    password = os.getenv("SFTP_PASSWORD")

    # Crear directorio temporal para el archivo comprimido
    temp_dir = tempfile.mkdtemp()
    nombre_archivo = os.path.basename(archivo_remoto)
    archivo_comprimido = os.path.join(temp_dir, f"{nombre_archivo}.tmp.pdf")

    # Comprimir el PDF con pikepdf
    '''
    if not comprimir_pdf_pikepdf(archivo_local, archivo_comprimido):
        print("⚠️ No se pudo comprimir. Enviando archivo original...")
        archivo_comprimido = archivo_local  # Fallback al original
    
    # Establecer conexión SSH y SFTP
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    sftp = ssh.open_sftp()

    # Crear directorios remotos si no existen
    dir_remoto = os.path.dirname(archivo_remoto)
    try:
        sftp.chdir(dir_remoto)
    except IOError:
        path_parts = dir_remoto.strip("/").split("/")
        current_path = ""
        for part in path_parts:
            current_path += f"/{part}"
            try:
                sftp.chdir(current_path)
            except IOError:
                sftp.mkdir(current_path)
                sftp.chdir(current_path)

    # Subir archivo comprimido
    sftp.put(archivo_comprimido, archivo_remoto)
    print(f"✅ Archivo cargado correctamente en: {archivo_remoto}")

    # Limpiar recursos
    sftp.close()
    ssh.close()
    shutil.rmtree(temp_dir)  # Borrar carpeta temporal
    '''