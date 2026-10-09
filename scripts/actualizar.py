import urllib.request
import xml.etree.ElementTree as ET
import json
import os

# Fuentes públicas de rugby totalmente gratuitas
FEEDS_RUGBY = [
    "https://www.cordobaxv.com.ar/feed/",
    "https://www.aplenarugby.com.ar/feed/"
]

def obtener_noticias():
    noticias = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for url in FEEDS_RUGBY:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item')[:5]:
                    titulo = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    if titulo and link:
                        noticias.append({
                            "titulo": titulo,
                            "link": link,
                            "fecha": pubDate
                        })
        except Exception as e:
            print(f"Error cargando fuente {url}: {e}")

    return noticias

if __name__ == "__main__":
    datos = obtener_noticias()
    
    # Crear la carpeta data si no existe y guardar las noticias en el JSON
    os.makedirs("data", exist_ok=True)
    with open("data/noticias.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print(f"Proceso completado: se guardaron {len(datos)} noticias correctamente.")
