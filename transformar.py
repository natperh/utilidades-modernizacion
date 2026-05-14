import boto3
import json
import os
import glob
import re
import traceback

# ============================================================
# CONFIGURACIÓN BEDROCK
# ============================================================

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# 🔥 INFERENCE PROFILE (NO MODEL DIRECTO)
MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-opus-4-1-20250805-v1:0"
)

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION
)

# ============================================================
# HELPERS
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
# INVOCACIÓN BEDROCK
# ============================================================

def invocar_claude(prompt_texto):

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8000,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt_texto
            }
        ]
    })

    print(f"MODEL_ID USADO: {MODEL_ID}")

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=body
        )

        response_body = json.loads(response["body"].read())

        return response_body["content"][0]["text"]

    except Exception as e:
        print("❌ CLIENT ERROR BEDROCK")
        print("TIPO:", type(e))
        print("ERROR:", str(e))
        print("\nTRACEBACK:")
        print(traceback.format_exc())
        raise


# ============================================================
# MODERNIZACIÓN COBOL
# ============================================================

def ejecutar_modernizacion():

    ruta_fuente = os.path.join(os.getcwd(), "fuente_cobol")

    print(f"📂 Buscando COBOL en: {ruta_fuente}")

    archivos = (
        glob.glob(f"{ruta_fuente}/*.cbl") +
        glob.glob(f"{ruta_fuente}/*.cob")
    )

    if not archivos:
        print("⚠️ No se encontraron archivos COBOL.")
        return

    # estructura output
    main_java = "SumaProject/src/main/java/com/modernizacion"
    test_java = "SumaProject/src/test/java/com/modernizacion"
    features_dir = "SumaProject/src/test/resources/features"
    docs_dir = "SumaProject/docs"

    os.makedirs(main_java, exist_ok=True)
    os.makedirs(test_java, exist_ok=True)
    os.makedirs(features_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    for archivo_path in archivos:

        nombre_base = os.path.basename(archivo_path).split(".")[0]

        print("\n================================================")
        print(f"🚀 Procesando: {nombre_base}")
        print("================================================")

        try:
            with open(archivo_path, "r", encoding="utf-8", errors="ignore") as f:
                codigo_cobol = f.read()

            prompt_texto = f"""
Eres un Arquitecto Senior.

Moderniza COBOL a Java 21.

FORMATO OBLIGATORIO:

[JAVA_START]
[JAVA_END]

[JUNIT_START]
[JUNIT_END]

[CUCUMBER_START]
[CUCUMBER_END]

[MERMAID_START]
[MERMAID_END]

[DOCS_START]
[DOCS_END]

COBOL:
{codigo_cobol}
"""

            print("📡 Invocando Claude via Bedrock...")

            texto_ia = invocar_claude(prompt_texto)

            print("✅ Respuesta recibida")

            java_code = extraer_seccion(texto_ia, "[JAVA_START]", "[JAVA_END]")
            junit_code = extraer_seccion(texto_ia, "[JUNIT_START]", "[JUNIT_END]")
            cucumber_code = extraer_seccion(texto_ia, "[CUCUMBER_START]", "[CUCUMBER_END]")
            mermaid_code = extraer_seccion(texto_ia, "[MERMAID_START]", "[MERMAID_END]")
            docs_txt = extraer_seccion(texto_ia, "[DOCS_START]", "[DOCS_END]")

            if java_code:
                guardar_archivo(
                    f"{main_java}/{nombre_base}.java",
                    limpiar_markdown(java_code)
                )

            if junit_code:
                guardar_archivo(
                    f"{test_java}/{nombre_base}Test.java",
                    limpiar_markdown(junit_code)
                )

            if cucumber_code:
                guardar_archivo(
                    f"{features_dir}/{nombre_base}.feature",
                    limpiar_markdown(cucumber_code)
                )

            if mermaid_code:
                guardar_archivo(
                    f"{docs_dir}/{nombre_base}.mmd",
                    limpiar_markdown(mermaid_code)
                )

            if docs_txt:
                guardar_archivo(
                    f"{docs_dir}/{nombre_base}.txt",
                    docs_txt
                )

            print(f"🎉 Completado: {nombre_base}")

        except Exception as e:
            print(f"❌ Error procesando {nombre_base}")
            print(str(e))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("================================================")
    print("🏗️ MODERNIZADOR COBOL → JAVA")
    print("⚡ Amazon Bedrock + Inference Profile")
    print("================================================")

    ejecutar_modernizacion()

    print("\n================================================")
    print("✅ FIN")
    print("================================================")
