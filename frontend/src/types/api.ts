export type StatusVaga = 'nao_iniciada' | 'aberta' | 'em_andamento' | 'em_analise' | 'pausada' | 'finalizada' | 'cancelada';

export interface Vaga {
  id: number;
  informacoes_basicas_titulo_vaga: string;
  status_vaga: StatusVaga;
}

export interface VagaDetalhada extends Vaga {
  informacoes_basicas_data_requicisao?: string;
  informacoes_basicas_limite_esperado_para_contratacao?: string;
  informacoes_basicas_vaga_sap?: string;
  informacoes_basicas_cliente?: string;
  informacoes_basicas_solicitante_cliente?: string;
  informacoes_basicas_empresa_divisao?: string;
  informacoes_basicas_requisitante?: string;
  informacoes_basicas_analista_responsavel?: string;
  informacoes_basicas_tipo_contratacao?: string;
  informacoes_basicas_prazo_contratacao?: string;
  informacoes_basicas_objetivo_vaga?: string;
  informacoes_basicas_prioridade_vaga?: string;
  informacoes_basicas_origem_vaga?: string;
  informacoes_basicas_superior_imediato?: string;
  informacoes_basicas_nome?: string;
  informacoes_basicas_telefone?: string;
  perfil_vaga_pais?: string;
  perfil_vaga_estado?: string;
  perfil_vaga_cidade?: string;
  perfil_vaga_bairro?: string;
  perfil_vaga_regiao?: string;
  perfil_vaga_local_trabalho?: string;
  perfil_vaga_vaga_especifica_para_pcd?: string;
  perfil_vaga_faixa_etaria?: string;
  perfil_vaga_horario_trabalho?: string;
  perfil_vaga_nivel_profissional?: string;
  perfil_vaga_nivel_academico?: string;
  perfil_vaga_nivel_ingles?: string;
  perfil_vaga_nivel_espanhol?: string;
  perfil_vaga_outro_idioma?: string;
  perfil_vaga_areas_atuacao?: string;
  perfil_vaga_principais_atividades?: string;
  perfil_vaga_competencia_tecnicas_e_comportamentais?: string;
  perfil_vaga_demais_observacoes?: string;
  perfil_vaga_viagens_requeridas?: string;
  perfil_vaga_equipamentos_necessarios?: string;
  beneficios_valor_venda?: string;
  beneficios_valor_compra_1?: string;
  beneficios_valor_compra_2?: string;
  informacoes_basicas_data_inicial?: string;
  informacoes_basicas_data_final?: string;
  perfil_vaga_habilidades_comportamentais_necessarias?: string;
  informacoes_basicas_nome_substituto?: string;
  vaga_texto_semantico?: string;
  updated_at?: string;
}

export interface Workbook {
  id: string;
  vaga_id: number;
  criado_por?: string;
  criado_em?: string;
  fechado_em?: string;
  status?: 'aberto' | 'fechado' | 'em_andamento';
  // Campos calculados que podem vir do backend
  vaga_titulo?: string;
  total_prospects?: number;
  name?: string;
  description?: string;
}

export interface Formacao {
  curso: string;
  nivel: string;
  ano_fim: string;
  ano_inicio: string;
  instituicao?: string;
  observacoes?: string;
}

export interface Idioma {
  idioma: string;
  nivel: string;
}

export interface Experiencia {
  fim: string;
  cargo: string;
  inicio: string;
  empresa: string;
  descricao: string;
}

export interface CvPt {
  idiomas: Idioma[];
  formacoes: Formacao[];
  habilidades: string[];
  experiencias: Experiencia[];
}

export interface Applicant {
  id: number;
  data_aceite?: string;
  nome: string;
  cpf: string;
  fonte_indicacao?: string;
  email: string;
  email_secundario?: string;
  data_nascimento?: string;
  telefone_celular?: string;
  telefone_recado?: string;
  sexo: string;
  estado_civil: string;
  pcd?: string;
  endereco?: string;
  skype?: string;
  url_linkedin?: string;
  facebook?: string;
  download_cv?: string;
  nivel_maximo_formacao: string;
  updated_at: string;
  cv_pt: CvPt;
  score_semantico?: number;  // Pontuação semântica para busca por filtros
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  applicants?: Applicant[];
  filtered_candidates?: Applicant[];  // Candidatos filtrados pela IA
  total_candidates?: number;          // Total de candidatos encontrados
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
