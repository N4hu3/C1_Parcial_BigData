import os
import datetime
import boto3
import requests

from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuración de AWS
s3 = boto3.client('s3')


def a(event, context):
    base_url = "https://casas.mitula.com.co/casas/villavicencio"
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


def b(event, context):
    # Detalles de configuración
    bucket_raw = "bucket-raw25"
    bucket_final = "bucket-final"
    folder_name = "casas"

    # Extraer la fecha actual
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Generar la ruta para el archivo CSV
    csv_key = f"casas/year={current_date[:4]}/month={current_date[5:7]}/day={current_date[8:]}/{current_date}.csv"

    # Recorrer los archivos HTML en el bucket raw
    for record in event['Records']:
        # Obtener el nombre del archivo HTML
        s3_key = record['s3']['object']['key']

        # Descargar el archivo HTML desde S3
        response = s3.get_object(Bucket=bucket_raw, Key=s3_key)
        html_content = response['Body'].read()

        # Parsear el HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extraer los datos requeridos (precio, metraje, número de habitaciones, características adicionales)
        # Supongamos que se extraen y se almacenan en las variables price, area, bedrooms y features

        # Escribir los datos en el archivo CSV
        csv_data = [
            ['Precio', 'Metraje', 'Habitaciones', 'Características adicionales'],
            [price, area, bedrooms, features]
        ]

        # Guardar el archivo CSV en S3
        csv_content = '\n'.join([','.join(row) for row in csv_data])
        s3.put_object(Bucket=bucket_final, Key=csv_key, Body=csv_content)

    return {
        'statusCode': 200,
        'body': 'Datos procesados y guardados en CSV correctamente.'
    }