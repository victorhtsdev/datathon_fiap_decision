import { useQuery } from '@tanstack/react-query';
import { Plus, FileText, Calendar, User, Settings, Activity, ArrowRight } from 'lucide-react';
import { apiService } from '../services/api';
import type { Workbook } from '../types/api';

interface WorkbookListProps {
  onCreateNew: () => void;
  onWorkbookSelect: (workbook: Workbook) => void;
}

export function WorkbookList({ onCreateNew, onWorkbookSelect }: WorkbookListProps) {
  const {
    data: workbooks = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['workbooks'],
    queryFn: () => apiService.getWorkbooks(),
  });

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
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <FileText className="w-6 h-6 text-orange-600" />
              </div>
              <p className="text-sm text-gray-600">Relatórios detalhados</p>
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
            {workbooks.length} workbook{workbooks.length !== 1 ? 's' : ''} criado{workbooks.length !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="grid gap-6">
          {workbooks.map((workbook) => (
            <div
              key={workbook.id}
              className="bg-white rounded-2xl border border-gray-200 p-8 hover:shadow-lg transition-all duration-300 hover:border-blue-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                      Workbook #{workbook.id.toString().slice(0, 8)}
                    </h3>
                    <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                      Ativo
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
              
              <button 
                disabled
                className="w-full bg-gray-100 text-gray-400 p-4 rounded-xl font-medium cursor-not-allowed flex items-center gap-3"
              >
                <FileText className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-semibold">Relatórios</div>
                  <div className="text-xs">Em breve</div>
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
