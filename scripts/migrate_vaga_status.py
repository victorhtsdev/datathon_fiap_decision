#!/usr/bin/env python3
"""
Script para migrar o campo vaga_ativa (Boolean) para status_vaga (Enum)
Este script converte:
- vaga_ativa = True -> status_vaga = 'nao_iniciada'
- vaga_ativa = False -> status_vaga = 'finalizada'
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.core.logging import log_info, log_error

def migrate_vaga_status():
    """Migra dados do campo vaga_ativa para status_vaga"""
    db = SessionLocal()
    try:
        log_info("🔄 Iniciando migração de vaga_ativa para status_vaga...")
        
        # Primeiro, adiciona a nova coluna se não existir
        try:
            db.execute(text("""
                ALTER TABLE vagas 
                ADD COLUMN IF NOT EXISTS status_vaga VARCHAR(20) DEFAULT 'nao_iniciada'
            """))
            db.commit()
            log_info("✅ Coluna status_vaga adicionada")
        except Exception as e:
            log_info(f"ℹ️  Coluna status_vaga já existe ou erro: {e}")
        
        # Verifica se a coluna vaga_ativa ainda existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vagas' AND column_name = 'vaga_ativa'
        """)).fetchone()
        
        if result:
            log_info("📊 Migrando dados de vaga_ativa para status_vaga...")
            
            # Migra dados: True -> nao_iniciada, False -> finalizada
            db.execute(text("""
                UPDATE vagas 
                SET status_vaga = CASE 
                    WHEN vaga_ativa = true THEN 'nao_iniciada'
                    WHEN vaga_ativa = false THEN 'finalizada'
                    ELSE 'nao_iniciada'
                END
                WHERE status_vaga IS NULL OR status_vaga = ''
            """))
            
            # Conta registros migrados
            count_result = db.execute(text("SELECT COUNT(*) FROM vagas")).fetchone()
            total_vagas = count_result[0] if count_result else 0
            
            db.commit()
            log_info(f"✅ Migração concluída! {total_vagas} vagas processadas")
            
            # Remove a coluna antiga (comentado por segurança)
            # log_info("🗑️  Removendo coluna vaga_ativa...")
            # db.execute(text("ALTER TABLE vagas DROP COLUMN IF EXISTS vaga_ativa"))
            # db.commit()
            # log_info("✅ Coluna vaga_ativa removida")
            
        else:
            log_info("ℹ️  Coluna vaga_ativa não encontrada, migração não necessária")
            
        # Verifica o resultado da migração
        status_counts = db.execute(text("""
            SELECT status_vaga, COUNT(*) as count 
            FROM vagas 
            GROUP BY status_vaga
        """)).fetchall()
        
        log_info("📈 Status das vagas após migração:")
        for status, count in status_counts:
            log_info(f"   - {status}: {count} vagas")
            
    except Exception as e:
        log_error(f"❌ Erro durante migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    db = SessionLocal()
    try:
        log_info("🔍 Verificando migração...")
        
        # Verifica se todas as vagas têm status válido
        invalid_status = db.execute(text("""
            SELECT COUNT(*) 
            FROM vagas 
            WHERE status_vaga NOT IN ('nao_iniciada', 'em_andamento', 'finalizada')
               OR status_vaga IS NULL
        """)).fetchone()
        
        if invalid_status and invalid_status[0] > 0:
            log_error(f"❌ {invalid_status[0]} vagas com status inválido encontradas!")
            return False
        else:
            log_info("✅ Todos os status estão válidos")
            return True
            
    except Exception as e:
        log_error(f"❌ Erro durante verificação: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando migração do campo vaga_ativa para status_vaga")
    print("=" * 60)
    
    try:
        migrate_vaga_status()
        
        if verify_migration():
            print("\n🎉 Migração concluída com sucesso!")
            print("\nPróximos passos:")
            print("1. Teste a API para garantir que tudo funciona")
            print("2. Se tudo estiver OK, remova manualmente a coluna vaga_ativa:")
            print("   ALTER TABLE vagas DROP COLUMN vaga_ativa;")
        else:
            print("\n⚠️  Migração concluída mas com problemas detectados")
            
    except Exception as e:
        print(f"\n💥 Falha na migração: {e}")
        sys.exit(1)
