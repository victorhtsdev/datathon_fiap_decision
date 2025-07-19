#!/usr/bin/env python3
"""
Teste para verificar a nova formatação das respostas do chat
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_response_formatting():
    """Testa a nova formatação das respostas"""
    
    print("🧪 TESTE DE FORMATAÇÃO DE RESPOSTAS")
    print("=" * 50)
    
    # Simula dados de candidatos
    mock_candidates = [
        {
            'id': 1,
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'endereco': 'São Paulo, SP',
            'nivel_maximo_formacao': 'Graduação em Engenharia',
            'score_semantico': 0.95,
            'distancia': 0.05,
            'cv_pt': {
                'idiomas': [
                    {'idioma': 'inglês', 'nivel': 'avançado'},
                    {'idioma': 'espanhol', 'nivel': 'intermediário'}
                ],
                'habilidades': ['Python', 'Java', 'React', 'Docker', 'AWS', 'PostgreSQL']
            }
        },
        {
            'id': 2,
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'endereco': 'Rio de Janeiro, RJ',
            'nivel_maximo_formacao': 'Mestrado em Ciência da Computação',
            'score_semantico': 0.92,
            'distancia': 0.08,
            'cv_pt': {
                'idiomas': [
                    {'idioma': 'inglês', 'nivel': 'fluente'},
                    {'idioma': 'francês', 'nivel': 'básico'}
                ],
                'habilidades': ['JavaScript', 'TypeScript', 'Node.js', 'React']
            }
        },
        {
            'id': 3,
            'nome': 'Pedro Costa',
            'email': 'pedro@email.com',
            'endereco': 'Belo Horizonte, MG',
            'nivel_maximo_formacao': 'MBA em Gestão de TI',
            'score_semantico': 0.89,
            'distancia': 0.11,
            'cv_pt': {
                'idiomas': [
                    {'idioma': 'inglês', 'nivel': 'avançado'}
                ],
                'habilidades': ['CSS', 'HTML', 'Sass', 'Bootstrap']
            }
        }
    ]
    
    # Simula critérios extraídos
    extracted_criteria = {
        'usar_similaridade': True,
        'filtros': {
            'idiomas': [
                {'idioma': 'inglês', 'niveis': ['avançado', 'fluente']}
            ],
            'habilidades': ['python', 'css', 'react']
        }
    }
    
    def simulate_fallback_response(candidates, original_criteria, extracted_criteria):
        """Simula a resposta do fallback manual"""
        
        filtros = extracted_criteria.get('filtros', {})
        response_parts = []
        
        # Cabeçalho
        response_parts.append(f"✅ **Encontrei {len(candidates)} candidatos usando busca semântica otimizada**")
        response_parts.append("")
        
        # Filtros aplicados
        if filtros and any(filtros.values()):
            response_parts.append("🔍 **Filtros aplicados:**")
            
            if 'idiomas' in filtros and filtros['idiomas']:
                idiomas_list = []
                for idioma in filtros['idiomas']:
                    if 'niveis' in idioma and idioma['niveis']:
                        nivel_text = ', '.join(idioma['niveis'])
                    else:
                        nivel_text = idioma.get('nivel', 'qualquer nível')
                    idiomas_list.append(f"{idioma['idioma']} ({nivel_text})")
                response_parts.append(f"- 🌐 Idiomas: {', '.join(idiomas_list)}")
            
            if 'habilidades' in filtros and filtros['habilidades']:
                response_parts.append(f"- 💻 Habilidades: {', '.join(filtros['habilidades'])}")
            
            if 'formacao' in filtros and filtros['formacao']:
                formacao_text = []
                if filtros['formacao'].get('nivel'):
                    formacao_text.append(filtros['formacao']['nivel'])
                if filtros['formacao'].get('curso'):
                    formacao_text.append(f"em {filtros['formacao']['curso']}")
                if formacao_text:
                    response_parts.append(f"- 🎓 Formação: {' '.join(formacao_text)}")
            
            if 'localizacao' in filtros:
                response_parts.append(f"- 📍 Localização: {filtros['localizacao']}")
            
            if 'sexo' in filtros:
                response_parts.append(f"- 👤 Sexo: {filtros['sexo']}")
            
            response_parts.append("")
        
        # Lista de candidatos
        response_parts.append("📋 **Candidatos selecionados:**")
        response_parts.append("")
        
        for i, candidate in enumerate(candidates[:5], 1):
            name = candidate.get('nome', 'N/A')
            location = candidate.get('endereco', 'N/A')
            education = candidate.get('nivel_maximo_formacao', 'N/A')
            score = candidate.get('score_semantico', 0)
            
            # Extrai idiomas e habilidades
            cv_data = candidate.get('cv_pt', {})
            idiomas = cv_data.get('idiomas', [])
            idiomas_text = ', '.join([f"{lang.get('idioma', '')} {lang.get('nivel', '')}" for lang in idiomas]) if idiomas else "Não informado"
            
            habilidades = cv_data.get('habilidades', [])
            habilidades_text = ', '.join(habilidades[:3]) if habilidades else "Não informado"
            if len(habilidades) > 3:
                habilidades_text += f" (+{len(habilidades)-3} mais)"
            
            response_parts.append(f"**{i}. {name}**")
            response_parts.append(f"   📍 {location} | 🎓 {education} | 🎯 Score: {score:.3f}")
            response_parts.append(f"   🌐 Idiomas: {idiomas_text}")
            response_parts.append(f"   💻 Habilidades: {habilidades_text}")
            response_parts.append("")
        
        if len(candidates) > 5:
            response_parts.append(f"... **e mais {len(candidates) - 5} candidatos**")
            response_parts.append("")
        
        # Rodapé
        response_parts.append("---")
        response_parts.append("🎯 **Busca baseada em similaridade semântica com a vaga**")
        response_parts.append("💾 **Candidatos salvos como prospects no workbook**")
        
        return '\n'.join(response_parts)
    
    # Testa diferentes cenários
    test_cases = [
        {
            "name": "Busca com idiomas e habilidades",
            "query": "candidatos com inglês avançado ou fluente e que saibam Python, CSS ou React",
            "criteria": extracted_criteria
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 CENÁRIO: {test_case['name']}")
        print(f"🔍 Query: \"{test_case['query']}\"")
        print("-" * 50)
        
        response = simulate_fallback_response(
            mock_candidates, 
            test_case['query'], 
            test_case['criteria']
        )
        
        print(response)
        print("\n" + "=" * 50)

def main():
    """Executa teste de formatação"""
    try:
        test_response_formatting()
        print("\n🎉 TESTE DE FORMATAÇÃO CONCLUÍDO!")
        print("✅ A nova formatação está mais organizada e visualmente atrativa")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
