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
  selecionado?: boolean;     // Indicador se foi selecionado manualmente
}

export interface MatchProspect {
  workbook_id: string;
  applicant_id: number;
  score_semantico: number;
  origem: string;
  selecionado: boolean;
  data_entrada: string;
  observacoes?: string;
}

export interface MatchProspectData {
  applicant_id: number;
  score_semantico?: number;
  origem?: string;
  selecionado?: boolean;
  observacoes?: string;
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

// Tipos para consulta de processed_applicants via match_prospects
export interface ApplicantProspect {
  // Dados do match_prospect
  workbook_id: string;
  applicant_id: number;
  score_semantico?: number;
  origem?: string;
  selecionado?: boolean;
  data_entrada?: string;
  observacoes?: string;
  
  // Dados do processed_applicant
  nome?: string;
  email?: string;
  cpf?: string;
  telefone_celular?: string;
  nivel_maximo_formacao?: string;
  cv_pt?: CvPt;
  updated_at?: string;
}

export interface ProspectMatchByWorkbook {
  workbook_id: string;
  vaga_id: number;
  vaga_titulo?: string;
  prospects: ApplicantProspect[];
  total_prospects: number;
}

export interface ProspectMatchByVaga {
  vaga_id: number;
  vaga_titulo?: string;
  workbooks: ProspectMatchByWorkbook[];
  total_prospects: number;
}

export interface WorkbookProspectSummary {
  workbook_id: string;
  vaga_id: number;
  vaga_titulo?: string;
  total_prospects: number;
}

// Análise de Performance Semântica
export interface TopPositionStats {
  quantidade: number;
  percentual: number;
}

export interface MetricasGerais {
  total_aprovados: number;
  media_posicao: number;
  mediana_posicao: number;
  desvio_padrao: number;
  vagas_analisadas: number;
  vagas_com_ranking_semantico: number;
}

export interface HistogramPoint {
  posicao: number;
  quantidade: number;
}

export interface StatusDistribution {
  status: string;
  quantidade: number;
}

export interface InterpretacaoEstruturada {
  titulo: string;
  visao_geral: {
    total_candidatos: {
      valor: number;
      descricao: string;
    };
    objetivo: string;
  };
  metricas_precisao: Array<{
    label: string;
    valor: string;
    tipo?: string;
    descricao?: string;
  }>;
  analise_detalhada: Array<{
    categoria: string;
    quantidade: number;
    percentual: number;
    interpretacao: string;
    cor: string;
  }>;
  conclusao: {
    nivel_precisao: string;
    cor: string;
    texto: string;
    recomendacao: string;
  };
}

export interface SemanticPerformanceResponse {
  metricas_gerais: MetricasGerais;
  distribuicao_top_positions: Record<string, TopPositionStats>;
  histogram_data: HistogramPoint[];
  status_distribution: StatusDistribution[];
  pgvector_info: {
    operador_usado: string;
    tipo_distancia: string;
    interpretacao: string;
    range_tipico: string;
    ordenacao: string;
  };
  mensagem_interpretacao: string;
  interpretacao_estruturada: InterpretacaoEstruturada;
  generated_at: string;
}

export interface CacheClearResponse {
  success: boolean;
  message: string;
}

export interface SemanticPerformanceInfo {
  titulo: string;
  descricao: string;
  metodologia: Record<string, string>;
  metricas_principais: string[];
  tecnologia: Record<string, string>;
  cache: Record<string, string>;
}
