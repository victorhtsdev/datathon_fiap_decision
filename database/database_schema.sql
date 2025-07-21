-- Database Schema for Datathon Decision

-- public.applicants definition
-- Drop table if exists
DROP TABLE IF EXISTS public.applicants;

CREATE TABLE public.applicants (
    id BIGINT NULL,
    infos_basicas_telefone_recado TEXT NULL,
    infos_basicas_telefone TEXT NULL,
    infos_basicas_objetivo_profissional TEXT NULL,
    infos_basicas_data_criacao TEXT NULL,
    infos_basicas_inserido_por TEXT NULL,
    infos_basicas_email TEXT NULL,
    infos_basicas_local TEXT NULL,
    infos_basicas_sabendo_de_nos_por TEXT NULL,
    infos_basicas_data_atualizacao TEXT NULL,
    infos_basicas_codigo_profissional TEXT NULL,
    infos_basicas_nome TEXT NULL,
    informacoes_pessoais_data_aceite TEXT NULL,
    informacoes_pessoais_nome TEXT NULL,
    informacoes_pessoais_cpf TEXT NULL,
    informacoes_pessoais_fonte_indicacao TEXT NULL,
    informacoes_pessoais_email TEXT NULL,
    informacoes_pessoais_email_secundario TEXT NULL,
    informacoes_pessoais_data_nascimento TEXT NULL,
    informacoes_pessoais_telefone_celular TEXT NULL,
    informacoes_pessoais_telefone_recado TEXT NULL,
    informacoes_pessoais_sexo TEXT NULL,
    informacoes_pessoais_estado_civil TEXT NULL,
    informacoes_pessoais_pcd TEXT NULL,
    informacoes_pessoais_endereco TEXT NULL,
    informacoes_pessoais_skype TEXT NULL,
    informacoes_pessoais_url_linkedin TEXT NULL,
    informacoes_pessoais_facebook TEXT NULL,
    informacoes_profissionais_titulo_profissional TEXT NULL,
    informacoes_profissionais_area_atuacao TEXT NULL,
    informacoes_profissionais_conhecimentos_tecnicos TEXT NULL,
    informacoes_profissionais_certificacoes TEXT NULL,
    informacoes_profissionais_outras_certificacoes TEXT NULL,
    informacoes_profissionais_remuneracao TEXT NULL,
    informacoes_profissionais_nivel_profissional TEXT NULL,
    formacao_e_idiomas_nivel_academico TEXT NULL,
    formacao_e_idiomas_nivel_ingles TEXT NULL,
    formacao_e_idiomas_nivel_espanhol TEXT NULL,
    formacao_e_idiomas_outro_idioma TEXT NULL,
    cv_pt TEXT NULL,
    cv_en TEXT NULL,
    formacao_e_idiomas_instituicao_ensino_superior TEXT NULL,
    formacao_e_idiomas_cursos TEXT NULL,
    formacao_e_idiomas_ano_conclusao TEXT NULL,
    informacoes_pessoais_download_cv TEXT NULL,
    informacoes_profissionais_qualificacoes TEXT NULL,
    informacoes_profissionais_experiencias TEXT NULL,
    formacao_e_idiomas_outro_curso TEXT NULL,
    cargo_atual_id_ibrati TEXT NULL,
    cargo_atual_email_corporativo TEXT NULL,
    cargo_atual_cargo_atual TEXT NULL,
    cargo_atual_projeto_atual TEXT NULL,
    cargo_atual_cliente TEXT NULL,
    cargo_atual_unidade TEXT NULL,
    cargo_atual_data_admissao TEXT NULL,
    cargo_atual_data_ultima_promocao TEXT NULL,
    cargo_atual_nome_superior_imediato TEXT NULL,
    cargo_atual_email_superior_imediato TEXT NULL
);

-- public.match_prospects definition
DROP TABLE IF EXISTS public.match_prospects;

CREATE TABLE public.match_prospects (
    workbook_id UUID NOT NULL,
    applicant_id BIGINT NOT NULL,
    score_semantico DOUBLE PRECISION NULL,
    origem TEXT NULL,
    selecionado BOOLEAN NULL DEFAULT FALSE,
    data_entrada TIMESTAMP NULL DEFAULT NOW(),
    observacoes TEXT NULL,
    CONSTRAINT uq_workbook_match UNIQUE (workbook_id, applicant_id)
);

-- public.processed_applicants definition
DROP TABLE IF EXISTS public.processed_applicants;

CREATE TABLE public.processed_applicants (
    id BIGINT NOT NULL,
    data_aceite TEXT NULL,
    nome TEXT NULL,
    cpf TEXT NULL,
    fonte_indicacao TEXT NULL,
    email TEXT NULL,
    email_secundario TEXT NULL,
    data_nascimento TEXT NULL,
    telefone_celular TEXT NULL,
    telefone_recado TEXT NULL,
    sexo TEXT NULL,
    estado_civil TEXT NULL,
    pcd TEXT NULL,
    endereco TEXT NULL,
    skype TEXT NULL,
    url_linkedin TEXT NULL,
    facebook TEXT NULL,
    download_cv TEXT NULL,
    cv_pt_json JSONB NULL,
    cv_texto_semantico TEXT NULL,
    cv_embedding BYTEA NULL,
    nivel_maximo_formacao TEXT NULL,
    cv_embedding_vector PUBLIC.vector NULL,
    updated_at TIMESTAMP NULL,
    CONSTRAINT processed_applicants_pkey PRIMARY KEY (id)
);

-- public.prospects definition
DROP TABLE IF EXISTS public.prospects;

CREATE TABLE public.prospects (
    vaga_id BIGINT NULL,
    titulo TEXT NULL,
    modalidade TEXT NULL,
    nome TEXT NULL,
    codigo TEXT NULL,
    situacao_candidado TEXT NULL,
    data_candidatura TEXT NULL,
    ultima_atualizacao TEXT NULL,
    comentario TEXT NULL,
    recrutador TEXT NULL
);

-- public.vagas definition
DROP TABLE IF EXISTS public.vagas;

CREATE TABLE public.vagas (
    id BIGINT NULL,
    informacoes_basicas_data_requicisao TEXT NULL,
    informacoes_basicas_limite_esperado_para_contratacao TEXT NULL,
    informacoes_basicas_titulo_vaga TEXT NULL,
    informacoes_basicas_vaga_sap TEXT NULL,
    informacoes_basicas_cliente TEXT NULL,
    informacoes_basicas_solicitante_cliente TEXT NULL,
    informacoes_basicas_empresa_divisao TEXT NULL,
    informacoes_basicas_requisitante TEXT NULL,
    informacoes_basicas_analista_responsavel TEXT NULL,
    informacoes_basicas_tipo_contratacao TEXT NULL,
    informacoes_basicas_prazo_contratacao TEXT NULL,
    informacoes_basicas_objetivo_vaga TEXT NULL,
    informacoes_basicas_prioridade_vaga TEXT NULL,
    informacoes_basicas_origem_vaga TEXT NULL,
    informacoes_basicas_superior_imediato TEXT NULL,
    informacoes_basicas_nome TEXT NULL,
    informacoes_basicas_telefone TEXT NULL,
    perfil_vaga_pais TEXT NULL,
    perfil_vaga_estado TEXT NULL,
    perfil_vaga_cidade TEXT NULL,
    perfil_vaga_bairro TEXT NULL,
    perfil_vaga_regiao TEXT NULL,
    perfil_vaga_local_trabalho TEXT NULL,
    perfil_vaga_vaga_especifica_para_pcd TEXT NULL,
    perfil_vaga_faixa_etaria TEXT NULL,
    perfil_vaga_horario_trabalho TEXT NULL,
    perfil_vaga_nivel_profissional TEXT NULL,
    perfil_vaga_nivel_academico TEXT NULL,
    perfil_vaga_nivel_ingles TEXT NULL,
    perfil_vaga_nivel_espanhol TEXT NULL,
    perfil_vaga_outro_idioma TEXT NULL,
    perfil_vaga_areas_atuacao TEXT NULL,
    perfil_vaga_principais_atividades TEXT NULL,
    perfil_vaga_competencia_tecnicas_e_comportamentais TEXT NULL,
    perfil_vaga_demais_observacoes TEXT NULL,
    perfil_vaga_viagens_requeridas TEXT NULL,
    perfil_vaga_equipamentos_necessarios TEXT NULL,
    beneficios_valor_venda TEXT NULL,
    beneficios_valor_compra_1 TEXT NULL,
    beneficios_valor_compra_2 TEXT NULL,
    informacoes_basicas_data_inicial TEXT NULL,
    informacoes_basicas_data_final TEXT NULL,
    perfil_vaga_habilidades_comportamentais_necessarias TEXT NULL,
    informacoes_basicas_nome_substituto TEXT NULL,
    vaga_texto_semantico TEXT NULL,
    vaga_embedding BYTEA NULL,
    vaga_embedding_vector PUBLIC.vector NULL,
    updated_at TIMESTAMP NULL,
    status_vaga TEXT NOT NULL DEFAULT 'nao_iniciada',
    CONSTRAINT vagas_status_vaga_check CHECK
      (status_vaga IN ('nao_iniciada','aberta','em_andamento','fechada'))
);

-- public.workbook definition
DROP TABLE IF EXISTS public.workbook;

CREATE TABLE public.workbook (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    vaga_id BIGINT NOT NULL,
    criado_em TIMESTAMP NULL DEFAULT NOW(),
    fechado_em TIMESTAMP NULL,
    status TEXT NULL DEFAULT 'aberto',
    criado_por TEXT NULL,
    CONSTRAINT workbook_pkey PRIMARY KEY (id)
);
