import boto3
import json
import os
import glob
import re

# 1. Configuración de Bedrock
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def extraer_seccion(texto, inicio, fin):
    """Extrae el contenido entre etiquetas personalizadas [INICIO] y [FIN]"""
    try:
        patron = rf"{re.escape(inicio)}(.*?){re.escape(fin)}"
        resultado = re.search(patron, texto, re.DOTALL)
        return resultado.group(1).strip() if resultado else ""
    except Exception as e:
        print(f"Error extrayendo sección {inicio}: {e}")
        return ""

def limpiar_markdown(texto):
    """Elimina marcas de bloques de código Markdown ```java, ```gherkin, etc."""
    return re.sub(r"```[a-z]*\n?", "", texto).replace("```", "").strip()

def ejecutar_modernizacion():
    # Definir rutas: Buscamos en 'fuente_cobol' que clonó el Buildspec
    ruta_actual = os.getcwd()
    ruta_fuente = os.path.join(ruta_actual, "fuente_cobol")
    
    # Buscar archivos COBOL
    archivos = glob.glob(f"{ruta_fuente}/*.cbl") + glob.glob(f"{ruta_fuente}/*.cob")
    
    if not archivos:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_fuente}")
        return

    for archivo_path in archivos:
        nombre_base = os.path.basename(archivo_path).split('.')[0]
        print(f"🚀 Procesando con IA: {nombre_base}...")

        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo_cobol = f.read()

        # PROMPT DE INGENIERÍA: Estricto, sin prosa, con Cucumber
        prompt_texto = f"""Eres un transpilador experto. Transforma COBOL a Java 21. 
No escribas introducciones ni explicaciones fuera de las etiquetas.

USA ESTE FORMATO EXACTO:

[JAVA_START]
(Código Java Spring Boot 3)
[JAVA_END]

[JUNIT_START]
(Pruebas unitarias JUnit 5)
[JUNIT_END]

[CUCUMBER_START]
(Archivo .feature en Gherkin/Cucumber)
[CUCUMBER_END]

[MERMAID_START]
(Código del diagrama Mermaid)
[MERMAID_END]

[DOCS_START]
(Documentación técnica en texto plano)
[DOCS_END]

Código COBOL de entrada:
{codigo_cobol}
"""

        body = json.dumps({
            "message": prompt_texto,
            "max_tokens": 4096,
            "temperature": 0.2
        })

        model_id = "cohere.command-r-v1:0"

        try:
            print(f"📡 Invocando Bedrock...")
            response = bedrock.invoke_model(body=body, modelId=model_id)
            response_body = json.loads(response.get('body').read())
            texto_ia = response_body.get('text', '')

            # --- ESTRUCTURACIÓN DE CARPETAS ---
            main_java = "SumaProject/src/main/java/com/modernizacion"
            test_java = "SumaProject/src/test/java/com/modernizacion"
            features_dir = "SumaProject/src/test/resources/features"
            docs_dir = "SumaProject/docs"

            for folder in [main_java, test_java, features_dir, docs_dir]:
                os.makedirs(folder, exist_ok=True)

            # --- EXTRACCIÓN Y GUARDADO ---
            
            # 1. Código Java
            java_code = extraer_seccion(texto_ia, "[JAVA_START]", "[JAVA_END]")
            if java_code:
                with open(f"{main_java}/{nombre_base}.java", "w") as f:
                    f.write(limpiar_markdown(java_code))

            # 2. JUnit Tests
            junit_code = extraer_seccion(texto_ia, "[JUNIT_START]", "[JUNIT_END]")
            if junit_code:
                with open(f"{test_java}/{nombre_base}Test.java", "w") as f:
                    f.write(limpiar_markdown(junit_code))

            # 3. Cucumber (.feature)
            cucumber_code = extraer_seccion(texto_ia, "[CUCUMBER_START]", "[CUCUMBER_END]")
            if cucumber_code:
                with open(f"{features_dir}/{nombre_base}.feature", "w") as f:
                    f.write(limpiar_markdown(cucumber_code))

            # 4. Mermaid (.mmd para luego convertir a PNG)
            mermaid_code = extraer_seccion(texto_ia, "[MERMAID_START]", "[MERMAID_END]")
            if mermaid_code:
                with open(f"{docs_dir}/diagrama.mmd", "w") as f:
                    f.write(limpiar_markdown(mermaid_code))

            # 5. Documentación (.txt)
            docs_txt = extraer_seccion(texto_ia, "[DOCS_START]", "[DOCS_END]")
            if docs_txt:
                with open(f"{docs_dir}/documentacion.txt", "w") as f:
                    f.write(docs_txt)

            print(f"✅ ¡Proyecto {nombre_base} creado en SumaProject/!")

        except Exception as e:
            print(f"❌ Error procesando {nombre_base}: {str(e)}")

if __name__ == "__main__":
    print("--- Arquitecto de Modernización v2.0 ---")
    ejecutar_modernizacion()
    print("--- Proceso Finalizado ---")
