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

def list_objects(bucket_name, prefix):
    """Obtener una lista de todos los objetos en un prefijo dado."""
    objects = []
    paginator = s3.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in response_iterator:
        if 'Contents' in page:
            objects.extend(page['Contents'])
    return objects

def b(event, context):
    # Detalles de configuración
    bucket_raw = "bucket-raw25"
    bucket_final = "bucket-final25"
    folder_name = "casas"

    # Extraer la fecha actual
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Generar la ruta para el archivo CSV
    csv_key = f"casas/year={current_date[:4]}/month={current_date[5:7]}/day={current_date[8:]}/{current_date}.csv"

    # Lista para almacenar los datos de todos los archivos
    all_data = []

    # Obtener la lista de objetos en el prefijo 'casas'
    objects = list_objects(bucket_raw, folder_name)

    # Procesar cada archivo
    for obj in objects:
        # Obtener la clave del objeto
        key = obj['Key']

        # Descargar el archivo HTML desde S3
        response = s3.get_object(Bucket=bucket_raw, Key=key)
        html_content = response['Body'].read()

        # Parsear el HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontrar todos los contenedores de información principal
        information_containers = soup.find_all("div", class_="listing-card__information-main")

        # Iterar sobre cada contenedor
        for container in information_containers:
            # Extraer los datos necesarios del HTML dentro de este contenedor
            title = container.find("div", class_="listing-card__title").text.strip()
            price = container.find("div", class_="price").text.strip()
            location = container.find("div", class_="listing-card__location").text.strip()
            bedrooms_tag = container.find("span", {"data-test": "bedrooms"})
            bedrooms = bedrooms_tag.text.strip() if bedrooms_tag else "No disponible"
            bathrooms_tag = container.find("span", {"data-test": "bathrooms"})
            bathrooms = bathrooms_tag.text.strip() if bathrooms_tag else "No disponible"
            area_divs = container.find_all("div", class_="listing-card__property")
            area = area_divs[2].text.strip() if len(area_divs) > 2 else "No disponible"
            # Agregar los datos a la lista
            all_data.append([title, price, location, bedrooms, bathrooms, area])

    # Escribir los datos en el archivo CSV
    csv_data = [
        ['Título', 'Precio', 'Ubicación', 'Habitaciones', 'Baños', 'Área']
    ]
    csv_data.extend(all_data)

    # Guardar el archivo CSV en S3
    csv_content = '\n'.join([','.join(row) for row in csv_data])
    s3.put_object(Bucket=bucket_final, Key=csv_key, Body=csv_content)

    return {
        'statusCode': 200,
        'body': 'Datos procesados y guardados en CSV correctamente.'
    }
