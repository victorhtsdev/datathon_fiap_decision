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

education_level_order = {
    "ensino médio": 1, "técnico": 2, "tecnólogo": 4, "especialização": 3, "graduação": 5,
    "bacharel": 6,"pós-graduação": 7, "MBA": 8, "mestrado": 9, "doutorado": 10, "certificacao": 0
}

VALID_LANGUAGE_LEVELS = {"básico", "intermediário", "avançado", "fluente", "nativo"}

def remove_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def fix_letter_spacing(text):
    def fix_line(line):
        return re.sub(r'((?:[A-Za-zÀ-ÿ]\s){3,}[A-Za-zÀ-ÿ])', lambda m: m.group(0).replace(' ', ''), line)
    return '\n'.join(fix_line(l) for l in text.splitlines())


def split_chunks(text, size=CHUNK_SIZE):
    chunks = [text[i:i+size] for i in range(0, len(text), size)]
    if DEBUG:
        print(f"🔹 Total chunks generated: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"  - Chunk {i+1} size: {len(chunk)} characters")
    return chunks

MAX_RETRIES = 10

def save_logs(base_name, content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/{base_name}_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def remove_duplicates(lst, keys):
    seen = set()
    uniques = []
    for item in lst:
        key = tuple(str(item.get(k, "")).strip().lower() for k in keys)
        if key not in seen:
            seen.add(key)
            uniques.append(item)
    return uniques


def extract_section(applicant_id, section_name, schema_snippet, cv_text):
    cv_text = fix_letter_spacing(cv_text)
    prompt_base = build_prompt(section_name, schema_snippet, cv_text)

    chunks = split_chunks(cv_text)
    seen_chunks = set()
    combined_data = []

    for i, chunk in enumerate(chunks):
        chunk_key = hash(chunk)
        if chunk_key in seen_chunks:
            continue
        seen_chunks.add(chunk_key)

        print(f"🧩 Processing chunk {i+1}/{len(chunks)} with {len(chunk)} characters")
        prompt = f"{prompt_base}\n\nCurrículo (parte {i+1}/{len(chunks)}):\n{chunk}"

        if DEBUG:
            print(f"📤 Prompt sent to model:\n{prompt}")
            if SAVE_LOGS:
                save_logs(f"prompt_chunk{i+1}", prompt)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                prompt_current = prompt
                output = subprocess.check_output(
                    ["ollama", "run", OLLAMA_MODEL, "--think=false"],
                    input=prompt_current.encode("utf-8"),
                    stderr=subprocess.STDOUT,
                    timeout=300
                ).decode("utf-8")

                if DEBUG:
                    print(f"📥 Model response:\n{output}")
                    if SAVE_LOGS:
                        save_logs(f"resposta_chunk{i+1}", output)

                if "{" not in output or "}" not in output:
                    raise ValueError("❌ The response does not contain JSON.")

                raw_json = remove_ansi(output[output.find('{'):output.rfind('}') + 1]).strip()

                try:
                    parsed = json.loads(raw_json)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Trying adaptive fix due to parsing error: {e}")
                    prompt_fix = (
                        f"{prompt_base}\n\n"
                        f"Currículo (parte {i+1}/{len(chunks)}):\n{chunk}\n\n"
                        f"⚠️ The previous response generated the error:\n{str(e)}\n"
                        f"Please correct and return a valid JSON with the key '{section_name}'."
                    )

                    if SAVE_LOGS:
                        os.makedirs("logs", exist_ok=True)
                        clean_output = remove_ansi(output)
                        log_data = (
                            f"applicant_id={applicant_id} | Parsing error: {str(e)}\n"
                            f"Failed response:\n{clean_output}\n\n"
                        )
                        log_filename = os.path.join("logs", f"fix_prompt_{datetime.now().date()}.log")
                        with open(log_filename, "a", encoding="utf-8") as f:
                            f.write(log_data)
                        output = subprocess.check_output(
                            ["ollama", "run", OLLAMA_MODEL, "--think=false"],
                            input=prompt_fix.encode("utf-8"),
                            stderr=subprocess.STDOUT,
                            timeout=120
                        ).decode("utf-8")

                    raw_json = remove_ansi(output[output.find('{'):output.rfind('}') + 1]).strip()
                    parsed = json.loads(raw_json)

                if isinstance(parsed, list):
                    parsed = {section_name: parsed}

                # --- FIELD ADJUSTMENT FOR EXPERIENCES ---
                if section_name == "experiencias":
                    experiences = parsed.get("experiencias", [])
                    for exp in experiences:
                        # Fix field names for the standardized schema
                        # Accepts variations: data_fim, data fim, data_inicio, data inicio
                        if "data_fim" in exp:
                            exp["fim"] = exp.pop("data_fim")
                        if "data fim" in exp:
                            exp["fim"] = exp.pop("data fim")
                        if "data_inicio" in exp:
                            exp["inicio"] = exp.pop("data_inicio")
                        if "data inicio" in exp:
                            exp["inicio"] = exp.pop("data inicio")

                combined_data.extend(parsed.get(section_name, []))
                break  # Success

            except Exception as e:
                print(f"⚠️ Error extracting '{section_name}' from chunk {i+1} (attempt {attempt}): {e}")

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

# Function to process a single applicant (used in the API)
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
        language["nivel"] = level if level in VALID_LANGUAGE_LEVELS else ""
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
            (f.get("nivel") or "").strip().lower() in education_level_order and
            not ((f.get("observacoes") or "").strip().lower() in {"trancado", "em andamento", "interrompida"})
        )
    ]
    if levels:
        max_education_level = max(levels, key=lambda x: education_level_order[x])
    print("📦 Final JSON to be inserted in the database:")
    print(json.dumps(final_json, indent=2, ensure_ascii=False))
    return final_json, max_education_level