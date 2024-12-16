import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import os

# URL base para scrapear las plataformas disponibles
BASE_URL = 'https://myrient.erista.me/files/Redump/'

# Carpeta de destino para las descargas
download_folder = r"C:\\Users\\mpzfm\\Downloads\\PS3"

def obtener_enlaces(url):
    """Obtiene los enlaces de descarga y los tamaños de los archivos desde la página web."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        download_links = []

        for row in rows:
            # Busca los enlaces y el tamaño en cada fila
            link = row.find('a')
            size = row.find('td', class_='size')

            if link and size:
                href = link.get('href')
                if href and ('.zip' in href or '.iso' in href):
                    file_size = size.text.strip()
                    download_links.append((href, file_size))
        print(download_links)
        return download_links
    else:
        print('Error al acceder a la página')
        return []

def listar_directorios(url_base):
    """Obtiene y lista los directorios disponibles para escrapear desde la página base."""
    response = requests.get(url_base)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        directories = []

        for row in rows:
            link = row.find('a')
            if link:
                href = link.get('href')
                if href and href.endswith('/'):
                    directories.append(href)
        return directories
    else:
        print('Error al acceder a la página base')
        return []

def filtrar_resultados(download_links):
    """Pregunta al usuario cómo desea filtrar los resultados y los filtra."""
    print("\n¿Cómo deseas ver los resultados?")
    print("1. Ver todos los resultados")
    print("2. Filtrar por 'Europe'")
    print("3. Filtrar por 'Spain'")
    print("4. Filtrar por 'Europe' y 'Spain'")

    opcion = input("Selecciona una opción (1-4): ")

    if opcion == '1':
        return download_links
    elif opcion == '2':
        return [link for link in download_links if 'Europe' in unquote(link[0])]
    elif opcion == '3':
        return [link for link in download_links if 'Spain' in unquote(link[0])]
    elif opcion == '4':
        return [link for link in download_links if 'Europe' in unquote(link[0]) or 'Spain' in unquote(link[0])]
    else:
        print("Opción no válida. Mostrando todos los resultados por defecto.")
        return download_links

def convertir_a_bytes(size_str):
    """Convierte una cadena de tamaño (como '6.4 GiB') a bytes."""
    size_str = size_str.lower()
    size = float(size_str.split()[0])  # El número
    unit = size_str.split()[1]  # La unidad (GiB, MiB, etc.)

    if unit == 'gib':
        return int(size * 1024**3)
    elif unit == 'mib':
        return int(size * 1024**2)
    elif unit == 'kib':
        return int(size * 1024)
    elif unit == 'bytes':
        return int(size)
    else:
        return 0  # Si no se puede convertir, retornamos 0

def listar_juegos(download_links):
    """Lista los juegos disponibles en la página web, incluyendo el tamaño de cada archivo."""
    if download_links:
        print(f"Se encontraron {len(download_links)} juegos:")
        for index, (link, size) in enumerate(download_links, start=1):
            print(f"{index}. {unquote(link)} - Tamaño: {size}")
    else:
        print("No se encontraron juegos para listar.")

def calcular_tamano_total(download_links):
    """Calcula el tamaño total de los juegos en bytes."""
    total_size = 0
    for _, size in download_links:
        total_size += convertir_a_bytes(size)
    return total_size

def descargar_juegos(download_links, selected_url):
    """Permite descargar los juegos filtrados."""
    print("\n¿Deseas descargar los juegos listados?")
    opcion = input("Escribe 'si' para proceder o cualquier otra tecla para cancelar: ").lower()

    if opcion == 'si':
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for link, size in download_links:
            file_url = selected_url + link  # Usar selected_url como base para los enlaces
            file_name = unquote(link).split('/')[-1]
            file_path = os.path.join(download_folder, file_name)

            print(f"Descargando {file_name} (Tamaño: {size})...")
            try:
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    print(f"{file_name} descargado correctamente en {download_folder}.")
                else:
                    print(f"Error al descargar {file_name}. Estado HTTP: {response.status_code}")
            except Exception as e:
                print(f"Error al descargar {file_name}: {e}")
    else:
        print("Descarga cancelada.")

def menu_principal():
    """Muestra el menú principal al usuario."""
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Seleccionar plataforma para scrapear")
        print("2. Salir")

        opcion = input("Selecciona una opción (1-2): ")

        if opcion == '1':
            print("\nListando plataformas disponibles...\n")
            directorios = listar_directorios(BASE_URL)
            if directorios:
                print("Plataformas disponibles:")
                for i, dir in enumerate(directorios, start=1):
                    # Decodifica el nombre del directorio para que sea legible (con espacios y caracteres especiales)
                    dir_name = unquote(dir)
                    print(f"{i}. {dir_name}")
                seleccion = int(input(f"\nSelecciona la plataforma (1-{len(directorios)}): "))
                if 1 <= seleccion <= len(directorios):
                    selected_url = BASE_URL + directorios[seleccion - 1]
                    print(f"\nSeleccionaste la plataforma: {unquote(directorios[seleccion - 1])}")
                    download_links = obtener_enlaces(selected_url)
                    resultados_filtrados = filtrar_resultados(download_links)
                    listar_juegos(resultados_filtrados)

                    # Calcular y mostrar el tamaño total antes de descargar
                    total_size = calcular_tamano_total(resultados_filtrados)
                    print(f"\nTamaño total de los juegos seleccionados: {total_size / (1024**3):.2f} GiB")

                    descargar_juegos(resultados_filtrados, selected_url)
                else:
                    print("Selección no válida. Volviendo al menú principal.")
            else:
                print("No se encontraron plataformas disponibles.")
        elif opcion == '2':
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta nuevamente.")

if __name__ == "__main__":
    menu_principal()
