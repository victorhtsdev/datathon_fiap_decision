#!/usr/bin/env python3
"""
Script para testar se o problema da sessão foi corrigido.
Simula múltiplas mensagens consecutivas no chat.
"""

import asyncio
import sys
import os

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.chat.services.chat_orchestrator import ChatOrchestrator
from app.core.database import SessionLocal


async def test_session_persistence():
    """Testa se as sessões persistem entre mensagens"""
    print("🔄 Testando persistência de sessões...")
    
    db = SessionLocal()
    orchestrator = ChatOrchestrator(db)
    
    workbook_id = "80fb2429-3fe7-4fdc-9bc9-da54e4466b23"  # ID do workbook do log
    
    try:
        # Primeira mensagem - deve criar nova sessão
        print("\n1️⃣ Primeira mensagem (criando sessão):")
        result1 = await orchestrator.process_message(
            message="filtre 4 candidatos",
            workbook_id=workbook_id
        )
        
        session_id = result1.get('session_id')
        print(f"   ✅ Session criada: {session_id}")
        print(f"   📝 Response: {result1['response'][:100]}...")
        
        # Segunda mensagem - deve usar sessão existente
        print("\n2️⃣ Segunda mensagem (usando sessão existente):")
        result2 = await orchestrator.process_message(
            message="mas traga somente os que tem ingles pelo menos intermediario",
            session_id=session_id,
            workbook_id=workbook_id
        )
        
        print(f"   ✅ Session utilizada: {result2.get('session_id')}")
        print(f"   📝 Response: {result2['response'][:100]}...")
        
        # Verificar se é a mesma sessão
        if session_id == result2.get('session_id'):
            print("\n✅ SUCESSO: As sessões são iguais - contexto preservado!")
        else:
            print("\n❌ FALHA: Sessões diferentes - contexto perdido!")
            
        # Verificar histórico da sessão
        session = orchestrator.get_session(session_id)
        if session:
            print(f"\n📚 Histórico da sessão ({len(session.messages)} mensagens):")
            for i, msg in enumerate(session.messages, 1):
                print(f"   {i}. [{msg.sender}] {msg.content[:80]}...")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_session_persistence())
