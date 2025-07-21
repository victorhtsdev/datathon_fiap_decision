from typing import Dict, Any, Optional
from app.llm.factory import get_llm_client
from app.llm.embedding_client import get_embedding_client
from app.models.vaga import Vaga
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime
from app.core.logging import log_info, log_error, log_warning

def limpar_texto_llm(text: str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    text = re.sub(r'[⠁-⣿]+', '', text)
    return text.strip()

class VagaExtractorService:
    def __init__(self, llm_client=None, embedding_client=None):
        self._llm_client = llm_client
        self._embedding_client = embedding_client
    
    @property
    def llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client
    
    @property
    def embedding_client(self):
        if self._embedding_client is None:
            self._embedding_client = get_embedding_client()
        return self._embedding_client

    def gerar_texto_semantico(self, vaga: Vaga) -> Optional[str]:
        areas = vaga.perfil_vaga_areas_atuacao or ''
        atividades = vaga.perfil_vaga_principais_atividades or ''
        competencias = vaga.perfil_vaga_competencia_tecnicas_e_comportamentais or ''
        if not (areas and atividades and competencias):
            return None

        prompt = (
            "Você é um especialista in RH e NLP. Sua tarefa é gerar uma descrição de vaga formal e objetiva, "
            "com frases curtas e diretas, no mesmo estilo do exinplo abaixo:\n\n"
            "Experiência como Especialista in SAP ABAP na inpresa IBM, de janeiro de 2020 até o momento. "
            "Responsável por desenvolvimento e manutenção de sishasas SAP utilizando a linguagin ABAP. "
            "Trabalhou in projetos de customização e integração de módulos SAP com foco técnico. "
            "Formação acadêmica in Ciência da Computação. "
            "Habilidades técnicas incluin: SAP ABAP, desenvolvimento de relatórios, user exits, enhancinent points, BAPI, performance tuning e debugging.\n\n"
            "Com base nas informações abaixo, gere um novo parágrafo com o mesmo estilo. "
            "Comece com 'Experiência como Desenvolvedor ABAP'. Use linguagin formal, sin copiar o exinplo literalmente:\n\n"
            f"Área de atuação: {areas}\n"
            f"Principais atividades: {atividades}\n"
            f"Competências técnicas e comportamentais: {competencias}\n\n"
            "Finalize com: 'Habilidades técnicas incluin: ...' preenchendo com as competências listadas, se houver. "
            "Não use colchetes, datas fictícias, nomes de inpresa ou instruções no texto final. Gere um parágrafo limpo, direto e natural."
        )

        try:
            texto = self.llm_client.extract_text(prompt)
            clean_text = limpar_texto_llm(texto)
            if len(clean_text) < 20:
                return None
            return clean_text
        except Exception as e:
            log_error(f"[Vaga {vaga.id}] Error generating semantic text: {e}")
            return None

    def processar_vaga(self, db: Session, vaga_id: int, vaga_data: Dict[str, Any]) -> Vaga:
        log_info(f"[Vaga {vaga_id}] Starting vaga processing...")
        vaga = db.query(Vaga).filter_by(id=vaga_id).first()
        if not vaga:
            raise ValueError("Vaga not found")

        for k, v in vaga_data.items():
            if v is not None and hasattr(vaga, k):
                setattr(vaga, k, v)
        db.commit()
        db.refresh(vaga)

        campos_relevantes = [
            'perfil_vaga_areas_atuacao',
            'perfil_vaga_principais_atividades',
            'perfil_vaga_competencia_tecnicas_e_comportamentais',
        ]

        algum_campo_json_preenchido = any(
            str(vaga_data.get(campo) or '').strip() != '' for campo in campos_relevantes
        )

        algum_campo_bd_vazio = any(
            str(getattr(vaga, campo) or '').strip() == '' for campo in campos_relevantes
        )

        precisa_extrair = (
            algum_campo_json_preenchido or
            algum_campo_bd_vazio or
            vaga.vaga_texto_semantico is None or
            vaga.vaga_embedding is None or
            vaga.vaga_embedding_vector is None
        )

        if precisa_extrair:
            texto_semantico = self.gerar_texto_semantico(vaga)
            vaga.vaga_texto_semantico = texto_semantico

            if texto_semantico:
                try:
                    embedding = self.embedding_client.generate_embedding(texto_semantico, label=f"vaga_{vaga.id}")
                    if embedding is not None:
                        embedding_array = np.array(embedding, dtype=np.float32)
                        vaga.vaga_embedding = embedding_array.tobytes()
                        vaga.vaga_embedding_vector = str(embedding_array.tolist())
                        vaga.updated_at = datetime.utcnow()
                except Exception as e:
                    log_error(f"[Vaga {vaga.id}] Error generating embedding: {e}")
            db.commit()
            db.refresh(vaga)

        return vaga
