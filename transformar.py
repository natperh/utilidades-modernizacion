import boto3
import json
import os
import glob

# 1. Configuración de Bedrock para Cohere (Región Virginia)
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def ejecutar_modernizacion():
    # Detectar la ruta donde CodeBuild descargó el código Cobol
    ruta_cobol = os.environ.get('CODEBUILD_SRC_DIR')
    
    if not ruta_cobol:
        print("❌ Error: No se pudo determinar la ruta del código fuente.")
        return

    # Buscar archivos .cbl o .cob
    archivos_encontrados = glob.glob(f"{ruta_cobol}/*.cbl") + glob.glob(f"{ruta_cobol}/*.cob")
    
    if not archivos_encontrados:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_cobol}")
        return

    for archivo_path in archivos_encontrados:
        nombre_base = os.path.basename(archivo_path)
        print(f"🚀 Procesando con Cohere Command R: {nombre_base}...")

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo_cobol = f.read()
        except Exception as e:
            print(f"❌ Error al leer el archivo {nombre_base}: {str(e)}")
            continue

        # Prompt estructurado para la modernización
        prompt_texto = f"""Actúa como un arquitecto de software experto. 
Transforma el siguiente código COBOL a Java 21 siguiendo estas instrucciones:
1. Genera código Java moderno con Spring Boot 3.
2. Extrae las reglas de negocio lógicas.
3. Crea un diagrama de flujo en formato Mermaid.js.
4. Genera pruebas unitarias con JUnit 5.

Código COBOL de entrada:
{codigo_cobol}
"""

        # Formato de Body ajustado para Cohere (Sin el campo 'stream' que causó error)
        body = json.dumps({
            "message": prompt_texto,
            "max_tokens": 4096,
            "temperature": 0.3
        })

        # ID del modelo que ya probaste con éxito en Lambda
        model_id = "cohere.command-r-v1:0"

        try:
            print(f"📡 Enviando petición a Bedrock ({model_id})...")
            response = bedrock.invoke_model(
                body=body, 
                modelId=model_id
            )
            
            # Leer y parsear la respuesta
            response_body = json.loads(response.get('body').read())
            
            # En Cohere, el texto generado viene directamente en la llave ['text']
            texto_final = response_body.get('text', 'No se recibió respuesta del modelo.')

            # Guardar el resultado en un archivo Markdown (.md)
            ruta_salida = os.path.join(ruta_cobol, f"resultado_{nombre_base}.md")
            with open(ruta_salida, "w", encoding='utf-8') as f_out:
                f_out.write(texto_final)
            
            print(f"✅ ¡Transformación Exitosa! Archivo creado: resultado_{nombre_base}.md")

        except Exception as e:
            print(f"❌ Error durante la invocación de la IA para {nombre_base}: {str(e)}")

if __name__ == "__main__":
    print("--- Iniciando Script de Modernización (Versión Cohere) ---")
    ejecutar_modernizacion()
    print("--- Proceso Finalizado ---")
