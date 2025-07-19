import { MapPin, Clock, Building } from 'lucide-react';
import type { Vaga } from '../types/api';

interface VagaCardProps {
  vaga: Vaga;
  onSelect: () => void;
  isLoading?: boolean;
}

export function VagaCard({ vaga, onSelect, isLoading }: VagaCardProps) {
  return (
    <div className="card hover:shadow-md transition-shadow duration-200 cursor-pointer group">
      <div className="space-y-4">
        {/* Header */}
        <div>
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
              {vaga.informacoes_basicas_titulo_vaga || 'Title not informed'}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              vaga.status_vaga === 'nao_iniciada' 
                ? 'bg-gray-100 text-gray-800' 
                : vaga.status_vaga === 'aberta'
                ? 'bg-green-100 text-green-800'
                : vaga.status_vaga === 'em_andamento'
                ? 'bg-blue-100 text-blue-800'
                : vaga.status_vaga === 'em_analise'
                ? 'bg-yellow-100 text-yellow-800'
                : vaga.status_vaga === 'pausada'
                ? 'bg-orange-100 text-orange-800'
                : vaga.status_vaga === 'cancelada'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {vaga.status_vaga === 'nao_iniciada' ? 'Não Iniciada' : 
               vaga.status_vaga === 'aberta' ? 'Aberta' :
               vaga.status_vaga === 'em_andamento' ? 'Em Andamento' : 
               vaga.status_vaga === 'em_analise' ? 'Em Análise' :
               vaga.status_vaga === 'pausada' ? 'Pausada' :
               vaga.status_vaga === 'finalizada' ? 'Finalizada' :
               vaga.status_vaga === 'cancelada' ? 'Cancelada' : 'Status Desconhecido'}
            </span>
          </div>
          <div className="flex items-center text-sm text-gray-500 mt-1">
            <Building className="w-4 h-4 mr-1" />
            <span>ID: {vaga.id}</span>
          </div>
        </div>

        {/* Informações adicionais podem ser adicionadas aqui quando disponíveis */}
        <div className="space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="w-4 h-4 mr-2" />
            <span>Localização não especificada</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="w-4 h-4 mr-2" />
            <span>Data não especificada</span>
          </div>
        </div>

        {/* Actions */}
        <div className="pt-4 border-t border-gray-100">
          <button
            onClick={onSelect}
            disabled={isLoading}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Carregando...
              </div>
            ) : (
              'Criar Workbook'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
