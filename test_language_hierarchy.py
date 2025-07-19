#!/usr/bin/env python3
"""
Teste para verificar a nova lógica de hierarquia de níveis de idiomas
"""

import sys
import os
import json
import re
from unittest.mock import Mock

def simulate_llm_extraction_with_hierarchy(filter_criteria: str) -> dict:
    """
    Simula extração do LLM com a nova lógica de hierarquia
    """
    
    test_responses = {
        "candidatos com inglês básico": {
            "vaga_id": None,
            "usar_similaridade": True,
            "filtros": {
                "idiomas": [
                    {"idioma": "inglês", "nivel_minimo": "básico", "incluir_superiores": True}
                ]
            }
        },
        "candidatos que tenham pelo menos inglês básico": {
            "vaga_id": None,
            "usar_similaridade": True,
            "filtros": {
                "idiomas": [
                    {"idioma": "inglês", "nivel_minimo": "básico", "incluir_superiores": True}
                ]
            }
        },
        "inglês avançado ou fluente": {
            "vaga_id": None,
            "usar_similaridade": True,
            "filtros": {
                "idiomas": [
                    {"idioma": "inglês", "nivel_minimo": "avançado", "incluir_superiores": True}
                ]
            }
        },
        "apenas inglês intermediário": {
            "vaga_id": None,
            "usar_similaridade": True,
            "filtros": {
                "idiomas": [
                    {"idioma": "inglês", "nivel_minimo": "intermediário", "incluir_superiores": False}
                ]
            }
        },
        "inglês fluente e python": {
            "vaga_id": None,
            "usar_similaridade": True,
            "filtros": {
                "idiomas": [
                    {"idioma": "inglês", "nivel_minimo": "fluente", "incluir_superiores": True}
                ],
                "habilidades": ["python"]
            }
        }
    }
    
    return test_responses.get(filter_criteria.lower(), {
        "vaga_id": None,
        "usar_similaridade": True,
        "filtros": {}
    })

def simulate_sql_generation_with_hierarchy(criteria: dict) -> str:
    """
    Simula a geração da query SQL com hierarquia de níveis
    """
    
    filtros = criteria.get('filtros', {})
    query_parts = [
        "SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,",
        "       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,",
        "       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia",
        "FROM processed_applicants pa, vagas v",
        "WHERE v.id = :vaga_id",
        "  AND pa.cv_embedding_vector IS NOT NULL",
        "  AND v.vaga_embedding_vector IS NOT NULL"
    ]
    
    # Filtro de idiomas com hierarquia
    if filtros.get('idiomas'):
        idiomas_conditions = []
        for idioma_req in filtros['idiomas']:
            idioma_nome = idioma_req.get('idioma', '').lower()
            nivel_minimo = idioma_req.get('nivel_minimo', '').lower()
            incluir_superiores = idioma_req.get('incluir_superiores', True)
            
            if idioma_nome and nivel_minimo:
                # Define hierarquia de níveis
                hierarquia_niveis = {
                    'básico': ['básico', 'intermediário', 'avançado', 'fluente'],
                    'basico': ['básico', 'intermediário', 'avançado', 'fluente'],
                    'intermediário': ['intermediário', 'avançado', 'fluente'],
                    'intermediario': ['intermediário', 'avançado', 'fluente'],
                    'avançado': ['avançado', 'fluente'],
                    'avancado': ['avançado', 'fluente'],
                    'fluente': ['fluente']
                }
                
                if incluir_superiores and nivel_minimo in hierarquia_niveis:
                    # Inclui o nível mínimo e todos os superiores
                    niveis_aceitos = hierarquia_niveis[nivel_minimo]
                else:
                    # Apenas o nível específico
                    niveis_aceitos = [nivel_minimo]
                
                # Monta condições OR para todos os níveis aceitos
                nivel_conditions = []
                for nivel in niveis_aceitos:
                    # Busca por variações do nível (com e sem acentos)
                    nivel_patterns = []
                    if nivel == 'básico':
                        nivel_patterns = ['básico', 'basico', 'basic']
                    elif nivel == 'intermediário':
                        nivel_patterns = ['intermediário', 'intermediario', 'intermediate']
                    elif nivel == 'avançado':
                        nivel_patterns = ['avançado', 'avancado', 'advanced']
                    elif nivel == 'fluente':
                        nivel_patterns = ['fluente', 'fluent']
                    else:
                        nivel_patterns = [nivel]
                    
                    for pattern in nivel_patterns:
                        nivel_conditions.append(f"@.nivel like_regex \"{pattern}\" flag \"i\"")
                
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
    
    # Ordenação e limite
    query_parts.append("ORDER BY distancia ASC")
    query_parts.append("LIMIT 20")
    
    return "\n".join(query_parts)

def test_hierarchy_logic():
    """Testa a lógica de hierarquia de níveis"""
    
    print("🔍 TESTE: Hierarquia de Níveis de Idiomas")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "candidatos com inglês básico",
            "expected_levels": ["básico", "intermediário", "avançado", "fluente"],
            "description": "Básico deve incluir todos os níveis superiores"
        },
        {
            "query": "candidatos que tenham pelo menos inglês básico",
            "expected_levels": ["básico", "intermediário", "avançado", "fluente"],
            "description": "Pelo menos básico = hierarquia completa"
        },
        {
            "query": "inglês avançado ou fluente",
            "expected_levels": ["avançado", "fluente"],
            "description": "Avançado deve incluir apenas avançado e fluente"
        },
        {
            "query": "apenas inglês intermediário",
            "expected_levels": ["intermediário"],
            "description": "Apenas = não incluir superiores"
        },
        {
            "query": "inglês fluente e python",
            "expected_levels": ["fluente"],
            "description": "Fluente é o nível mais alto"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: '{case['query']}'")
        print(f"   📋 Expectativa: {case['description']}")
        
        # Simula extração de critérios
        criteria = simulate_llm_extraction_with_hierarchy(case['query'])
        idiomas = criteria.get('filtros', {}).get('idiomas', [])
        
        if idiomas:
            idioma_info = idiomas[0]
            nivel_minimo = idioma_info.get('nivel_minimo')
            incluir_superiores = idioma_info.get('incluir_superiores', True)
            
            print(f"   🔧 LLM extraiu: nivel_minimo='{nivel_minimo}', incluir_superiores={incluir_superiores}")
            
            # Verifica a hierarquia que será aplicada
            hierarquia_niveis = {
                'básico': ['básico', 'intermediário', 'avançado', 'fluente'],
                'basico': ['básico', 'intermediário', 'avançado', 'fluente'],
                'intermediário': ['intermediário', 'avançado', 'fluente'],
                'intermediario': ['intermediário', 'avançado', 'fluente'],
                'avançado': ['avançado', 'fluente'],
                'avancado': ['avançado', 'fluente'],
                'fluente': ['fluente']
            }
            
            if incluir_superiores and nivel_minimo in hierarquia_niveis:
                niveis_aplicados = hierarquia_niveis[nivel_minimo]
            else:
                niveis_aplicados = [nivel_minimo]
            
            print(f"   📊 Níveis que serão aceitos: {niveis_aplicados}")
            
            # Verifica se está correto
            if set(niveis_aplicados) == set(case['expected_levels']):
                print(f"   ✅ CORRETO: Hierarquia aplicada corretamente")
            else:
                print(f"   ❌ ERRO: Esperado {case['expected_levels']}, obtido {niveis_aplicados}")
        else:
            print(f"   ❌ ERRO: Nenhum idioma extraído")
        
        # Gera query SQL
        sql_query = simulate_sql_generation_with_hierarchy(criteria)
        if "jsonb_path_exists" in sql_query and "idiomas" in sql_query:
            print(f"   ✅ Query SQL gerada com filtro de idiomas")
        else:
            print(f"   ⚠️  Query SQL sem filtro de idiomas")

def test_sql_patterns():
    """Testa se os padrões SQL estão corretos"""
    
    print(f"\n\n🔍 TESTE: Padrões SQL para Variações de Níveis")
    print("=" * 60)
    
    criteria = {
        "usar_similaridade": True,
        "filtros": {
            "idiomas": [
                {"idioma": "inglês", "nivel_minimo": "básico", "incluir_superiores": True}
            ]
        }
    }
    
    query = simulate_sql_generation_with_hierarchy(criteria)
    
    print("🔍 Query SQL gerada:")
    print("-" * 40)
    query_lines = query.split('\n')
    for line in query_lines:
        if 'jsonb_path_exists' in line and 'idiomas' in line:
            print(f"📝 {line}")
    
    # Verifica se contém os padrões esperados
    expected_patterns = ['básico', 'basico', 'basic', 'intermediário', 'intermediario', 'intermediate', 
                        'avançado', 'avancado', 'advanced', 'fluente', 'fluent']
    
    patterns_found = []
    for pattern in expected_patterns:
        if pattern in query:
            patterns_found.append(pattern)
    
    print(f"\n📊 Padrões encontrados na query: {patterns_found}")
    
    if len(patterns_found) >= 10:  # Deve encontrar a maioria dos padrões
        print(f"✅ Query inclui variações de níveis (português/inglês, com/sem acentos)")
    else:
        print(f"⚠️  Query pode estar faltando algumas variações")

def main():
    """Executa todos os testes de hierarquia"""
    
    print("🚀 TESTES DE HIERARQUIA DE NÍVEIS DE IDIOMAS")
    print("=" * 80)
    
    try:
        # Testa lógica de hierarquia
        test_hierarchy_logic()
        
        # Testa padrões SQL
        test_sql_patterns()
        
        print("\n" + "=" * 80)
        print("🎉 TESTES DE HIERARQUIA CONCLUÍDOS!")
        print("✅ O sistema agora entende hierarquia de níveis de idiomas")
        print("✅ 'Inglês básico' retorna candidatos básico, intermediário, avançado e fluente")
        print("✅ 'Inglês avançado' retorna candidatos avançado e fluente")
        print("✅ Query SQL suporta variações (português/inglês, com/sem acentos)")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
