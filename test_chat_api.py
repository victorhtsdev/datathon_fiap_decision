#!/usr/bin/env python3
"""
Script para testar a API REST do chat com session_id
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
WORKBOOK_ID = "80fb2429-3fe7-4fdc-9bc9-da54e4466b23"

def test_chat_api():
    """Testa a API do chat com session_id"""
    print("🔄 Testando API do chat com session_id...")
    
    # Primeira mensagem - sem session_id
    print("\n1️⃣ Primeira mensagem (criando sessão):")
    payload1 = {
        "message": "filtre 4 candidatos",
        "workbook_id": WORKBOOK_ID
    }
    
    response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
    result1 = response1.json()
    
    session_id = result1.get('session_id')
    print(f"   ✅ Session criada: {session_id}")
    print(f"   📝 Response: {result1['response'][:100]}...")
    
    # Segunda mensagem - com session_id
    print("\n2️⃣ Segunda mensagem (usando sessão existente):")
    payload2 = {
        "message": "mas traga somente os que tem ingles pelo menos intermediario",
        "workbook_id": WORKBOOK_ID,
        "session_id": session_id
    }
    
    response2 = requests.post(f"{BASE_URL}/chat", json=payload2)
    result2 = response2.json()
    
    print(f"   ✅ Session utilizada: {result2.get('session_id')}")
    print(f"   📝 Response: {result2['response'][:100]}...")
    
    # Verificar se é a mesma sessão
    if session_id == result2.get('session_id'):
        print("\n✅ SUCESSO: As sessões são iguais - contexto preservado!")
    else:
        print("\n❌ FALHA: Sessões diferentes - contexto perdido!")
        
    # Verificar histórico
    print("\n📚 Verificando histórico da sessão:")
    history_response = requests.get(f"{BASE_URL}/chat/history/{session_id}")
    history = history_response.json()
    
    if history.get('found'):
        messages = history.get('messages', [])
        print(f"   ✅ Histórico encontrado: {len(messages)} mensagens")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. [{msg['sender']}] {msg['content'][:80]}...")
    else:
        print("   ❌ Histórico não encontrado")

if __name__ == "__main__":
    test_chat_api()
