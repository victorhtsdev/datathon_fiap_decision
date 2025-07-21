import type { 
  Vaga, 
  VagaDetalhada, 
  Workbook, 
  Applicant, 
  MatchProspect, 
  MatchProspectData, 
  ApplicantProspect, 
  ProspectMatchByWorkbook, 
  ProspectMatchByVaga, 
  WorkbookProspectSummary,
  SemanticPerformanceResponse,
  CacheClearResponse,
  SemanticPerformanceInfo
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log('🌐 Making fetch to:', url);
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📦 Data received:', data);
      return data;
    } catch (error) {
      console.error('🚨 Fetch error:', error);
      throw error;
    }
  }

  // Vagas
  getVagas = async (onlyActive: boolean = true): Promise<Vaga[]> => {
    const endpoint = `/vagas/lista?apenas_ativas=${onlyActive}`;
    console.log('🔄 Making request to:', `${API_BASE_URL}${endpoint}`);
    try {
      const result = await this.fetchApi<Vaga[]>(endpoint);
      console.log('✅ Data received:', result);
      return result;
    } catch (error) {
      console.error('❌ Request error:', error);
      throw error;
    }
  }

  getVagasAbertas = async (): Promise<Vaga[]> => {
    const endpoint = `/vagas/abertas`;
    console.log('🔄 Making request to:', `${API_BASE_URL}${endpoint}`);
    try {
      const result = await this.fetchApi<Vaga[]>(endpoint);
      console.log('✅ Vagas abertas received:', result);
      return result;
    } catch (error) {
      console.error('❌ Request error:', error);
      throw error;
    }
  }

  getVagaDetalhes = async (vagaId: number): Promise<VagaDetalhada> => {
    return this.fetchApi<VagaDetalhada>(`/vagas/${vagaId}`);
  }

  // Workbooks
  getWorkbooks = async (): Promise<Workbook[]> => {
    return this.fetchApi<Workbook[]>('/workbook');
  }

  createWorkbook = async (data: { vaga_id: number; criado_por?: string }): Promise<Workbook> => {
    return this.fetchApi<Workbook>('/workbook', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  getWorkbook = async (workbookId: string): Promise<Workbook> => {
    return this.fetchApi<Workbook>(`/workbook/${workbookId}`);
  }

  updateWorkbook = async (workbookId: string, data: Partial<Workbook>): Promise<Workbook> => {
    return this.fetchApi<Workbook>(`/workbook/${workbookId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  deleteWorkbook = async (workbookId: string): Promise<{ message: string }> => {
    return this.fetchApi<{ message: string }>(`/workbook/${workbookId}`, {
      method: 'DELETE',
    });
  }

  // Match Prospects
  getMatchProspects = async (workbookId: string): Promise<MatchProspect[]> => {
    return this.fetchApi<MatchProspect[]>(`/workbook/${workbookId}/match-prospects`);
  }

  updateMatchProspects = async (
    workbookId: string, 
    prospects: MatchProspectData[]
  ): Promise<{ message: string; workbook_id: string; prospects_count: number }> => {
    return this.fetchApi<{ message: string; workbook_id: string; prospects_count: number }>(
      `/workbook/${workbookId}/match-prospects`,
      {
        method: 'POST',
        body: JSON.stringify({ prospects }),
      }
    );
  }

  // Applicants
  getApplicantsByIds = async (applicantIds: number[]): Promise<Applicant[]> => {
    return this.fetchApi<Applicant[]>('/get_applicants_by_ids', {
      method: 'POST',
      body: JSON.stringify({ applicant_ids: applicantIds }),
    });
  }

  // Chat
  sendChatMessage = async (
    message: string, 
    workbookId?: string, 
    context?: string,
    sessionId?: string
  ): Promise<{ 
    response: string; 
    session_id?: string;
    filtered_candidates?: Applicant[]; 
    total_candidates?: number 
  }> => {
    return this.fetchApi<{ 
      response: string; 
      session_id?: string;
      filtered_candidates?: Applicant[]; 
      total_candidates?: number 
    }>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        workbook_id: workbookId,
        context,
        session_id: sessionId
      }),
    });
  }

  // Prospects Match
  getProspectsByWorkbook = async (workbookId: string): Promise<ProspectMatchByWorkbook> => {
    return this.fetchApi<ProspectMatchByWorkbook>(`/prospects-match/by-workbook/${workbookId}`);
  }

  getProspectsByVaga = async (vagaId: number): Promise<ProspectMatchByVaga> => {
    return this.fetchApi<ProspectMatchByVaga>(`/prospects-match/by-vaga/${vagaId}`);
  }

  searchProspectsByName = async (name: string, limit: number = 50): Promise<ApplicantProspect[]> => {
    return this.fetchApi<ApplicantProspect[]>(`/prospects-match/search/by-name?name=${encodeURIComponent(name)}&limit=${limit}`);
  }

  getWorkbooksWithProspectsSummary = async (): Promise<{ total_workbooks: number; workbooks: WorkbookProspectSummary[] }> => {
    return this.fetchApi<{ total_workbooks: number; workbooks: WorkbookProspectSummary[] }>('/prospects-match/workbooks/summary');
  }

  // Análise de Performance Semântica
  getSemanticPerformanceAnalysis = async (): Promise<SemanticPerformanceResponse> => {
    return this.fetchApi<SemanticPerformanceResponse>('/api/analytics/semantic-performance');
  }

  clearSemanticPerformanceCache = async (): Promise<CacheClearResponse> => {
    return this.fetchApi<CacheClearResponse>('/api/analytics/semantic-performance/cache', {
      method: 'DELETE',
    });
  }

  getSemanticPerformanceInfo = async (): Promise<SemanticPerformanceInfo> => {
    return this.fetchApi<SemanticPerformanceInfo>('/api/analytics/semantic-performance/info');
  }
}

// Criar uma instância e exportar como padrão
const apiServiceInstance = new ApiService();
export const apiService = apiServiceInstance;
export default apiServiceInstance;
