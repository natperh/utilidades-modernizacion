import boto3
import json
import os
import glob

# 1. Configuración de Bedrock con Cohere
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def ejecutar_modernizacion():
    ruta_cobol = os.environ.get('CODEBUILD_SRC_DIR')
    
    if not ruta_cobol:
        print("❌ Error: No se pudo determinar la ruta del código fuente.")
        return

    archivos_encontrados = glob.glob(f"{ruta_cobol}/*.cbl") + glob.glob(f"{ruta_cobol}/*.cob")
    
    if not archivos_encontrados:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_cobol}")
        return

    for archivo_path in archivos_encontrados:
        nombre_base = os.path.basename(archivo_path)
        print(f"🚀 Procesando con Cohere: {nombre_base}...")

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo_cobol = f.read()
        except Exception as e:
            print(f"❌ Error al leer el archivo {nombre_base}: {str(e)}")
            continue

        prompt_texto = f"""Analiza este código COBOL y genera:
1. Código Java 21 con Spring Boot.
2. Reglas de negocio detalladas.
3. Diagrama de flujo en Mermaid.js.
4. Pruebas unitarias JUnit y Cucumber.

Código COBOL:
{codigo_cobol}"""

        # Formato específico para Cohere Command R
        body = json.dumps({
            "message": prompt_texto,
            "max_tokens": 4096,
            "temperature": 0.3,
            "stream": False
        })

        # El ID que ya probaste en tu Lambda
        model_id = "cohere.command-r-v1:0"

        try:
            print(f"📡 Enviando petición a Cohere ({model_id})...")
            response = bedrock.invoke_model(
                body=body, 
                modelId=model_id
            )
            
            response_body = json.loads(response.get('body').read())
            
            # En Cohere, el texto viene en ['text']
            texto_final = response_body.get('text', 'No se generó respuesta.')

            ruta_salida = os.path.join(ruta_cobol, f"resultado_{nombre_base}.md")
            with open(ruta_salida, "w", encoding='utf-8') as f_out:
                f_out.write(texto_final)
            
            print(f"✅ ¡ÉXITO! Guardado en: resultado_{nombre_base}.md")

        except Exception as e:
            print(f"❌ Error con Cohere para {nombre_base}: {str(e)}")

if __name__ == "__main__":
    print("--- Iniciando Modernización con Cohere ---")
    ejecutar_modernizacion()
    print("--- Proceso Finalizado ---")
