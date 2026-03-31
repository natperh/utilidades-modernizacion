import boto3
import json
import os
import glob

# 1. Configuración de Bedrock
# Usamos Virginia (us-east-1) porque es donde suelen estar disponibles los modelos más nuevos
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def ejecutar_modernizacion():
    # Buscamos la ruta donde AWS descargó el código Cobol
    ruta_cobol = os.environ.get('CODEBUILD_SRC_DIR')
    
    # Buscamos cualquier archivo .cbl o .cob en esa carpeta
    archivos_encontrados = glob.glob(f"{ruta_cobol}/*.cbl") + glob.glob(f"{ruta_cobol}/*.cob")
    
    if not archivos_encontrados:
        print("No se encontraron archivos Cobol para procesar.")
        return

    for archivo_path in archivos_encontrados:
        nombre_base = os.path.basename(archivo_path)
        print(f"Procesando: {nombre_base}...")

        with open(archivo_path, 'r') as f:
            codigo_cobol = f.read()

        # El Prompt maestro para Bedrock
        prompt = f"""
        Eres un arquitecto experto en modernización de Mainframe a AWS.
        Analiza el siguiente código COBOL y genera:
        1. Código Java 21 funcional (usando Spring Boot si es necesario).
        2. Reglas de negocio extraídas del código.
        3. Diagrama de flujo en formato Mermaid.js.
        4. Pruebas unitarias con JUnit y un archivo .feature de Cucumber.
        
        IMPORTANTE: Devuelve todo en formato Markdown claro.

        Código COBOL a transformar:
        {codigo_cobol}
        """

        # Configuración para Claude 3.5 Sonnet
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        })

        try:
            response = bedrock.invoke_model(
                body=body, 
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"
            )
            
            resultado = json.loads(response.get('body').read())
            texto_final = resultado['content'][0]['text']

            # Guardamos el resultado de vuelta en la carpeta del proyecto
            ruta_salida = f"{ruta_cobol}/resultado_{nombre_base}.md"
            with open(ruta_salida, "w") as f_out:
                f_out.write(texto_final)
            
            print(f"✅ Transformación exitosa para {nombre_base}")

        except Exception as e:
            print(f"❌ Error al procesar {nombre_base}: {str(e)}")

if __name__ == "__main__":
    ejecutar_modernizacion()
