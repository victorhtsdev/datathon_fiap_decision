import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface UseDataRefreshNotificationProps {
  onDataRefresh: (message: string) => void;
}

export function useDataRefreshNotification({ onDataRefresh }: UseDataRefreshNotificationProps) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const cache = queryClient.getQueryCache();
    
    const unsubscribe = cache.subscribe((event) => {
      // Detecta quando uma query é atualizada com sucesso
      if (event?.type === 'updated' && event.query.state.status === 'success') {
        const queryKey = event.query.queryKey[0] as string;
        
        // Mapear tipos de query para mensagens amigáveis
        const messages: Record<string, string> = {
          'workbooks': 'Lista de workbooks atualizada',
          'vagas': 'Lista de vagas atualizada',
          'semantic-performance': 'Análise de performance atualizada',
          'match-prospects': 'Dados de candidatos atualizados',
        };

        const message = messages[queryKey];
        if (message) {
          onDataRefresh(message);
        }
      }
    });

    return () => unsubscribe();
  }, [queryClient, onDataRefresh]);
}
