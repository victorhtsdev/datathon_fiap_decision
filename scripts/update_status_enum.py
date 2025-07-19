#!/usr/bin/env python3
"""
Script para atualizar o enum StatusVaga no banco PostgreSQL
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório pai ao path para poder importar os módulos
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine, text
from app.core.config import settings


def update_status_vaga_enum():
    """Atualiza o enum StatusVaga no banco PostgreSQL"""
    
    # Configurar conexão com o banco
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Iniciar transação
            trans = connection.begin()
            
            try:
                print("🔄 Atualizando enum StatusVaga no banco de dados...")
                
                # Verificar se o enum existe
                check_enum = text("""
                    SELECT 1 FROM pg_type WHERE typname = 'statusvaga'
                """)
                
                result = connection.execute(check_enum).fetchone()
                
                if result:
                    print("✅ Enum StatusVaga encontrado. Adicionando novos valores...")
                    
                    # Adicionar novos valores ao enum existente
                    new_values = ['aberta', 'em_analise', 'pausada', 'cancelada']
                    
                    for value in new_values:
                        # Verificar se o valor já existe
                        check_value = text("""
                            SELECT 1 FROM pg_enum 
                            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'statusvaga')
                            AND enumlabel = :value
                        """)
                        
                        exists = connection.execute(check_value, {"value": value}).fetchone()
                        
                        if not exists:
                            # Adicionar o novo valor
                            add_value = text(f"ALTER TYPE statusvaga ADD VALUE '{value}'")
                            connection.execute(add_value)
                            print(f"  ➕ Adicionado valor: {value}")
                        else:
                            print(f"  ✓ Valor já existe: {value}")
                
                else:
                    print("❌ Enum StatusVaga não encontrado no banco.")
                    print("O banco pode estar usando um tipo diferente ou não ter sido criado ainda.")
                    
                    # Listar todos os enums disponíveis
                    list_enums = text("""
                        SELECT typname FROM pg_type WHERE typtype = 'e'
                    """)
                    enums = connection.execute(list_enums).fetchall()
                    print("Enums disponíveis no banco:")
                    for enum_name in enums:
                        print(f"  - {enum_name[0]}")
                
                # Commit da transação
                trans.commit()
                print("✅ Atualização do enum concluída com sucesso!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Erro durante a atualização: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        raise


def check_enum_values():
    """Verifica os valores atuais do enum StatusVaga"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Listar valores do enum
            query = text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'statusvaga')
                ORDER BY enumsortorder
            """)
            
            values = connection.execute(query).fetchall()
            
            print("📋 Valores atuais do enum StatusVaga:")
            for value in values:
                print(f"  - {value[0]}")
                
    except Exception as e:
        print(f"❌ Erro ao verificar enum: {e}")


if __name__ == "__main__":
    print("🔄 Script de Atualização do Enum StatusVaga")
    print("=" * 45)
    
    # Verificar valores atuais
    print("1. Verificando valores atuais...")
    check_enum_values()
    
    print("\n" + "=" * 45)
    
    # Atualizar o enum
    print("2. Atualizando enum...")
    update_status_vaga_enum()
    
    print("\n" + "=" * 45)
    
    # Verificar valores após atualização
    print("3. Verificando valores após atualização...")
    check_enum_values()
