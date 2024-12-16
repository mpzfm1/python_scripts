import os

def borrar_claves_sin_iso(directorio):
    try:
        # Obtén la lista de archivos en el directorio
        archivos = os.listdir(directorio)
        
        # Filtra los archivos por extensión
        isos = {os.path.splitext(archivo)[0] for archivo in archivos if archivo.endswith('.iso')}
        keys = [archivo for archivo in archivos if archivo.endswith('.key')]

        # Compara y elimina las claves sin ISO correspondiente
        for key in keys:
            nombre_base = os.path.splitext(key)[0]
            if nombre_base not in isos:
                ruta_key = os.path.join(directorio, key)
                os.remove(ruta_key)
                print(f'Eliminado: {key}')
        
        print("Proceso completado.")
    except Exception as e:
        print(f"Se produjo un error: {e}")

# Especifica el directorio donde se encuentran los archivos
directorio_ejemplo = r"D:\PS3ISO"
borrar_claves_sin_iso(directorio_ejemplo)
