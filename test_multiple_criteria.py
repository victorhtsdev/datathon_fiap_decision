#!/usr/bin/env python3
"""
Teste para verificar a melhoria na extração de critérios múltiplos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import re
from unittest.mock import Mock

def test_improved_criteria_extraction():
    """Testa a extração melhorada de critérios múltiplos"""
    
    print("🧪 TESTE DE EXTRAÇÃO DE CRITÉRIOS MÚLTIPLOS")
    print("=" * 60)
    
    # Casos de teste para verificar múltiplas opções
    test_cases = [
        {
            "input": "filtre 10 candidatos que tenham inglês avançado ou fluente",
            "expected_json": {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "idiomas": [
                        {"idioma": "inglês", "niveis": ["avançado", "fluente"]}
                    ]
                }
            }
        },
        {
            "input": "candidatos com Java, Python e CSS",
            "expected_json": {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "habilidades": ["java", "python", "css"]
                }
            }
        },
        {
            "input": "desenvolvedor React ou Angular com inglês fluente ou nativo",
            "expected_json": {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "habilidades": ["react", "angular"],
                    "idiomas": [
                        {"idioma": "inglês", "niveis": ["fluente", "nativo"]}
                    ]
                }
            }
        },
        {
            "input": "candidato com espanhol intermediário ou avançado e Python",
            "expected_json": {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "idiomas": [
                        {"idioma": "espanhol", "niveis": ["intermediário", "avançado"]}
                    ],
                    "habilidades": ["python"]
                }
            }
        }
    ]
    
    def simulate_improved_llm(query):
        """Simula o LLM melhorado que captura múltiplas opções"""
        
        # Análise básica para simulação
        if "inglês avançado ou fluente" in query.lower():
            return {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "idiomas": [
                        {"idioma": "inglês", "niveis": ["avançado", "fluente"]}
                    ]
                }
            }
        elif "java, python e css" in query.lower():
            return {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "habilidades": ["java", "python", "css"]
                }
            }
        elif "react ou angular" in query.lower() and "inglês fluente ou nativo" in query.lower():
            return {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "habilidades": ["react", "angular"],
                    "idiomas": [
                        {"idioma": "inglês", "niveis": ["fluente", "nativo"]}
                    ]
                }
            }
        elif "espanhol intermediário ou avançado" in query.lower() and "python" in query.lower():
            return {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {
                    "idiomas": [
                        {"idioma": "espanhol", "niveis": ["intermediário", "avançado"]}
                    ],
                    "habilidades": ["python"]
                }
            }
        else:
            return {
                "vaga_id": None,
                "usar_similaridade": True,
                "filtros": {}
            }
    
    def generate_sql_query(criteria):
        """Simula a geração da query SQL melhorada"""
        
        query_parts = [
            "SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,",
            "       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,",
            "       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia",
            "FROM processed_applicants pa, vagas v",
            "WHERE v.id = :vaga_id",
            "  AND pa.cv_embedding_vector IS NOT NULL",
            "  AND v.vaga_embedding_vector IS NOT NULL"
        ]
        
        filtros = criteria.get('filtros', {})
        
        # Filtro de idiomas melhorado
        if filtros.get('idiomas'):
            idiomas_conditions = []
            for idioma_req in filtros['idiomas']:
                idioma_nome = idioma_req.get('idioma', '').lower()
                
                # Suporte para múltiplos níveis
                if 'niveis' in idioma_req and idioma_req['niveis']:
                    niveis = [nivel.lower() for nivel in idioma_req['niveis']]
                    nivel_conditions = []
                    for nivel in niveis:
                        nivel_conditions.append(f"@.nivel like_regex \"{nivel}\" flag \"i\"")
                    nivel_query = f"({' || '.join(nivel_conditions)})"
                    
                    idiomas_conditions.append(
                        f"jsonb_path_exists(pa.cv_pt_json, "
                        f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\" && {nivel_query})')"
                    )
            
            if idiomas_conditions:
                query_parts.append(f"  AND ({' OR '.join(idiomas_conditions)})")
        
        # Filtro de habilidades
        if filtros.get('habilidades'):
            habilidades_conditions = []
            for habilidade in filtros['habilidades']:
                habilidade_clean = habilidade.lower().strip()
                if habilidade_clean:
                    habilidades_conditions.append(
                        f"jsonb_path_exists(pa.cv_pt_json, "
                        f"'$.habilidades[*] ? (@ like_regex \"{habilidade_clean}\" flag \"i\")')"
                    )
            
            if habilidades_conditions:
                query_parts.append(f"  AND ({' OR '.join(habilidades_conditions)})")
        
        query_parts.extend([
            "ORDER BY distancia ASC",
            "LIMIT 20"
        ])
        
        return "\n".join(query_parts)
    
    # Executa testes
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TESTE {i}: '{test_case['input']}'")
        print("-" * 40)
        
        # Simula extração de critérios
        extracted = simulate_improved_llm(test_case['input'])
        
        print(f"✅ Critérios extraídos:")
        print(f"   📋 JSON: {json.dumps(extracted, indent=2, ensure_ascii=False)}")
        
        # Verifica se capturou múltiplas opções
        filtros = extracted.get('filtros', {})
        
        if 'idiomas' in filtros:
            for idioma in filtros['idiomas']:
                if 'niveis' in idioma and len(idioma['niveis']) > 1:
                    print(f"   ✅ Múltiplos níveis detectados: {idioma['niveis']}")
                elif 'nivel' in idioma:
                    print(f"   📌 Nível único: {idioma['nivel']}")
        
        if 'habilidades' in filtros and len(filtros['habilidades']) > 1:
            print(f"   ✅ Múltiplas habilidades detectadas: {filtros['habilidades']}")
        
        # Gera SQL
        sql_query = generate_sql_query(extracted)
        print(f"\n🔍 Query SQL gerada:")
        
        # Mostra partes relevantes da query
        sql_lines = sql_query.split('\n')
        for line in sql_lines:
            if 'jsonb_path_exists' in line or 'ORDER BY' in line:
                print(f"   {line.strip()}")
        
        # Verifica se a query contém OR para múltiplas opções
        if '||' in sql_query or ' OR ' in sql_query:
            print(f"   ✅ Query usa OR para múltiplas opções")
        else:
            print(f"   📌 Query não contém múltiplas opções")

def main():
    """Executa o teste"""
    print("🚀 INICIANDO TESTE DE CRITÉRIOS MÚLTIPLOS")
    print("=" * 80)
    
    test_improved_criteria_extraction()
    
    print("\n" + "=" * 80)
    print("🎉 TESTE CONCLUÍDO!")
    print("✅ Verifique se o LLM está capturando múltiplas opções corretamente")
    print("✅ Verifique se as queries SQL usam OR para combinar opções")

if __name__ == "__main__":
    main()
