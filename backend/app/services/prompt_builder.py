def build_prompt(section_name: str, schema_snippet: str, cv_text: str) -> str:
    if section_name == "formacoes":
        prompt_base = (
            "Você é um especialista em RH. Extraia apenas a **formação acadêmica formal** do currículo abaixo.\n\n"
            "⚠️ NÃO inclua experiências profissionais, cargos ou atividades realizadas no trabalho.\n"
            "⚠️ NÃO confunda certificações, treinamentos curtos ou cursos livres com formação acadêmica.\n"
            "⚠️ Ignore nomes de empresas, funções (ex: analista, gerente, técnico) e ambientes de trabalho.\n"
            "❌ Nunca use nomes de empresas como instituição de ensino.\n"
            "❌ Nunca crie formações genéricas sem curso explícito.\n"
            "❌ Nunca invente cursos com base no nome de instituições mencionadas em experiências profissionais (ex: onde a pessoa deu aula, participou de eventos ou prestou serviços).\n"
            "✅ Considere apenas instituições formais (escolas, faculdades, universidades, centros técnicos reconhecidos).\n"
            "✅ Sempre inclua o ensino médio (ex: 'ensino médio', '2º grau completo') se for mencionado.\n\n"
            "📌 Certificações (ex: PMP, Java Programmer, SAFe Agilist) devem ser classificadas como tipo 'certificacao' no campo 'nivel'.\n"
            "📌 Cursos livres, treinamentos, bootcamps, workshops e formações SAP devem ser classificados como tipo 'curso' no campo 'nivel'.\n"
            "📌 Um curso simples ou certificação geralmente é de curta duração, não conduz a um diploma acadêmico e é focado em uma habilidade específica.\n"
            "📌 Nunca classifique certificações, cursos livres ou formações SAP como 'tecnólogo'.\n"
            "📌 Cursos com nome iniciado por **'Tecnologia em ...'** devem ser classificados como **'tecnólogo'** (nível superior).\n"
            "📌 Cursos com nome iniciado por **'Técnico em ...'** devem ser classificados como **'técnico'** (nível médio).\n"
            "📌 Atenção: **'Tecnologia'** no nome do curso indica um curso tecnólogo (superior), enquanto **'Técnico'** indica um curso técnico (médio). Nunca confunda os dois.\n\n"
            f"Formato esperado (JSON com a chave '{section_name}'):\n{schema_snippet}\n\n"
            "Regras obrigatórias:\n"
            "- Campo 'nivel': use apenas uma das opções: ensino médio, técnico, tecnólogo, graduação, pós-graduação, especialização, MBA, mestrado, doutorado, curso, certificacao.\n"
            "- Campo 'observacoes': use apenas quando a formação estiver incompleta, trancada ou interrompida (ex: 'incompleto', 'trancado'); caso contrário, use null.\n"
            "- Os campos 'ano_inicio' e 'ano_fim' devem obrigatoriamente conter mês e ano no formato MM/YYYY. Exemplo válido: '03/2018'.\n"
            "- Nunca preencha apenas o mês (ex: '01') ou apenas o ano (ex: '2018'). Ambos devem estar presentes. Se o mês for desconhecido, use '01' como padrão.\n"
            f"- O JSON deve começar com '{{ \"{section_name}\": [' }}'"
        )
    elif section_name == "experiencias":
        prompt_base = (
            "Você é um especialista em RH. Extraia todas as **experiências profissionais formais** do currículo abaixo.\n\n"
            f"{schema_snippet}\n\n"
            "⚠️ **Regras obrigatórias**:\n"
            "- Experiência é qualquer atividade em empresa, escola, hospital, órgão público ou consultoria com *cargo* declarado.\n"
            "- NÃO confunda experiência com formação ou cursos.\n"
            "- Ignore linhas como 'ensino superior', 'pós-graduação', 'MBA', etc., quando não houver cargo.\n"
            "- Para cada experiência retorne:\n"
            "  • **empresa**\n"
            "  • **cargo**\n"
            "  • **data início** e **data fim** devem estar obrigatoriamente no formato **MM/AAAA**, com **mês e ano em formato numérico** (ex: '03/2022'). Se o mês não for informado, use '01' como padrão.\n"
            "  • **descrição** detalhada das atividades\n"
            "- **NUNCA** preencha datas como 'MM/0000', '0000', '2022', 'jan/2020' ou similares. Use sempre números.\n"
            "- Se não conseguir extrair ao menos o ANO, marque a experiência como **inválida** e NÃO a inclua.\n"
            "- Cada empresa/cargo deve ser um item separado (não agrupe várias empresas).\n"
            "- Instituições educacionais contam como experiência apenas se houver cargo (ex.: instrutor, professor).\n"
            f"- Se não houver experiências válidas, devolva: {{ \"{section_name}\": [] }}\n"
        )
    elif section_name == "habilidades":
        prompt_base = (
            "Você é um especialista em RH. Extraia as habilidades técnicas e profissionais do currículo abaixo.\n\n"
            f"Formato: JSON com a chave '{section_name}' e lista de habilidades.\n\n"
            f"{schema_snippet}\n\n"
            "Regras:\n"
            "- Cada item deve ser uma habilidade única.\n"
            "- Não agrupe várias ferramentas em uma única string.\n"
            "- Idiomas não entram em habilidades."
        )
    elif section_name == "idiomas":
        prompt_base = (
            "Você é um especialista em RH. Extraia **apenas os idiomas falados ou estudados** mencionados no currículo abaixo.\n\n"
            f"Formato esperado:\n{schema_snippet}\n\n"
            "⚠️ Regras obrigatórias:\n"
            "- NÃO inclua nomes de escolas de idiomas (ex: CNA, Wizard, Fisk, etc.)\n"
            "- NÃO deduza idiomas com base em nomes de instituições, culturas ou nacionalidade\n"
            "- NÃO inclua linguagens de programação (ex: Python, Java, etc.)\n"
            f"- Se nenhum idioma for citado claramente, retorne: {{ '{section_name}': [] }}\n"
            "- Campo 'nivel' deve ser: básico, intermediário, avançado, fluente ou nativo. Use null se ausente."
        )
    else:
        prompt_base = f"{schema_snippet}\n\n{cv_text}"
    return f"{prompt_base}\n\nCurrículo:\n{cv_text}"
