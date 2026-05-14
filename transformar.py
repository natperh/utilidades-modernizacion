import boto3
import json
import os
import glob
import re
import traceback
import botocore.exceptions

# ============================================================
# CONFIGURACIÓN BEDROCK + CLAUDE
# ============================================================

REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION
)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def extraer_seccion(texto, inicio, fin):
    try:
        patron = rf"{re.escape(inicio)}(.*?){re.escape(fin)}"
        resultado = re.search(patron, texto, re.DOTALL)
        return resultado.group(1).strip() if resultado else ""
    except Exception as e:
        print(f"❌ Error extrayendo sección {inicio}: {e}")
        return ""


def limpiar_markdown(texto):
    texto = re.sub(r"```[a-zA-Z]*\n?", "", texto)
    texto = texto.replace("```", "")
    return texto.strip()


def guardar_archivo(ruta, contenido):
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"✅ Archivo generado: {ruta}")
    except Exception as e:
        print(f"❌ Error guardando {ruta}: {e}")


# ============================================================
# INVOCACIÓN CLAUDE
# ============================================================

def invocar_claude(prompt_texto):

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt_texto
            }
        ]
    })

    response = bedrock.invoke_model(
        body=body,
        modelId=MODEL_ID
    )
    print("MODEL_ID REAL:", MODEL_ID)

    response_body = json.loads(response["body"].read())

    return response_body["content"][0]["text"]


# ============================================================
# MODERNIZACIÓN COBOL
# ============================================================

def ejecutar_modernizacion():

    ruta_fuente = os.path.join(os.getcwd(), "fuente_cobol")

    print(f"📂 Buscando COBOL en: {ruta_fuente}")

    archivos = (
        glob.glob(f"{ruta_fuente}/*.cbl") +
        glob.glob(f"{ruta_fuente}/*.cob") +
        glob.glob(f"{ruta_fuente}/*.cpy")
    )

    if not archivos:
        print("⚠️ No se encontraron archivos COBOL.")
        return

    # ========================================================
    # ESTRUCTURA MAVEN
    # ========================================================

    main_java = "SumaProject/src/main/java/com/modernizacion"
    test_java = "SumaProject/src/test/java/com/modernizacion"
    features_dir = "SumaProject/src/test/resources/features"
    docs_dir = "SumaProject/docs"

    os.makedirs(main_java, exist_ok=True)
    os.makedirs(test_java, exist_ok=True)
    os.makedirs(features_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    # ========================================================
    # PROCESAMIENTO
    # ========================================================

    for archivo_path in archivos:

        nombre_base = os.path.basename(archivo_path).split(".")[0]

        print("\n================================================")
        print(f"🚀 Procesando: {nombre_base}")
        print("================================================")

        try:

            with open(archivo_path, "r", encoding="utf-8", errors="ignore") as f:
                codigo_cobol = f.read()

            # =================================================
            # PROMPT
            # =================================================

            prompt_texto = f"""
Eres un Arquitecto de Software Senior.

Convierte COBOL a Java 21 con Clean Architecture.

OBLIGATORIO:
[JAVA_START]...[JAVA_END]
[JUNIT_START]...[JUNIT_END]
[CUCUMBER_START]...[CUCUMBER_END]
[MERMAID_START]...[MERMAID_END]
[DOCS_START]...[DOCS_END]
[POM_START]...[POM_END]

COBOL:
{codigo_cobol}
"""

            print("📡 Invocando Claude...")

            try:
                texto_ia = invocar_claude(prompt_texto)
                print("✅ Respuesta recibida desde Bedrock")

            except botocore.exceptions.ClientError as e:
                print("❌ CLIENT ERROR BEDROCK")

                print("CODE:", e.response["Error"]["Code"])
                print("MESSAGE:", e.response["Error"]["Message"])

                print(traceback.format_exc())
                raise e

            except Exception as e:
                print("❌ ERROR GENERAL INVOCANDO BEDROCK")
                print(traceback.format_exc())
                raise e

            # =================================================
            # EXTRAER SECCIONES
            # =================================================

            java_code = extraer_seccion(texto_ia, "[JAVA_START]", "[JAVA_END]")
            junit_code = extraer_seccion(texto_ia, "[JUNIT_START]", "[JUNIT_END]")
            cucumber_code = extraer_seccion(texto_ia, "[CUCUMBER_START]", "[CUCUMBER_END]")
            mermaid_code = extraer_seccion(texto_ia, "[MERMAID_START]", "[MERMAID_END]")
            docs_txt = extraer_seccion(texto_ia, "[DOCS_START]", "[DOCS_END]")
            pom_xml = extraer_seccion(texto_ia, "[POM_START]", "[POM_END]")

            # =================================================
            # GUARDAR
            # =================================================

            if java_code:
                guardar_archivo(f"{main_java}/{nombre_base}.java", limpiar_markdown(java_code))

            if junit_code:
                guardar_archivo(f"{test_java}/{nombre_base}Test.java", limpiar_markdown(junit_code))

            if cucumber_code:
                guardar_archivo(f"{features_dir}/{nombre_base}.feature", limpiar_markdown(cucumber_code))

            if mermaid_code:
                guardar_archivo(f"{docs_dir}/{nombre_base}.mmd", limpiar_markdown(mermaid_code))

            if docs_txt:
                guardar_archivo(f"{docs_dir}/{nombre_base}.txt", docs_txt)

            if pom_xml:
                guardar_archivo("SumaProject/pom.xml", limpiar_markdown(pom_xml))

            print(f"🎉 Modernización completada: {nombre_base}")

        except Exception as e:
            print(f"❌ Error procesando {nombre_base}")
            print(traceback.format_exc())


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("================================================")
    print("🏗️ ARQUITECTO MODERNIZADOR COBOL → JAVA")
    print("⚡ Amazon Bedrock + Claude")
    print("================================================")

    ejecutar_modernizacion()

    print("\n================================================")
    print("✅ PROCESO FINALIZADO")
    print("================================================")
