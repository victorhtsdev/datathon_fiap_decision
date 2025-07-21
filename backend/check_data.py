from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/datathon_decision')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    status_positivos = ('Contratado como Hunting', 'Contratado pela Decision', 'Documentação PJ', 'Aprovado', 'Proposta Aceita')
    
    # Vagas únicas
    query1 = f"SELECT COUNT(DISTINCT vaga_id) FROM prospects WHERE situacao_candidado IN {status_positivos}"
    result_vagas = conn.execute(text(query1)).fetchone()
    
    # Total candidatos
    query2 = f"SELECT COUNT(*) FROM prospects WHERE situacao_candidado IN {status_positivos}"
    result_candidatos = conn.execute(text(query2)).fetchone()
    
    print(f'Vagas únicas com candidatos aprovados: {result_vagas[0]}')
    print(f'Total de candidatos aprovados: {result_candidatos[0]}')
    if result_vagas[0] > 0:
        print(f'Média de candidatos aprovados por vaga: {result_candidatos[0] / result_vagas[0]:.2f}')
    
    # Verificar algumas vagas com múltiplos aprovados
    query3 = f"""
    SELECT vaga_id, COUNT(*) as total_aprovados
    FROM prospects 
    WHERE situacao_candidado IN {status_positivos}
    GROUP BY vaga_id
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC
    LIMIT 10
    """
    
    result_multiplos = conn.execute(text(query3)).fetchall()
    print(f'\nExemplos de vagas com múltiplos candidatos aprovados:')
    for vaga_id, total in result_multiplos:
        print(f'  Vaga {vaga_id}: {total} candidatos aprovados')
