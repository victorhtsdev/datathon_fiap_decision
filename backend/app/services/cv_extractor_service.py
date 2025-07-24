import re
import time
import json
from datetime import datetime
import os

from app.core.config import settings
from app.services.prompt_builder import build_prompt
from app.llm.factory import get_llm_client

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SAVE_LOGS = os.getenv("SAVE_LOGS", "False").lower() == "true"

education_level_order = {
    "ensino médio": 1, "técnico": 2, "tecnólogo": 4, "especialização": 3, "graduação": 5,
    "bacharel": 6, "pós-graduação": 7, "MBA": 8, "mestrado": 9, "doutorado": 10, "certificacao": 0
}

VALID_LANGUAGE_LEVELS = {"básico", "intermediário", "avançado", "fluente", "nativo"}
MAX_RETRIES = 10


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
        print(f"🔹 Total chunks: {len(chunks)}")
    return chunks


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
    """
    Extrai do LLM (Ollama ou DeepSeek) a seção do CV, com retry e deduplicação.
    """
    cv_text = fix_letter_spacing(cv_text)
    prompt_base = build_prompt(section_name, schema_snippet, cv_text)
    chunks = split_chunks(cv_text)
    seen = set()
    result = []
    llm = get_llm_client()

    for idx, chunk in enumerate(chunks, start=1):
        key = hash(chunk)
        if key in seen: continue
        seen.add(key)
        print(f"🧩 Chunk {idx}/{len(chunks)} length={len(chunk)}")

        for attempt in range(1, MAX_RETRIES+1):
            try:
                # extrai via cliente genérico
                parsed = llm.extract_section(section_name, prompt_base)
                if isinstance(parsed, dict) and parsed.get("error"):
                    raise ValueError(parsed["error"])

                # ajusta lista
                if isinstance(parsed, list):
                    parsed = {section_name: parsed}

                # campo especial para 'experiencias'
                if section_name == "experiencias":
                    for exp in parsed.get("experiencias", []):
                        if "data_fim" in exp: exp["fim"] = exp.pop("data_fim")
                        if "data fim" in exp: exp["fim"] = exp.pop("data fim")
                        if "data_inicio" in exp: exp["inicio"] = exp.pop("data_inicio")
                        if "data inicio" in exp: exp["inicio"] = exp.pop("data inicio")

                result.extend(parsed.get(section_name, []))
                break

            except Exception as e:
                print(f"⚠️ Erro {section_name} chunk {idx} tentativa {attempt}: {e}")
                if attempt == MAX_RETRIES:
                    print(f"❌ Falha definitiva no chunk {idx}")

    # dedupe conforme seção
    if section_name == "formacoes":
        result = remove_duplicates(result, ["curso","instituicao","ano_inicio","ano_fim"])
    elif section_name == "experiencias":
        result = remove_duplicates(result, ["empresa","cargo","inicio","fim"])
    elif section_name == "idiomas":
        result = remove_duplicates(result, ["idioma","nivel"])
    elif section_name == "habilidades":
        result = list(set(item.strip() for item in result if isinstance(item,str)))

    return {section_name: result}


def merge_results(forms, exps, skills, langs):
    return {
        "formacoes": forms.get("formacoes", []),
        "experiencias": exps.get("experiencias", []),
        "habilidades": skills.get("habilidades", []),
        "idiomas": langs.get("idiomas", [])
    }


def language_was_mentioned(text, lang):
    return bool(lang) and re.search(rf"\b{re.escape(lang)}\b", text, re.IGNORECASE)


def process_single_applicant(app):
    from app.models.processed_applicant import ProcessedApplicant
    from app.core.database import SessionLocal
    start = time.time()
    cid = app.get("id")
    txt = app.get("cv_pt", "")
    if not txt or len(txt.strip())<30:
        print(f"⚠️ CV inválido {cid}"); return None

    schemas = {
      "formacoes": json.dumps({"formacoes":[{"curso":"","nivel":"","instituicao":"","ano_inicio":"","ano_fim":"","observacoes":None}]},ensure_ascii=False),
      "experiencias": json.dumps({"experiencias":[{"empresa":"","cargo":"","inicio":"","fim":"","descricao":""}]},ensure_ascii=False),
      "habilidades": json.dumps({"habilidades":[]},ensure_ascii=False),
      "idiomas": json.dumps({"idiomas":[{"idioma":"","nivel":""}]},ensure_ascii=False)
    }

    forms = extract_section(cid,"formacoes",schemas["formacoes"],txt)
    exps = extract_section(cid,"experiencias",schemas["experiencias"],txt)
    sks  = extract_section(cid,"habilidades",schemas["habilidades"],txt)
    lgs  = extract_section(cid,"idiomas",schemas["idiomas"],txt)

    if not (forms and exps and sks and lgs): print(f"⚠️ Extração incompleta {cid}"); return None

    # valida idiomas
    valid_langs = []
    for l in lgs.get("idiomas",[]):
        lvl = (l.get("nivel") or "").strip().lower()
        if lvl in VALID_LANGUAGE_LEVELS and language_was_mentioned(txt,l.get("idioma","")):
            valid_langs.append({"idioma":l.get("idioma"),"nivel":lvl})
    lgs["idiomas"] = valid_langs

    # ajusta formacoes incompletas
    for f in forms.get("formacoes",[]):
        if isinstance(f.get("ano_fim"),str) and "incompleto" in f["ano_fim"].lower():
            f["ano_fim"] = None; f["observacoes"]="incompleto"

    final = merge_results(forms,exps,sks,lgs)
    levels = [(f.get("nivel") or "").strip().lower() for f in final.get("formacoes",[]) if (f.get("nivel") or "") in education_level_order]
    max_lvl = max(levels,key=lambda x:education_level_order[x]) if levels else None

    print("📦 JSON final:",json.dumps(final,ensure_ascii=False,indent=2))
    return final, max_lvl
