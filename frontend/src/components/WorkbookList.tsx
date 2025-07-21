import { useQuery } from '@tanstack/react-query';
import { Plus, FileText, Calendar, User, Settings, Activity, ArrowRight, Search, Filter } from 'lucide-react';
import { useState, useMemo } from 'react';
import { apiService } from '../services/api';
import type { Workbook } from '../types/api';

interface WorkbookListProps {
  onCreateNew: () => void;
  onWorkbookSelect: (workbook: Workbook) => void;
}

export function WorkbookList({ onCreateNew, onWorkbookSelect }: WorkbookListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterVagaId, setFilterVagaId] = useState('');

  const {
    data: workbooks = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['workbooks'],
    queryFn: () => apiService.getWorkbooks(),
    staleTime: 2 * 60 * 1000, // 2 minutos 
    refetchOnWindowFocus: true, // Recarrega quando volta para a aba
    refetchOnMount: true, // Recarrega quando componente monta
  });

  // Filtrar e ordenar workbooks
  const filteredAndSortedWorkbooks = useMemo(() => {
    let filtered = workbooks;

    // Aplicar filtros
    if (searchTerm || filterVagaId) {
      filtered = workbooks.filter((workbook) => {
        const matchesSearch = searchTerm === '' || 
          (workbook.vaga_titulo && workbook.vaga_titulo.toLowerCase().includes(searchTerm.toLowerCase()));
        
        const matchesVagaId = filterVagaId === '' || 
          workbook.vaga_id.toString().includes(filterVagaId);
        
        return matchesSearch && matchesVagaId;
      });
    }

    // Ordenar por status (abertos primeiro) e depois por timestamp decrescente
    return filtered.sort((a, b) => {
      // Primeiro, priorizar workbooks abertos
      if (a.status === 'aberto' && b.status !== 'aberto') return -1;
      if (a.status !== 'aberto' && b.status === 'aberto') return 1;
      
      // Dentro do mesmo status, ordenar por data decrescente (mais recentes primeiro)
      const dateA = new Date(a.criado_em || '').getTime();
      const dateB = new Date(b.criado_em || '').getTime();
      return dateB - dateA; // Ordem decrescente
    });
  }, [workbooks, searchTerm, filterVagaId]);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Carregando seus workbooks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-10 h-10 text-red-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Ops! Algo deu errado</h3>
          <p className="text-gray-600 mb-6">Não conseguimos carregar seus workbooks.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  // Estado vazio - nenhum workbook
  if (workbooks.length === 0) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="text-center max-w-lg">
          <div className="w-32 h-32 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-8">
            <FileText className="w-16 h-16 text-blue-600" />
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Bem-vindo ao DataThon Decision! 👋
          </h2>
          
          <p className="text-gray-600 text-lg mb-8 leading-relaxed">
            Você ainda não tem nenhum workbook. <br />
            Comece criando seu primeiro para analisar candidatos e fazer matching inteligente com suas vagas.
          </p>
          
          <button
            onClick={onCreateNew}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 rounded-xl font-semibold text-lg flex items-center gap-3 mx-auto transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            <Plus className="w-6 h-6" />
            Criar Meu Primeiro Workbook
            <ArrowRight className="w-5 h-5" />
          </button>
          
          <div className="mt-8 grid grid-cols-3 gap-4 max-w-md mx-auto">
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <User className="w-6 h-6 text-green-600" />
              </div>
              <p className="text-sm text-gray-600">Analise candidatos</p>
            </div>
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
              <p className="text-sm text-gray-600">Matching inteligente</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Lista de workbooks
  return (
    <div className="flex gap-8">
      {/* Área principal - Lista de workbooks */}
      <div className="flex-1">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Seus Workbooks</h2>
          <p className="text-gray-600">
            {filteredAndSortedWorkbooks.length} de {workbooks.length} workbook{workbooks.length !== 1 ? 's' : ''} 
            {filteredAndSortedWorkbooks.length !== workbooks.length ? ' (filtrado' + (filteredAndSortedWorkbooks.length !== 1 ? 's' : '') + ')' : ''}
          </p>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <h3 className="font-semibold text-gray-900">Filtros</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Buscar por nome da vaga
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  id="search"
                  placeholder="Digite o nome da vaga..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="vagaId" className="block text-sm font-medium text-gray-700 mb-2">
                Filtrar por ID da vaga
              </label>
              <input
                type="text"
                id="vagaId"
                placeholder="Digite o ID da vaga..."
                value={filterVagaId}
                onChange={(e) => setFilterVagaId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </div>
          
          {(searchTerm || filterVagaId) && (
            <div className="mt-4 flex items-center gap-2">
              <span className="text-sm text-gray-600">Filtros ativos:</span>
              {searchTerm && (
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  Nome: "{searchTerm}"
                </span>
              )}
              {filterVagaId && (
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  ID: {filterVagaId}
                </span>
              )}
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterVagaId('');
                }}
                className="text-sm text-gray-500 hover:text-gray-700 underline ml-2"
              >
                Limpar filtros
              </button>
            </div>
          )}
        </div>

        <div className="grid gap-6">
          {filteredAndSortedWorkbooks.map((workbook) => (
            <div
              key={workbook.id}
              className="bg-white rounded-2xl border border-gray-200 p-8 hover:shadow-lg transition-all duration-300 hover:border-blue-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-4 h-4 rounded-full ${
                      workbook.status === 'fechado' ? 'bg-gray-400' : 'bg-green-500 animate-pulse'
                    }`}></div>
                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                      Workbook #{workbook.id.toString().slice(0, 8)}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      workbook.status === 'fechado' 
                        ? 'bg-gray-100 text-gray-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {workbook.status === 'fechado' ? 'Encerrado' : 'Ativo'}
                    </span>
                  </div>
                  
                  {/* Título da vaga */}
                  {workbook.vaga_titulo && (
                    <div className="mb-4">
                      <p className="text-gray-600 font-medium text-lg">
                        📋 {workbook.vaga_titulo}
                      </p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-3 gap-6 mb-6">
                    <div className="flex items-center gap-3">
                      <User className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm text-gray-500">Criado por</p>
                        <p className="font-medium text-gray-900">{workbook.criado_por || 'Sistema'}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Calendar className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="text-sm text-gray-500">Data de criação</p>
                        <p className="font-medium text-gray-900">
                          {workbook.criado_em 
                            ? new Date(workbook.criado_em).toLocaleDateString('pt-BR')
                            : 'Não informado'
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Activity className="w-5 h-5 text-purple-500" />
                      <div>
                        <p className="text-sm text-gray-500">Vaga ID</p>
                        <p className="font-medium text-gray-900">#{workbook.vaga_id}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <button 
                  onClick={() => onWorkbookSelect(workbook)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium flex items-center gap-2"
                >
                  Ver Detalhes
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          
          {/* Mensagem quando não há resultados após filtrar */}
          {filteredAndSortedWorkbooks.length === 0 && workbooks.length > 0 && (searchTerm || filterVagaId) && (
            <div className="text-center py-12 bg-white rounded-2xl border border-gray-200">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhum workbook encontrado</h3>
              <p className="text-gray-600 mb-4">
                Não encontramos workbooks que correspondam aos filtros aplicados.
              </p>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterVagaId('');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
              >
                Limpar filtros
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar de ações */}
      <div className="w-80">
        <div className="sticky top-8 space-y-6">
          {/* Card de ações principais */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Ações Rápidas
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={onCreateNew}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white p-4 rounded-xl font-medium transition-all duration-200 flex items-center gap-3 group"
              >
                <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                <div className="text-left">
                  <div className="font-semibold">Novo Workbook</div>
                  <div className="text-xs text-blue-100">Analisar candidatos</div>
                </div>
              </button>
            </div>
          </div>

          {/* Card de estatísticas */}
          {workbooks.length > 0 && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-6">
              <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                Estatísticas
              </h4>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total de workbooks</span>
                  <span className="text-2xl font-bold text-blue-600">{workbooks.length}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Ativos</span>
                  <span className="text-2xl font-bold text-green-600">{workbooks.length}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
