import re
import time
import json
import subprocess
from datetime import datetime
import os
from app.core.config import settings
from app.services.prompt_builder import build_prompt

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SAVE_LOGS = os.getenv("SAVE_LOGS", "False").lower() == "true"


OLLAMA_MODEL = settings.OLLAMA_MODEL

ordem_niveis = {
    "ensino médio": 1, "técnico": 2, "tecnólogo": 4, "especialização": 3, "graduação": 5,
    "bacharel": 6,"pós-graduação": 7, "MBA": 8, "mestrado": 9, "doutorado": 10, "certificacao": 0
}

VALID_NIVEIS_IDIOMA = {"básico", "intermediário", "avançado", "fluente", "nativo"}

def remove_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def corrigir_espacamento_letras(texto):
    def corrigir_linha(linha):
        return re.sub(r'((?:[A-Za-zÀ-ÿ]\s){3,}[A-Za-zÀ-ÿ])', lambda m: m.group(0).replace(' ', ''), linha)
    
    return '\n'.join(corrigir_linha(l) for l in texto.splitlines())


def split_chunks(text, size=CHUNK_SIZE):
    chunks = [text[i:i+size] for i in range(0, len(text), size)]
    if DEBUG:
        print(f"🔹 Total de chunks gerados: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"  - Chunk {i+1} tamanho: {len(chunk)} caracteres")
    return chunks


MAX_RETRIES = 10


def salvar_logs(nome_base, conteudo):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/{nome_base}_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(conteudo)

def remove_duplicates(lista, keys):
    seen = set()
    uniques = []
    for item in lista:
        key = tuple(str(item.get(k, "")).strip().lower() for k in keys)
        if key not in seen:
            seen.add(key)
            uniques.append(item)
    return uniques


def extract_section(applicant_id, section_name, schema_snippet, cv_text):
    cv_text = corrigir_espacamento_letras(cv_text)
    prompt_base = build_prompt(section_name, schema_snippet, cv_text)

    chunks = split_chunks(cv_text)
    seen_chunks = set()
    combined_data = []

    for i, chunk in enumerate(chunks):
        chunk_key = hash(chunk)
        if chunk_key in seen_chunks:
            continue
        seen_chunks.add(chunk_key)

        print(f"🧩 Processando chunk {i+1}/{len(chunks)} com {len(chunk)} caracteres")
        prompt = f"{prompt_base}\n\nCurrículo (parte {i+1}/{len(chunks)}):\n{chunk}"

        if DEBUG:
            print(f"📤 Prompt enviado ao modelo:\n{prompt}")
            if SAVE_LOGS:
                salvar_logs(f"prompt_chunk{i+1}", prompt)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                prompt_atual = prompt
                output = subprocess.check_output(
                    ["ollama", "run", OLLAMA_MODEL, "--think=false"],
                    input=prompt_atual.encode("utf-8"),
                    stderr=subprocess.STDOUT,
                    timeout=300
                ).decode("utf-8")

                if DEBUG:
                    print(f"📥 Resposta do modelo:\n{output}")
                    if SAVE_LOGS:
                        salvar_logs(f"resposta_chunk{i+1}", output)

                if "{" not in output or "}" not in output:
                    raise ValueError("❌ A resposta não contém JSON.")

                raw_json = remove_ansi(output[output.find('{'):output.rfind('}') + 1]).strip()

                try:
                    parsed = json.loads(raw_json)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Tentando ajuste adaptativo devido a erro de parsing: {e}")
                    prompt_reparo = (
                        f"{prompt_base}\n\n"
                        f"Currículo (parte {i+1}/{len(chunks)}):\n{chunk}\n\n"
                        f"⚠️ A resposta anterior gerou o erro:\n{str(e)}\n"
                        f"Por favor, corrija e retorne um JSON válido com a chave '{section_name}'."
                    )

                    if SAVE_LOGS:
                        os.makedirs("logs", exist_ok=True)
                        clean_output = remove_ansi(output)
                        log_data = (
                            f"applicant_id={applicant_id} | Erro de parsing: {str(e)}\n"
                            f"Resposta que falhou:\n{clean_output}\n\n"
                        )
                        log_filename = os.path.join("logs", f"reparo_prompt_{datetime.now().date()}.log")
                        with open(log_filename, "a", encoding="utf-8") as f:
                            f.write(log_data)
                        output = subprocess.check_output(
                            ["ollama", "run", OLLAMA_MODEL, "--think=false"],
                            input=prompt_reparo.encode("utf-8"),
                            stderr=subprocess.STDOUT,
                            timeout=120
                        ).decode("utf-8")

                    raw_json = remove_ansi(output[output.find('{'):output.rfind('}') + 1]).strip()
                    parsed = json.loads(raw_json)

                if isinstance(parsed, list):
                    parsed = {section_name: parsed}

                # --- AJUSTE DE CAMPOS PARA EXPERIENCIAS ---
                if section_name == "experiencias":
                    experiencias = parsed.get("experiencias", [])
                    for exp in experiencias:
                        # Corrige nomes de campos para o schema padronizado
                        # Aceita variações: data_fim, data fim, data_inicio, data inicio
                        if "data_fim" in exp:
                            exp["fim"] = exp.pop("data_fim")
                        if "data fim" in exp:
                            exp["fim"] = exp.pop("data fim")
                        if "data_inicio" in exp:
                            exp["inicio"] = exp.pop("data_inicio")
                        if "data inicio" in exp:
                            exp["inicio"] = exp.pop("data inicio")

                combined_data.extend(parsed.get(section_name, []))
                break  # Sucesso

            except Exception as e:
                print(f"⚠️ Erro ao extrair '{section_name}' do chunk {i+1} (tentativa {attempt}): {e}")
                if attempt == MAX_RETRIES and SAVE_LOGS:
                    salvar_logs(f"erro_chunk{i+1}", output)

    if section_name == "formacoes":
        combined_data = remove_duplicates(combined_data, ["curso", "instituicao", "ano_inicio", "ano_fim"])
    elif section_name == "experiencias":
        combined_data = remove_duplicates(combined_data, ["empresa", "cargo", "inicio", "fim"])
    elif section_name == "idiomas":
        combined_data = remove_duplicates(combined_data, ["idioma", "nivel"])
    elif section_name == "habilidades":
        combined_data = list(set(item.strip() for item in combined_data if isinstance(item, str)))

    return {section_name: combined_data}

def merge_results(formations, experiences, skills, languages):
    return {
        "formacoes": formations.get("formacoes", []),
        "experiencias": experiences.get("experiencias", []),
        "habilidades": skills.get("habilidades", []),
        "idiomas": languages.get("idiomas", [])
    }

def language_was_mentioned(cv_text, language):
    if not language:
        return False
    return re.search(rf"\b{re.escape(str(language))}\b", cv_text, re.IGNORECASE)

# Função para processar um único candidato (usada na API)
def process_single_applicant(applicant_dict):
    import time
    from app.models.processed_applicant import ProcessedApplicant
    from app.core.database import SessionLocal
    start_time = time.time()
    applicant_id = applicant_dict["id"]
    cv_text = applicant_dict["cv_pt"]
    if not cv_text or len(cv_text.strip()) < 30:
        print(f"⚠️ Empty or too short CV for applicant {applicant_id}.")
        return
    schema_form = json.dumps({"formacoes": [{"curso": "", "nivel": "", "instituicao": "", "ano_inicio": "", "ano_fim": "", "observacoes": None}]}, ensure_ascii=False)
    schema_exp  = json.dumps({"experiencias": [{"empresa": "", "cargo": "", "inicio": "", "fim": "", "descricao": ""}]}, ensure_ascii=False)
    schema_hab  = json.dumps({"habilidades": []}, ensure_ascii=False)
    schema_idi  = json.dumps({"idiomas": [{"idioma": "", "nivel": ""}]}, ensure_ascii=False)
    formations = extract_section(applicant_id, "formacoes", schema_form, cv_text)
    experiences  = extract_section(applicant_id, "experiencias", schema_exp, cv_text)
    skills  = extract_section(applicant_id, "habilidades", schema_hab, cv_text)
    languages  = extract_section(applicant_id, "idiomas", schema_idi, cv_text)
    if not formations or not experiences or not skills or not languages:
        print(f"⚠️ Incomplete extraction for applicant {applicant_id}, skipping insertion.")
        return
    for language in languages.get("idiomas", []):
        if not isinstance(language, dict):
            continue
        level = (language.get("nivel") or "").strip().lower()
        language["nivel"] = level if level in VALID_NIVEIS_IDIOMA else ""
    languages["idiomas"] = [
        language for language in languages.get("idiomas", [])
        if isinstance(language, dict) and language_was_mentioned(cv_text, language.get("idioma", ""))
    ]
    for f in formations.get("formacoes", []):
        if "observacoes" not in f:
            f["observacoes"] = None
        if isinstance(f.get("ano_fim"), str) and "incompleto" in f["ano_fim"].lower():
            f["ano_fim"] = None
            f["observacoes"] = "incompleto"
    final_json = merge_results(formations, experiences, skills, languages)
    max_education_level = None
    levels = [
        (f.get("nivel") or "").strip().lower()
        for f in final_json.get("formacoes", [])
        if (
            (f.get("nivel") or "").strip().lower() in ordem_niveis and
            not ((f.get("observacoes") or "").strip().lower() in {"trancado", "em andamento", "interrompida"})
        )
    ]
    if levels:
        max_education_level = max(levels, key=lambda x: ordem_niveis[x])
    print("📦 Final JSON to be inserted in the database:")
    print(json.dumps(final_json, indent=2, ensure_ascii=False))
    return final_json, max_education_level
