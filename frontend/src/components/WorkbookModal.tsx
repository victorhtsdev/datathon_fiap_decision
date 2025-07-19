import { useState } from 'react';
import { X, User, Briefcase, MapPin, Clock } from 'lucide-react';
import type { VagaDetalhada } from '../types/api';

interface WorkbookModalProps {
  vaga: VagaDetalhada;
  onClose: () => void;
  onCreate: (criadoPor: string) => void;
  isLoading: boolean;
}

export function WorkbookModal({ vaga, onClose, onCreate, isLoading }: WorkbookModalProps) {
  const [criadoPor, setCriadoPor] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (criadoPor.trim()) {
      onCreate(criadoPor.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Criar Workbook</h2>
            <p className="text-sm text-gray-600">
              Crie um novo workbook para esta vaga
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {/* Vaga Info */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Briefcase className="w-5 h-5 text-primary-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">
                  {vaga.informacoes_basicas_titulo_vaga || 'Título não informado'}
                </h3>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center text-sm text-gray-600">
                    <User className="w-4 h-4 mr-2" />
                    <span>ID: {vaga.id}</span>
                  </div>
                  {vaga.informacoes_basicas_cliente && (
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-2" />
                      <span>Cliente: {vaga.informacoes_basicas_cliente}</span>
                    </div>
                  )}
                  {vaga.informacoes_basicas_data_requicisao && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>Data: {vaga.informacoes_basicas_data_requicisao}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="criado-por" className="block text-sm font-medium text-gray-700 mb-2">
                Criado por *
              </label>
              <input
                id="criado-por"
                type="email"
                value={criadoPor}
                onChange={(e) => setCriadoPor(e.target.value)}
                placeholder="Digite seu e-mail"
                className="input"
                required
                disabled={isLoading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Insira o e-mail do responsável pelo workbook
              </p>
            </div>

            {/* Additional vaga details */}
            {vaga.perfil_vaga_areas_atuacao && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Áreas de Atuação
                </label>
                <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                  {vaga.perfil_vaga_areas_atuacao}
                </div>
              </div>
            )}

            {vaga.perfil_vaga_principais_atividades && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Principais Atividades
                </label>
                <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                  {vaga.perfil_vaga_principais_atividades}
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={!criadoPor.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Criando...
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
