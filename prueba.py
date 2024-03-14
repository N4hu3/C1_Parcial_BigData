from bs4 import BeautifulSoup

# Lee el contenido del archivo HTML
with open("contenido-pag-1-2024-03-14 (1).html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parsea el HTML
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

    # Imprimir los datos
    print("Título:", title)
    print("Precio:", price)
    print("Ubicación:", location)
    print("Habitaciones:", bedrooms)
    print("Baños:", bathrooms)
    print("Área:", area)
    print()