import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  Target, 
  Users, 
  RefreshCw, 
  Info, 
  AlertCircle, 
  CheckCircle,
  Zap
} from 'lucide-react';
import { apiService } from '../services/api';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

export function SemanticPerformanceAnalysis() {
  const [showInfo, setShowInfo] = useState(false);
  const [showRefreshConfirm, setShowRefreshConfirm] = useState(false);
  const queryClient = useQueryClient();

  // Query para buscar dados de performance
  const { 
    data: performanceData, 
    isLoading, 
    isFetching,
    error, 
    refetch 
  } = useQuery({
    queryKey: ['semantic-performance'],
    queryFn: () => apiService.getSemanticPerformanceAnalysis(),
    staleTime: 5 * 60 * 1000, // 5 minutos (reduzido de 30min)
    gcTime: 10 * 60 * 1000, // 10 minutos em cache (garbage collection time)
    retry: 2,
    refetchOnWindowFocus: true, // Recarrega quando volta para a aba
    refetchOnMount: true, // Recarrega quando componente monta
    refetchInterval: 10 * 60 * 1000, // Recarrega a cada 10 minutos automaticamente
    // Sem timeout durante o loading para permitir cálculos longos
  });

  // Query para buscar informações sobre a análise
  const { data: infoData } = useQuery({
    queryKey: ['semantic-performance-info'],
    queryFn: () => apiService.getSemanticPerformanceInfo(),
    staleTime: 60 * 60 * 1000, // 1 hora
  });

  // Mutation para limpar cache
  const clearCacheMutation = useMutation({
    mutationFn: () => apiService.clearSemanticPerformanceCache(),
    onSuccess: () => {
      // Remove os dados do cache para forçar nova busca
      queryClient.removeQueries({ queryKey: ['semantic-performance'] });
    },
  });

  const handleRefresh = async () => {
    try {
      // Limpa o cache no backend
      await clearCacheMutation.mutateAsync();
      // Remove dados do cache do React Query para garantir nova busca
      queryClient.removeQueries({ queryKey: ['semantic-performance'] });
      // Força uma nova busca (que irá mostrar loading via isFetching)
      refetch();
      // Fecha o modal
      setShowRefreshConfirm(false);
    } catch (error) {
      console.error('Erro ao atualizar dados:', error);
      // Mesmo com erro, força refetch
      queryClient.removeQueries({ queryKey: ['semantic-performance'] });
      refetch();
      setShowRefreshConfirm(false);
    }
  };

  if (isLoading || isFetching) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center max-w-md">
          <RefreshCw className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            Analisando Performance Semântica
          </h3>
          <p className="text-gray-600 mb-4">
            Processando dados de candidatos aprovados e calculando métricas de precisão...
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
            <p className="text-sm text-blue-800 mb-2">
              <strong>⏱️ Esta operação pode levar alguns minutos</strong>
            </p>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• Analisando vagas com candidatos aprovados</li>
              <li>• Calculando similaridade semântica com pgvector</li>
              <li>• Gerando métricas e interpretações</li>
            </ul>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Por favor, aguarde sem fechar a página...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-red-600" />
          <h3 className="text-lg font-semibold text-red-900">Erro ao carregar dados</h3>
        </div>
        <p className="text-red-700 mb-4">
          Não foi possível carregar a análise de performance semântica.
        </p>
        <button
          onClick={handleRefresh}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (!performanceData) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <Info className="w-6 h-6 text-yellow-600" />
          <p className="text-yellow-800">Nenhum dado de performance disponível.</p>
        </div>
      </div>
    );
  }

  // Preparar dados para gráficos
  const topPositionsData = Object.entries(performanceData.distribuicao_top_positions).map(([key, value]) => ({
    name: key.replace('top_', 'Top '),
    quantidade: value.quantidade,
    percentual: value.percentual,
  }));

  const histogramData = performanceData.histogram_data; // Mostrar todas as posições

  // Calcular percentuais para o gráfico de status
  const totalCandidatos = performanceData.status_distribution.reduce((acc, item) => acc + item.quantidade, 0);
  const statusData = performanceData.status_distribution.map((item, index) => ({
    ...item,
    percentual: totalCandidatos > 0 ? ((item.quantidade / totalCandidatos) * 100).toFixed(1) : 0,
    color: COLORS[index % COLORS.length],
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-white bg-opacity-20 p-3 rounded-lg">
              <TrendingUp className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Análise de Performance Semântica</h1>
              <p className="text-blue-100 mt-1">
                Eficácia do algoritmo de matching baseado em pgvector
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors"
              title="Informações sobre a análise"
            >
              <Info className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowRefreshConfirm(true)}
              disabled={isLoading || isFetching || clearCacheMutation.isPending}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors disabled:opacity-50"
              title="Atualizar dados (limpa cache e recalcula)"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading || isFetching || clearCacheMutation.isPending ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Info Panel */}
      {showInfo && infoData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Como funciona esta análise</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Metodologia</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                {Object.entries(infoData.metodologia).map(([key, value]) => (
                  <li key={key}>• {value}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Tecnologia</h4>
              <div className="text-sm text-blue-700 space-y-1">
                <p><strong>Operador:</strong> {infoData.tecnologia.operador}</p>
                <p><strong>Base de dados:</strong> {infoData.tecnologia.base_dados}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Total Aprovados</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData.metricas_gerais.total_aprovados.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <Target className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Média de Posição</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData.metricas_gerais.media_posicao.toFixed(1)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 text-yellow-600" />
            <div>
              <p className="text-sm text-gray-600">Mediana</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData.metricas_gerais.mediana_posicao}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Top 1</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData.distribuicao_top_positions.top_1?.percentual.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-indigo-600" />
            <div>
              <p className="text-sm text-gray-600">Vagas Analisadas</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData.metricas_gerais.vagas_analisadas}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Positions */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribuição por Top Positions
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topPositionsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [`${value}%`, 'Percentual']}
                labelFormatter={(label: string) => label}
              />
              <Legend />
              <Bar dataKey="percentual" fill="#8884d8" name="Percentual (%)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribuição por Status
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={70}
                fill="#8884d8"
                dataKey="quantidade"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => [value, 'Candidatos']}
                labelFormatter={(label, payload) => {
                  if (payload && payload.length > 0) {
                    const data = payload[0].payload as { status: string; percentual: string };
                    return `${data.status} (${data.percentual}%)`;
                  }
                  return label;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Legenda customizada */}
          <div className="mt-4 grid grid-cols-1 gap-2">
            {statusData.map((item, index) => (
              <div key={index} className="flex items-center gap-3 p-2 rounded bg-gray-50">
                <div 
                  className="w-4 h-4 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: item.color }}
                ></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{item.status}</p>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="font-semibold">{item.quantidade}</span>
                  <span>({item.percentual}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Histograma */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Histograma: Posições dos Candidatos Aprovados
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={histogramData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="posicao" 
              label={{ value: 'Posição no Ranking Semântico', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: 'Quantidade de Aprovados', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value: number) => [value, 'Candidatos Aprovados']}
              labelFormatter={(label: number) => `Posição ${label}`}
            />
            <Bar dataKey="quantidade" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Interpretação Estruturada */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
          📊 {performanceData.interpretacao_estruturada?.titulo || 'Interpretação dos Resultados'}
        </h3>
        
        {performanceData.interpretacao_estruturada ? (
          <div className="space-y-6">
            {/* Visão Geral */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                📈 Visão Geral
              </h4>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-2xl font-bold text-blue-600">
                    {performanceData.interpretacao_estruturada.visao_geral.total_candidatos.valor.toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    {performanceData.interpretacao_estruturada.visao_geral.total_candidatos.descricao}
                  </p>
                </div>
                <div>
                  <p className="text-gray-700">
                    {performanceData.interpretacao_estruturada.visao_geral.objetivo}
                  </p>
                </div>
              </div>
            </div>

            {/* Métricas de Precisão */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                🎯 Métricas de Precisão
              </h4>
              <div className="grid md:grid-cols-2 gap-4">
                {performanceData.interpretacao_estruturada.metricas_precisao.map((metrica, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <p className="font-medium text-gray-800">{metrica.label}</p>
                      {metrica.descricao && (
                        <p className="text-xs text-gray-600">{metrica.descricao}</p>
                      )}
                    </div>
                    <p className="text-lg font-bold text-blue-600">{metrica.valor}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Análise Detalhada */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                🔍 Análise Detalhada
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-semibold text-gray-800">Top N</th>
                      <th className="text-center py-2 px-3 font-semibold text-gray-800">Quantidade</th>
                      <th className="text-center py-2 px-3 font-semibold text-gray-800">Percentual</th>
                      <th className="text-left py-2 px-3 font-semibold text-gray-800">Interpretação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {performanceData.interpretacao_estruturada.analise_detalhada.map((item, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: item.cor }}
                            ></div>
                            <span className="font-medium">{item.categoria}</span>
                          </div>
                        </td>
                        <td className="text-center py-3 px-3 font-semibold">{item.quantidade}</td>
                        <td className="text-center py-3 px-3 font-semibold text-blue-600">
                          {item.percentual}%
                        </td>
                        <td className="py-3 px-3 text-gray-600">{item.interpretacao}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Conclusão */}
            <div className={`rounded-lg p-4 border-2 ${
              performanceData.interpretacao_estruturada.conclusao.cor === 'green' ? 'border-green-200 bg-green-50' :
              performanceData.interpretacao_estruturada.conclusao.cor === 'yellow' ? 'border-yellow-200 bg-yellow-50' :
              performanceData.interpretacao_estruturada.conclusao.cor === 'red' ? 'border-red-200 bg-red-50' :
              'border-gray-200 bg-gray-50'
            }`}>
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                🏆 Conclusão
              </h4>
              <div className="space-y-3">
                <p className="font-medium text-gray-800">
                  {performanceData.interpretacao_estruturada.conclusao.texto}
                </p>
                <div className={`p-3 rounded border-l-4 ${
                  performanceData.interpretacao_estruturada.conclusao.cor === 'green' ? 'border-green-400 bg-green-100' :
                  performanceData.interpretacao_estruturada.conclusao.cor === 'yellow' ? 'border-yellow-400 bg-yellow-100' :
                  performanceData.interpretacao_estruturada.conclusao.cor === 'red' ? 'border-red-400 bg-red-100' :
                  'border-gray-400 bg-gray-100'
                }`}>
                  <p className="text-sm text-gray-700">
                    <strong>Recomendação:</strong> {performanceData.interpretacao_estruturada.conclusao.recomendacao}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <div className="whitespace-pre-line text-gray-700">
              {performanceData.mensagem_interpretacao}
            </div>
          </div>
        )}
      </div>

      {/* Footer com timestamp */}
      <div className="text-center text-sm text-gray-500">
        Dados gerados em: {new Date(performanceData.generated_at).toLocaleString('pt-BR')}
      </div>

      {/* Modal de confirmação de atualização */}
      {showRefreshConfirm && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowRefreshConfirm(false);
            }
          }}
        >
          <div className="bg-white rounded-lg p-6 max-w-md w-mx mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <RefreshCw className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Atualizar Análise</h3>
                <p className="text-sm text-gray-600">Recalcular performance semântica</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              Tem certeza que deseja atualizar os dados? Isso irá:
              <br />
              <span className="block mt-2 space-y-1">
                <span className="text-blue-700 font-medium">• Limpar o cache atual</span><br />
                <span className="text-blue-700 font-medium">• Recalcular toda a análise semântica</span><br />
                <span className="text-blue-700 font-medium">• Processar vagas e candidatos aprovados</span>
              </span>
              <br />
              <span className="text-orange-600 font-medium">
                ⏱️ Esta operação pode levar alguns minutos para ser concluída.
              </span>
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowRefreshConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleRefresh}
                disabled={clearCacheMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {clearCacheMutation.isPending ? (
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Atualizando...
                  </div>
                ) : (
                  'Atualizar Análise'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
