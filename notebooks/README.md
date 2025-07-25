# 📚 Notebooks do Projeto — Pesquisa Semântica de Candidatos

Esta pasta contém notebooks organizados por etapa do pipeline de processamento e avaliação de currículos e vagas. Abaixo estão os notebooks disponíveis e suas respectivas descrições.

---

## 🧠 1. `Normalizacao_CV_Gemma_v1.ipynb`

Notebook responsável por:

- Extrair informações estruturadas de currículos (formações, experiências, habilidades, idiomas) usando o modelo `Gemma` via Ollama.
- Gerar JSON estruturado por candidato.
- Calcular o nível máximo de formação considerando regras de negócio (ignora "em andamento", "trancado", etc.).
- Armazenar os dados tratados na tabela `processed_applicants`.

---

## 🔍 2. `Pesquisa_Semantica_Teste.ipynb`

Notebook de testes para:

- Verificar a qualidade da busca semântica com embeddings.
- Realizar buscas por similaridade entre candidatos e vagas usando embeddings vetoriais.
- Avaliar o funcionamento do motor de busca antes da integração final.

---

## 🎯 3. `Avaliacao_PesquisaSemantica.ipynb`

Notebook de avaliação da performance da busca semântica:

- Analisa os candidatos aprovados e suas posições no ranking retornado.
- Calcula métricas como posição média, mediana, Top 1, Top 3, Top 5 e Top 10.
- Gera insights sobre a efetividade do algoritmo de recomendação semântica.
- Usado para validar se o modelo está priorizando bem os candidatos mais adequados.

---

## 📄 4. `Tratamento_semantico.ipynb`

Notebook que:

- Converte o JSON estruturado dos currículos em texto semântico.
- Utiliza esse texto para posterior geração de embeddings.
- Serve como ponte entre a extração via LLM e a etapa de similaridade vetorial.

---

## 📄 5. `Tratamento_Semantico_Vaga.ipynb`

Notebook semelhante ao anterior, mas focado em vagas:

- Trata a descrição bruta da vaga e extrai o texto semântico correspondente.
- Prepara os dados da vaga para geração de embeddings e comparação com candidatos.
- Pode incluir normalização textual e regras específicas para transformar vagas em representações mais precisas.

---

## ✅ Observações

- Os notebooks seguem uma ordem lógica: **extração → tratamento → embeddings → avaliação**.
- Todo o pipeline pode ser automatizado futuramente, mas os notebooks permitem controle manual e validação em cada etapa.
- O projeto utiliza modelos LLM locais (`Ollama + Gemma`) e pode ser adaptado para OpenAI ou DeepSeek.

---