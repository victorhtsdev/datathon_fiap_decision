import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, ArrowLeft, CheckCircle } from 'lucide-react';
import { Vaga } from '../types/api';
import { apiService } from '../services/api';

interface VagaSelectorProps {
  onVagaSelect: (vaga: Vaga) => void;
  onBack: () => void;
  selectedVaga?: Vaga;
  isCreating?: boolean;
}

const VagaSelector: React.FC<VagaSelectorProps> = ({ 
  onVagaSelect, 
  onBack, 
  selectedVaga,
  isCreating = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const {
    data: vagas = [],
    isLoading: loading,
    error,
  } = useQuery({
    queryKey: ['vagas'],
    queryFn: () => apiService.getVagas(),
    staleTime: 1 * 60 * 1000, // 1 minuto (dados de vagas podem mudar frequentemente)
    refetchOnWindowFocus: true, // Recarrega quando volta para a aba
    refetchOnMount: true, // Recarrega quando componente monta
  });

  const filteredVagas = vagas.filter(vaga => {
    const matchesSearch = vaga.informacoes_basicas_titulo_vaga.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'aberta': return 'bg-green-100 text-green-800';
      case 'em_andamento': return 'bg-blue-100 text-blue-800';
      case 'em_analise': return 'bg-yellow-100 text-yellow-800';
      case 'pausada': return 'bg-orange-100 text-orange-800';
      case 'finalizada': return 'bg-gray-100 text-gray-800';
      case 'cancelada': return 'bg-red-100 text-red-800';
      case 'nao_iniciada': return 'bg-gray-100 text-gray-600';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'nao_iniciada': return 'Não Iniciada';
      case 'aberta': return 'Aberta';
      case 'em_andamento': return 'Em Andamento';
      case 'em_analise': return 'Em Análise';
      case 'pausada': return 'Pausada';
      case 'finalizada': return 'Finalizada';
      case 'cancelada': return 'Cancelada';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-8">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Voltar
            </button>
            <h1 className="text-3xl font-bold text-gray-800">Selecionar Vaga</h1>
          </div>
          
          <div className="flex justify-center items-center py-32">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-8">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Voltar
            </button>
            <h1 className="text-3xl font-bold text-gray-800">Selecionar Vaga</h1>
          </div>
          
          <div className="text-center py-32">
            <div className="text-red-600 text-xl mb-4">{error?.message || 'Erro desconhecido'}</div>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tentar Novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Voltar
          </button>
          <h1 className="text-3xl font-bold text-gray-800">Selecionar Vaga</h1>
          {selectedVaga && (
            <div className="flex items-center gap-2 ml-auto">
              {isCreating ? (
                <>
                  <div className="w-4 h-4 border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                  <span className="text-blue-600 font-medium">
                    Criando workbook para: {selectedVaga.informacoes_basicas_titulo_vaga}
                  </span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-600 font-medium">
                    Vaga selecionada: {selectedVaga.informacoes_basicas_titulo_vaga}
                  </span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="max-w-md">
            {/* Busca */}
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar vagas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Lista de Vagas */}
        {filteredVagas.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-gray-500 text-lg mb-4">
              {searchTerm 
                ? 'Nenhuma vaga encontrada com o termo de busca.'
                : 'Nenhuma vaga cadastrada no sistema.'
              }
            </div>
            {searchTerm && (
              <button
                onClick={() => {
                  setSearchTerm('');
                }}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Limpar Busca
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredVagas.map((vaga) => (            <div
              key={vaga.id}
              className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-all border-2 ${
                selectedVaga?.id === vaga.id 
                  ? 'border-blue-500 ring-2 ring-blue-200' 
                  : 'border-transparent hover:border-blue-200'
              } ${
                isCreating ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
              }`}
              onClick={() => !isCreating && onVagaSelect(vaga)}
            >
                <div className="p-6">
                  {/* Header da Vaga */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-800 mb-2">
                        {vaga.informacoes_basicas_titulo_vaga}
                      </h3>
                      <p className="text-gray-600 font-medium">ID: {vaga.id}</p>
                    </div>
                    {selectedVaga?.id === vaga.id && (
                      <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 ml-4" />
                    )}
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(vaga.status_vaga)}`}>
                      {getStatusDisplay(vaga.status_vaga)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Resultados */}
        {filteredVagas.length > 0 && (
          <div className="mt-6 text-center text-gray-600">
            Mostrando {filteredVagas.length} de {vagas.length} vagas
          </div>
        )}
      </div>
    </div>
  );
};

export { VagaSelector };
export default VagaSelector;
