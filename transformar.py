import boto3
import json
import os
import glob

# 1. Configuración de Bedrock
# Usamos el ID de la versión 2 (20241022-v2:0) que es la activa y no "Legacy"
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def ejecutar_modernizacion():
    # Buscamos la ruta donde AWS descargó el código Cobol (Origen Primario)
    ruta_cobol = os.environ.get('CODEBUILD_SRC_DIR')
    
    if not ruta_cobol:
        print("❌ Error: No se pudo determinar la ruta del código fuente.")
        return

    # Buscamos cualquier archivo .cbl o .cob en esa carpeta
    archivos_encontrados = glob.glob(f"{ruta_cobol}/*.cbl") + glob.glob(f"{ruta_cobol}/*.cob")
    
    if not archivos_encontrados:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_cobol}")
        return

    for archivo_path in archivos_encontrados:
        nombre_base = os.path.basename(archivo_path)
        print(f"🚀 Procesando: {nombre_base}...")

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo_cobol = f.read()
        except Exception as e:
            print(f"❌ Error al leer el archivo {nombre_base}: {str(e)}")
            continue

        # El Prompt maestro para Bedrock
        prompt_texto = f"""
        Eres un arquitecto experto en modernización de Mainframe a AWS.
        Analiza el siguiente código COBOL y genera:
        1. Código Java 21 moderno usando Spring Boot.
        2. Reglas de negocio detalladas extraídas de la lógica.
        3. Un diagrama de flujo en formato Mermaid.js.
        4. Pruebas unitarias con JUnit y un archivo .feature de Cucumber.
        
        IMPORTANTE: Devuelve todo en un único formato Markdown claro y bien estructurado.

        Código COBOL a transformar:
        {codigo_cobol}
        """

        # Estructura de "body" compatible con Claude 3.5 Sonnet v2
        # El contenido DEBE ser una lista con el tipo 'text'
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_texto
                        }
                    ]
                }
            ]
        })

        # ID del modelo estable para Claude 3.5 Sonnet v2
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

        try:
            print(f"📡 Enviando petición a Amazon Bedrock ({model_id})...")
            response = bedrock.invoke_model(
                body=body, 
                modelId=model_id
            )
            
            # Procesar la respuesta de AWS
            response_body = json.loads(response.get('body').read())
            
            # En Claude 3.5, el texto viene dentro de content[0]['text']
            texto_final = response_body['content'][0]['text']

            # Guardamos el resultado en la misma carpeta del proyecto Cobol
            ruta_salida = os.path.join(ruta_cobol, f"resultado_{nombre_base}.md")
            with open(ruta_salida, "w", encoding='utf-8') as f_out:
                f_out.write(texto_final)
            
            print(f"✅ Transformación exitosa guardada en: resultado_{nombre_base}.md")

        except Exception as e:
            print(f"❌ Error al procesar con la IA para {nombre_base}: {str(e)}")

if __name__ == "__main__":
    print("--- Iniciando Script de Modernización Centralizado ---")
    ejecutar_modernizacion()
    print("--- Proceso Finalizado ---")
