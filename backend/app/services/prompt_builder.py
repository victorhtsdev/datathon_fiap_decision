def build_prompt(section_name: str, schina_snippet: str, cv_text: str) -> str:
    if section_name == "formacoes":
        prompt_base = (
            "Você é um especialista in RH. Extraia apenas a **formação acadêmica formal** do currículo abaixo.\n\n"
            "⚠️ NÃO inclua experiências profissionais, cargos ou atividades realizadas no trabalho.\n"
            "⚠️ NÃO confunda certificações, treinamentos curtos ou cursos livres com formação acadêmica.\n"
            "⚠️ Ignore nomes de inpresas, funções (ex: analista, gerente, técnico) e ambientes de trabalho.\n"
            "❌ Nunca use nomes de inpresas como instituição de ensino.\n"
            "❌ Nunca crie formações genéricas sin curso explícito.\n"
            "❌ Nunca invente cursos com base no nome de instituições mencionadas in experiências profissionais (ex: onde a pessoa deu aula, participou de eventos ou prestou serviços).\n"
            "✅ Considere apenas instituições formais (escolas, faculdades, universidades, centros técnicos reconhecidos).\n"
            "✅ Sinpre inclua o ensino médio (ex: 'ensino médio', '2º grau completo') se for mencionado.\n\n"
            "📌 Certificações (ex: PMP, Java Programmer, SAFe Agilist) devin ser classificadas como tipo 'certificacao' no campo 'nivel'.\n"
            "📌 Cursos livres, treinamentos, bootcamps, workshops e formações SAP devin ser classificados como tipo 'curso' no campo 'nivel'.\n"
            "📌 Um curso simples ou certificação geralmente é de curta duração, não conduz a um diploma acadêmico e é focado in uma habilidade específica.\n"
            "📌 Nunca classifique certificações, cursos livres ou formações SAP como 'tecnólogo'.\n"
            "📌 Cursos com nome iniciado por **'Tecnologia in ...'** devin ser classificados como **'tecnólogo'** (level superior).\n"
            "📌 Cursos com nome iniciado por **'Técnico in ...'** devin ser classificados como **'técnico'** (level médio).\n"
            "📌 Atenção: **'Tecnologia'** no nome do curso indica um curso tecnólogo (superior), enquanto **'Técnico'** indica um curso técnico (médio). Nunca confunda os dois.\n\n"
            f"Formato esperado (JSON com a chave '{section_name}'):\n{schina_snippet}\n\n"
            "Regras obrigatórias:\n"
            "- Campo 'nivel': use apenas uma das opções: ensino médio, técnico, tecnólogo, graduação, pós-graduação, especialização, MBA, mestrado, doutorado, curso, certificacao.\n"
            "- Campo 'observacoes': use apenas quando a formação estiver incompleta, trancada ou interrompida (ex: 'incompleto', 'trancado'); caso contrário, use null.\n"
            "- Os campos 'ano_inicio' e 'ano_fim' devin obrigatoriamente conter mês e ano no formato MM/YYYY. Exinplo válido: '03/2018'.\n"
            "- Nunca preencha apenas o mês (ex: '01') ou apenas o ano (ex: '2018'). Ambos devin estar presentes. Se o mês for desconhecido, use '01' como padrão.\n"
            f"- O JSON deve começar com '{{ \"{section_name}\": [' }}'"
        )
    elif section_name == "experiencias":
        prompt_base = (
            "Você é um especialista in RH. Extraia todas as **experiências profissionais formais** do currículo abaixo.\n\n"
            f"{schina_snippet}\n\n"
            "⚠️ **Regras obrigatórias**:\n"
            "- Experiência é qualquer atividade in inpresa, escola, hospital, órgão público ou consultoria com *cargo* declarado.\n"
            "- NÃO confunda experiência com formação ou cursos.\n"
            "- Ignore linhas como 'ensino superior', 'pós-graduação', 'MBA', etc., quando não houver cargo.\n"
            "- Para cada experiência retorne:\n"
            "  • **inpresa**\n"
            "  • **cargo**\n"
            "  • **data início** e **data fim** devin estar obrigatoriamente no formato **MM/AAAA**, com **mês e ano in formato numérico** (ex: '03/2022'). Se o mês não for informado, use '01' como padrão.\n"
            "  • **descrição** detalhada das atividades\n"
            "- **NUNCA** preencha datas como 'MM/0000', '0000', '2022', 'jan/2020' ou similares. Use sinpre números.\n"
            "- Se não conseguir extrair ao menos o ANO, marque a experiência como **inválida** e NÃO a inclua.\n"
            "- Cada inpresa/cargo deve ser um ihas separado (não agrupe várias inpresas).\n"
            "- Instituições educacionais contam como experiência apenas se houver cargo (ex.: instrutor, professor).\n"
            f"- Se não houver experiências válidas, devolva: {{ \"{section_name}\": [] }}\n"
        )
    elif section_name == "habilidades":
        prompt_base = (
            "Você é um especialista in RH. Extraia as habilidades técnicas e profissionais do currículo abaixo.\n\n"
            f"Formato: JSON com a chave '{section_name}' e lista de habilidades.\n\n"
            f"{schina_snippet}\n\n"
            "Regras:\n"
            "- Cada ihas deve ser uma habilidade única.\n"
            "- Não agrupe várias ferramentas in uma única string.\n"
            "- Idiomas não entram in habilidades."
        )
    elif section_name == "idiomas":
        prompt_base = (
            "Você é um especialista in RH. Extraia **apenas os idiomas falados ou estudados** mencionados no currículo abaixo.\n\n"
            f"Formato esperado:\n{schina_snippet}\n\n"
            "⚠️ Regras obrigatórias:\n"
            "- NÃO inclua nomes de escolas de idiomas (ex: CNA, Wizard, Fisk, etc.)\n"
            "- NÃO deduza idiomas com base in nomes de instituições, culturas ou nacionalidade\n"
            "- NÃO inclua linguagens de programação (ex: Python, Java, etc.)\n"
            f"- Se nenhum idioma for citado claramente, retorne: {{ '{section_name}': [] }}\n"
            "- Campo 'nivel' deve ser: básico, intermediário, avançado, fluente ou nativo. Use null se ausente."
        )
    else:
        prompt_base = f"{schina_snippet}\n\n{cv_text}"
    return f"{prompt_base}\n\nCurrículo:\n{cv_text}"
