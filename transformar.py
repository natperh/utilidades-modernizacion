import boto3
import json
import os
import glob
import re

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def extraer_bloque(texto, lenguaje):
    """Extrae el contenido entre bloques de código Markdown ```lenguaje ... ```"""
    patron = rf"```{lenguaje}\s*(.*?)\s*```"
    resultado = re.search(patron, texto, re.DOTALL)
    return resultado.group(1) if resultado else ""

def ejecutar_modernizacion():
    # CAMBIO: Ahora buscamos en la carpeta que clonamos en el Buildspec
    ruta_trabajo = os.getcwd()
    ruta_fuente = os.path.join(ruta_trabajo, "fuente_cobol")
    
    archivos_encontrados = glob.glob(f"{ruta_fuente}/*.cbl") + glob.glob(f"{ruta_fuente}/*.cob")
    
    if not archivos_encontrados:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_fuente}")
        return

    for archivo_path in archivos_encontrados:
        nombre_base = os.path.basename(archivo_path).split('.')[0]
        print(f"🚀 Procesando: {nombre_base}...")

        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo_cobol = f.read()

        # Prompt mejorado para pedir formatos específicos que podamos separar
        prompt_texto = f"""Actúa como un arquitecto de software experto.
Transforma este COBOL a Java 21. 
ENTREGA TU RESPUESTA EXACTAMENTE EN ESTE ORDEN Y FORMATO:
1. Código Java (Spring Boot) dentro de un bloque ```java
2. Pruebas Unitarias dentro de un bloque ```junit
3. Diagrama Mermaid dentro de un bloque ```mermaid
4. Documentación explicativa en texto plano (sin bloques de código).

Código COBOL:
{codigo_cobol}
"""

        body = json.dumps({"message": prompt_texto, "max_tokens": 4096, "temperature": 0.3})
        
        try:
            response = bedrock.invoke_model(body=body, modelId="cohere.command-r-v1:0")
            texto_final = json.loads(response.get('body').read()).get('text', '')

            # --- PARTE NUEVA: REPARTIR ARCHIVOS ---
            # 1. Crear carpetas
            os.makedirs("SumaProject/src/main/java", exist_ok=True)
            os.makedirs("SumaProject/src/test/java", exist_ok=True)
            os.makedirs("SumaProject/docs", exist_ok=True)

            # 2. Extraer bloques
            java_code = extraer_bloque(texto_final, "java")
            junit_code = extraer_bloque(texto_final, "junit")
            mermaid_text = extraer_bloque(texto_final, "mermaid")
            
            # Limpiar el texto final para dejar solo la documentación
            doc_text = re.sub(r"```.*?```", "", texto_final, flags=re.DOTALL).strip()

            # 3. Guardar archivos individuales
            if java_code:
                with open(f"SumaProject/src/main/java/{nombre_base}.java", "w") as f:
                    f.write(java_code)
            
            if junit_code:
                with open(f"SumaProject/src/test/java/{nombre_base}Test.java", "w") as f:
                    f.write(junit_code)
            
            if doc_text:
                with open(f"SumaProject/docs/documentacion.txt", "w") as f:
                    f.write(doc_text)
            
            if mermaid_text:
                with open(f"SumaProject/docs/diagrama.mmd", "w") as f:
                    f.write(mermaid_text)

            print(f"✅ Proyecto {nombre_base} estructurado correctamente.")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    ejecutar_modernizacion()
