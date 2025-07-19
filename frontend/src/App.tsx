import { useState } from 'react';
import { QueryClient, QueryClientProvider, useMutation, useQueryClient } from '@tanstack/react-query';
import { VagaSelector } from './components/VagaSelector';
import { WorkbookList } from './components/WorkbookList';
import { WorkbookDetails } from './components/WorkbookDetails';
import { Header } from './components/Header';
import { apiService } from './services/api';
import type { Vaga, Workbook } from './types/api';

const globalQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, 
      retry: 1,
    },
  },
});

type ViewMode = 'workbooks' | 'create-workbook' | 'workbook-details';

function CreateWorkbookView({ onBack }: { onBack: () => void }) {
  const queryClient = useQueryClient();
  const [selectedVaga, setSelectedVaga] = useState<Vaga | undefined>();
  
  const createWorkbookMutation = useMutation({
    mutationFn: (vaga: Vaga) => apiService.createWorkbook({ vaga_id: vaga.id }),
    onSuccess: () => {
      // Invalida a query dos workbooks para recarregar a lista
      queryClient.invalidateQueries({ queryKey: ['workbooks'] });
      // Invalida a query das vagas para remover a vaga da seleção
      queryClient.invalidateQueries({ queryKey: ['vagas'] });
      // Volta para a lista
      onBack();
    },
    onError: (error) => {
      console.error('Erro ao criar workbook:', error);
      // O erro será mostrado pelo VagaSelector
    }
  });

  const handleVagaSelect = (vaga: Vaga) => {
    setSelectedVaga(vaga);
    createWorkbookMutation.mutate(vaga);
  };

  return (
    <div>
      <div className="mb-6">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-800 flex items-center gap-2 transition-colors"
          disabled={createWorkbookMutation.isPending}
        >
          ← Voltar para Workbooks
        </button>
      </div>
      
      {createWorkbookMutation.error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Erro ao criar workbook:</p>
          <p>{(createWorkbookMutation.error as Error).message}</p>
        </div>
      )}
      
      <VagaSelector 
        onVagaSelect={handleVagaSelect}
        onBack={onBack}
        selectedVaga={selectedVaga}
        isCreating={createWorkbookMutation.isPending}
      />
    </div>
  );
}

function AppContent() {
  const [currentView, setCurrentView] = useState<ViewMode>('workbooks');
  const [selectedWorkbook, setSelectedWorkbook] = useState<Workbook | null>(null);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const queryClient = useQueryClient();

  const deleteWorkbookMutation = useMutation({
    mutationFn: (workbook: Workbook) => apiService.deleteWorkbook(workbook.id),
    onSuccess: () => {
      // Invalida a query dos workbooks para recarregar a lista
      queryClient.invalidateQueries({ queryKey: ['workbooks'] });
      // Invalida a query das vagas para atualizar os status
      queryClient.invalidateQueries({ queryKey: ['vagas'] });
      // Volta para a lista
      setCurrentView('workbooks');
      setSelectedWorkbook(null);
      // Mostra notificação de sucesso
      setNotification({type: 'success', message: 'Workbook excluído com sucesso!'});
      // Remove a notificação após 3 segundos
      setTimeout(() => setNotification(null), 3000);
    },
    onError: (error) => {
      console.error('Erro ao deletar workbook:', error);
      // Mostra notificação de erro
      setNotification({type: 'error', message: 'Erro ao excluir workbook. Tente novamente.'});
      // Remove a notificação após 5 segundos
      setTimeout(() => setNotification(null), 5000);
    }
  });

  const handleWorkbookSelect = (workbook: Workbook) => {
    setSelectedWorkbook(workbook);
    setCurrentView('workbook-details');
  };

  const handleDeleteWorkbook = (workbook: Workbook) => {
    deleteWorkbookMutation.mutate(workbook);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'workbooks':
        return <WorkbookList 
          onCreateNew={() => setCurrentView('create-workbook')}
          onWorkbookSelect={handleWorkbookSelect}
        />;
      case 'create-workbook':
        return <CreateWorkbookView onBack={() => setCurrentView('workbooks')} />;
      case 'workbook-details':
        return selectedWorkbook ? (
          <WorkbookDetails 
            workbook={selectedWorkbook} 
            onBack={() => setCurrentView('workbooks')}
            onDelete={handleDeleteWorkbook}
            isDeleting={deleteWorkbookMutation.isPending}
          />
        ) : (
          <WorkbookList 
            onCreateNew={() => setCurrentView('create-workbook')}
            onWorkbookSelect={handleWorkbookSelect}
          />
        );
      default:
        return <WorkbookList 
          onCreateNew={() => setCurrentView('create-workbook')}
          onWorkbookSelect={handleWorkbookSelect}
        />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Notificação */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
          notification.type === 'success' 
            ? 'bg-green-600 text-white' 
            : 'bg-red-600 text-white'
        }`}>
          <div className="flex items-center gap-2">
            <div className="font-medium">{notification.message}</div>
            <button 
              onClick={() => setNotification(null)}
              className="ml-2 text-white hover:text-gray-200"
            >
              ×
            </button>
          </div>
        </div>
      )}
      
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {currentView !== 'workbook-details' && (
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Sistema de Matching de Candidatos
              </h1>
              <p className="text-gray-600">
                {currentView === 'workbooks' 
                  ? 'Gerencie seus workbooks de análise de candidatos'
                  : 'Selecione uma vaga para criar um novo workbook de recrutamento'
                }
              </p>
            </div>
          )}
          
          {renderCurrentView()}
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={globalQueryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
