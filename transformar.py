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
    """Elimina marcas de bloques de código Markdown residuales"""
    return re.sub(r"```[a-z]*\n?", "", texto).replace("```", "").strip()

def ejecutar_modernizacion():
    # Definir rutas: Buscamos en 'fuente_cobol' clonada por el Buildspec
    ruta_actual = os.getcwd()
    ruta_fuente = os.path.join(ruta_actual, "fuente_cobol")
    
    archivos = glob.glob(f"{ruta_fuente}/*.cbl") + glob.glob(f"{ruta_fuente}/*.cob")
    
    if not archivos:
        print(f"⚠️ No se encontraron archivos Cobol en {ruta_fuente}")
        return

    for archivo_path in archivos:
        nombre_base = os.path.basename(archivo_path).split('.')[0]
        print(f"🚀 Procesando archivo: {nombre_base}...")

        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo_cobol = f.read()

        # PROMPT ESTRUCTURADO: Foco en BPM y Reglas de Negocio COBOL
        prompt_texto = f"""Eres un Arquitecto de Software y Analista de Procesos Senior. 
Tu tarea es modernizar este COBOL a Java 21, pero la documentación y el diagrama deben ser de nivel negocio.

INSTRUCCIONES DE FORMATO (OBLIGATORIO):
No escribas prosa fuera de las etiquetas. Usa exactamente estos delimitadores:

[JAVA_START]
(Código Java Spring Boot 3 con Clean Architecture)
[JAVA_END]

[JUNIT_START]
(Pruebas unitarias JUnit 5 enfocadas en lógica de negocio)
[JUNIT_END]

[CUCUMBER_START]
(Archivo .feature con escenarios Gherkin que describan el comportamiento esperado)
[CUCUMBER_END]

[MERMAID_START]
graph TD
  subgraph "Business Process Model (BPM)"
    Start((Inicio)) --> Input[Lectura de Datos COBOL]
    Input --> Logic{{Validación de Reglas}}
    Logic -- Fallo --> Error((Fin con Error))
    Logic -- Éxito --> Calc[Procesamiento de Reglas de Negocio]
    Calc --> Output[Escritura/Salida de Resultados]
    Output --> End((Fin Proceso))
  end
  %% Continúa el flujo BPM basado en el código COBOL
[MERMAID_END]

[DOCS_START]
ANÁLISIS TÉCNICO-FUNCIONAL DEL PROGRAMA COBOL:
1. DESCRIPCIÓN GENERAL: (Qué hace el programa originalmente en el Mainframe)
2. REGLAS DE NEGOCIO: (Listado detallado y numerado de las validaciones y cálculos lógicos del COBOL)
3. VARIABLES CRÍTICAS: (Mapeo de las variables más importantes del COBOL y su función)
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
            print(f"📡 Invocando Bedrock para {nombre_base}...")
            response = bedrock.invoke_model(body=body, modelId=model_id)
            response_body = json.loads(response.get('body').read())
            texto_ia = response_body.get('text', '')

            # --- ESTRUCTURACIÓN DE CARPETAS (Estándar Maven) ---
            main_java = "SumaProject/src/main/java/com/modernizacion"
            test_java = "SumaProject/src/test/java/com/modernizacion"
            features_dir = "SumaProject/src/test/resources/features"
            docs_dir = "SumaProject/docs"

            for folder in [main_java, test_java, features_dir, docs_dir]:
                os.makedirs(folder, exist_ok=True)

            # --- EXTRACCIÓN Y GUARDADO DE COMPONENTES ---
            
            # 1. Código Fuente Java
            java_code = extraer_seccion(texto_ia, "[JAVA_START]", "[JAVA_END]")
            if java_code:
                with open(f"{main_java}/{nombre_base}.java", "w", encoding='utf-8') as f:
                    f.write(limpiar_markdown(java_code))

            # 2. Pruebas JUnit
            junit_code = extraer_seccion(texto_ia, "[JUNIT_START]", "[JUNIT_END]")
            if junit_code:
                with open(f"{test_java}/{nombre_base}Test.java", "w", encoding='utf-8') as f:
                    f.write(limpiar_markdown(junit_code))

            # 3. Escenarios Cucumber (Gherkin)
            cucumber_code = extraer_seccion(texto_ia, "[CUCUMBER_START]", "[CUCUMBER_END]")
            if cucumber_code:
                with open(f"{features_dir}/{nombre_base}.feature", "w", encoding='utf-8') as f:
                    f.write(limpiar_markdown(cucumber_code))

            # 4. Diagrama BPM (Mermaid)
            mermaid_code = extraer_seccion(texto_ia, "[MERMAID_START]", "[MERMAID_END]")
            if mermaid_code:
                with open(f"{docs_dir}/diagrama.mmd", "w", encoding='utf-8') as f:
                    f.write(limpiar_markdown(mermaid_code))

            # 5. Documentación de Reglas de Negocio
            docs_txt = extraer_seccion(texto_ia, "[DOCS_START]", "[DOCS_END]")
            if docs_txt:
                with open(f"{docs_dir}/documentacion.txt", "w", encoding='utf-8') as f:
                    f.write(docs_txt)

            print(f"✅ Proyecto {nombre_base} finalizado exitosamente.")

        except Exception as e:
            print(f"❌ Error procesando {nombre_base}: {str(e)}")

if __name__ == "__main__":
    print("--- 🏗️ Iniciando Arquitecto de Modernización (BPM & Clean Code) ---")
    ejecutar_modernizacion()
    print("--- Proceso Finalizado ---")
