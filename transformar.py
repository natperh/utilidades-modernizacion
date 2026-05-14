import boto3
import json
import os
import glob
import re

# ============================================================
# CONFIGURACIÓN BEDROCK + CLAUDE
# ============================================================

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-sonnet-4-20250514-v1:0"
)

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION
)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def extraer_seccion(texto, inicio, fin):
    """
    Extrae contenido entre etiquetas.
    """

    try:
        patron = rf"{re.escape(inicio)}(.*?){re.escape(fin)}"

        resultado = re.search(
            patron,
            texto,
            re.DOTALL
        )

        return resultado.group(1).strip() if resultado else ""

    except Exception as e:
        print(f"❌ Error extrayendo sección {inicio}: {e}")
        return ""


def limpiar_markdown(texto):
    """
    Limpia bloques markdown residuales.
    """

    texto = re.sub(r"```[a-zA-Z]*\n?", "", texto)
    texto = texto.replace("```", "")

    return texto.strip()


def guardar_archivo(ruta, contenido):
    """
    Guarda archivo asegurando directorios.
    """

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

    response_body = json.loads(
        response.get("body").read()
    )

    return response_body["content"][0]["text"]


# ============================================================
# MODERNIZACIÓN COBOL
# ============================================================

def ejecutar_modernizacion():

    ruta_actual = os.getcwd()

    ruta_fuente = os.path.join(
        ruta_actual,
        "fuente_cobol"
    )

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
    # PROCESAMIENTO ARCHIVOS
    # ========================================================

    for archivo_path in archivos:

        nombre_base = os.path.basename(
            archivo_path
        ).split(".")[0]

        print("\n================================================")
        print(f"🚀 Procesando: {nombre_base}")
        print("================================================")

        try:

            with open(
                archivo_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                codigo_cobol = f.read()

            # =================================================
            # PROMPT CLAUDE
            # =================================================

            prompt_texto = f"""
Eres un Arquitecto de Software Senior experto en:

- COBOL Mainframe
- Java 21
- Spring Boot 3
- Clean Architecture
- Domain Driven Design
- BPM
- Modernización Legacy
- JUnit 5
- Cucumber
- Diseño Empresarial

OBJETIVO:
Modernizar este programa COBOL hacia Java 21 empresarial.

REGLAS OBLIGATORIAS:
- NO OMITAS NINGUNA SECCIÓN
- TODAS LAS ETIQUETAS SON OBLIGATORIAS
- NO USES TEXTO FUERA DE LAS ETIQUETAS
- NO USES MARKDOWN EXTERNO
- GENERA CÓDIGO COMPLETO
- GENERA CÓDIGO COMPILABLE
- GENERA CLEAN ARCHITECTURE
- GENERA BUENAS PRÁCTICAS
- GENERA NOMBRES EMPRESARIALES

FORMATO OBLIGATORIO:

[JAVA_START]
(Java Spring Boot 3 + Java 21)
[JAVA_END]

[JUNIT_START]
(Pruebas JUnit 5)
[JUNIT_END]

[CUCUMBER_START]
(Feature file Gherkin)
[CUCUMBER_END]

[MERMAID_START]
(Diagrama BPM Mermaid)
[MERMAID_END]

[DOCS_START]
(Documentación funcional y técnica)
[DOCS_END]

[POM_START]
(pom.xml Maven completo)
[POM_END]

COBOL DE ENTRADA:
{codigo_cobol}
"""

            # =================================================
            # LLAMADA CLAUDE
            # =================================================

            print(f"📡 Invocando Claude 3.5 Sonnet...")

            texto_ia = invocar_claude(prompt_texto)

            print("✅ Respuesta recibida desde Bedrock")

            # =================================================
            # EXTRAER SECCIONES
            # =================================================

            java_code = extraer_seccion(
                texto_ia,
                "[JAVA_START]",
                "[JAVA_END]"
            )

            junit_code = extraer_seccion(
                texto_ia,
                "[JUNIT_START]",
                "[JUNIT_END]"
            )

            cucumber_code = extraer_seccion(
                texto_ia,
                "[CUCUMBER_START]",
                "[CUCUMBER_END]"
            )

            mermaid_code = extraer_seccion(
                texto_ia,
                "[MERMAID_START]",
                "[MERMAID_END]"
            )

            docs_txt = extraer_seccion(
                texto_ia,
                "[DOCS_START]",
                "[DOCS_END]"
            )

            pom_xml = extraer_seccion(
                texto_ia,
                "[POM_START]",
                "[POM_END]"
            )

            # =================================================
            # GUARDAR ARCHIVOS
            # =================================================

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
                    f"{docs_dir}/{nombre_base}_diagrama.mmd",
                    limpiar_markdown(mermaid_code)
                )

            if docs_txt:

                guardar_archivo(
                    f"{docs_dir}/{nombre_base}_documentacion.txt",
                    docs_txt
                )

            if pom_xml:

                guardar_archivo(
                    "SumaProject/pom.xml",
                    limpiar_markdown(pom_xml)
                )

            print(f"🎉 Modernización completada: {nombre_base}")

        except Exception as e:

            print(f"❌ Error procesando {nombre_base}")
            print(str(e))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("================================================")
    print("🏗️ ARQUITECTO MODERNIZADOR COBOL → JAVA")
    print("⚡ Amazon Bedrock + Claude 3.5 Sonnet")
    print("================================================")

    ejecutar_modernizacion()

    print("\n================================================")
    print("✅ PROCESO FINALIZADO")
    print("================================================")
