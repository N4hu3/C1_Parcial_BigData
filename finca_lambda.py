import os
import datetime
import boto3
import requests

from urllib.parse import urljoin

# Configuración de AWS
s3 = boto3.client('s3')


def a(event, context):
    base_url = "https://casas.mitula.com.co/"
    bucket_name = "bucket-raw25"
    folder_name = "casas"

    # Obtener la fecha actual
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Descargar las 5 primeras páginas
    for page_number in range(1, 6):
        page_url = urljoin(base_url, f"?page={page_number}")
        page_content = requests.get(page_url).content

        # Construir la clave para el archivo en S3
        file_name = f"contenido-pag-{page_number}-{current_date}.html"
        s3_key = os.path.join(folder_name, file_name)

        # Subir el archivo a S3
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=page_content)

    return {
        "statusCode": 200,
        "body": "Páginas descargadas y guardadas en S3 correctamente."
    }
