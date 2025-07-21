import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Send, User, MapPin, Phone, Mail, Calendar, GraduationCap, Briefcase, Star, ChevronDown, ChevronUp, Bot, MessageCircle, Trash2, FileText, Target, Users, AlertCircle, Globe, Save, CheckCircle, RotateCcw } from 'lucide-react';
import { apiService } from '../services/api';
import type { Workbook, Applicant, ChatMessage, MatchProspectData } from '../types/api';

interface WorkbookDetailsProps {
  workbook: Workbook;
  onBack: () => void;
  onDelete?: (workbook: Workbook) => void;
  isDeleting?: boolean;
}

interface ApplicantCardProps {
  applicant: Applicant;
  isExpanded: boolean;
  onToggle: () => void;
  isSelected: boolean;
  onSelectChange: (selected: boolean) => void;
  isWorkbookClosed: boolean;
}

function ApplicantCard({ applicant, isExpanded, onToggle, isSelected, onSelectChange, isWorkbookClosed }: ApplicantCardProps) {
  return (
    <div className={`bg-white rounded-lg border-2 shadow-sm hover:shadow-md transition-all duration-200 ${
      isSelected 
        ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-blue-100' 
        : 'border-gray-200 hover:border-gray-300'
    } ${isWorkbookClosed ? 'opacity-75' : ''}`}>
      {/* Header do card - sempre visível */}
      <div className="p-4">
        <div className="flex items-center gap-3">
          {/* Checkbox de seleção */}
          <div className="flex-shrink-0">
            <input
              type="checkbox"
              checked={isSelected}
              disabled={isWorkbookClosed}
              onChange={(e) => {
                e.stopPropagation();
                if (!isWorkbookClosed) {
                  onSelectChange(e.target.checked);
                }
              }}
              className={`w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer ${
                isWorkbookClosed ? 'cursor-not-allowed opacity-50' : ''
              }`}
            />
          </div>
          
          {/* Informações do candidato */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="flex-shrink-0">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                isSelected 
                  ? 'bg-gradient-to-br from-blue-600 to-indigo-700' 
                  : 'bg-gradient-to-br from-blue-500 to-purple-600'
              }`}>
                {applicant.nome.charAt(0).toUpperCase()}
              </div>
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900 truncate">{applicant.nome}</h3>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full flex-shrink-0">
                  ID: {applicant.id}
                </span>
              </div>
              <p className="text-sm text-gray-600 truncate">{applicant.email}</p>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-xs text-gray-500 capitalize">{applicant.nivel_maximo_formacao}</p>
                {applicant.score_semantico !== undefined && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                    Score: {(applicant.score_semantico * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Informações resumidas e botão expandir */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {applicant.cv_pt?.habilidades?.length || 0} habilidades
              </div>
              <div className="text-xs text-gray-500">
                {applicant.cv_pt?.experiencias?.length || 0} experiências
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggle();
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Conteúdo expandido */}
      {isExpanded && (
        <div className="border-t border-gray-100 p-4 space-y-6">
          {/* Informações pessoais */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <User className="w-4 h-4" />
              Informações Pessoais
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-400" />
                <span>ID: {applicant.id}</span>
              </div>
              {applicant.score_semantico !== undefined && (
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-gray-400" />
                  <span>Score Semântico: {(applicant.score_semantico * 100).toFixed(2)}%</span>
                </div>
              )}
              {applicant.telefone_celular && (
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span>{applicant.telefone_celular}</span>
                </div>
              )}
              {applicant.data_nascimento && applicant.data_nascimento !== "0000-00-00" && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>
                    {(() => {
                      try {
                        let dateStr = applicant.data_nascimento;
                        
                        // Se está no formato DD-MM-YYYY, converte para YYYY-MM-DD
                        if (dateStr.match(/^\d{2}-\d{2}-\d{4}$/)) {
                          const [day, month, year] = dateStr.split('-');
                          dateStr = `${year}-${month}-${day}`;
                        }
                        
                        const date = new Date(dateStr);
                        return isNaN(date.getTime()) ? applicant.data_nascimento : date.toLocaleDateString('pt-BR');
                      } catch {
                        return applicant.data_nascimento;
                      }
                    })()}
                  </span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-gray-400" />
                <span className="capitalize">{applicant.sexo === 'F' ? 'Feminino' : 'Masculino'}</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span className="capitalize">{applicant.estado_civil}</span>
              </div>
            </div>
          </div>

          {/* Habilidades */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Habilidades
            </h4>
            <div className="flex flex-wrap gap-2">
              {(applicant.cv_pt?.habilidades || []).map((habilidade, index) => (
                <span
                  key={index}
                  className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full"
                >
                  {habilidade}
                </span>
              ))}
            </div>
          </div>

          {/* Idiomas */}
          {applicant.cv_pt?.idiomas && applicant.cv_pt.idiomas.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Idiomas
              </h4>
              <div className="flex flex-wrap gap-2">
                {(applicant.cv_pt?.idiomas || []).map((idioma, index) => (
                  <span
                    key={index}
                    className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full"
                  >
                    {idioma.idioma} - {idioma.nivel}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Formação */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <GraduationCap className="w-4 h-4" />
              Formação
            </h4>
            <div className="space-y-3">
              {(applicant.cv_pt?.formacoes || []).map((formacao, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-900">{formacao.curso}</div>
                  <div className="text-sm text-gray-600 capitalize">{formacao.nivel}</div>
                  <div className="text-xs text-gray-500">
                    {formacao.ano_inicio} - {formacao.ano_fim}
                    {formacao.instituicao && ` • ${formacao.instituicao}`}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Experiências */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Briefcase className="w-4 h-4" />
              Experiências Profissionais
            </h4>
            <div className="space-y-4">
              {(applicant.cv_pt?.experiencias || []).map((experiencia, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium text-gray-900">{experiencia.cargo}</div>
                      <div className="text-sm font-medium text-blue-600">{experiencia.empresa}</div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {experiencia.inicio} - {experiencia.fim}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {experiencia.descricao}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Componente para exibir informações da vaga horizontalmente
interface VagaInfoHorizontalProps {
  vagaId: number;
}

function VagaInfoHorizontal({ vagaId }: VagaInfoHorizontalProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { data: vaga, isLoading, error } = useQuery({
    queryKey: ['vaga', vagaId],
    queryFn: () => apiService.getVagaDetalhes(vagaId),
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchOnWindowFocus: true, // Recarrega quando volta para a aba
  });

  if (isLoading) {
    return (
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="flex gap-6">
            <div className="h-4 bg-gray-200 rounded w-32"></div>
            <div className="h-4 bg-gray-200 rounded w-40"></div>
            <div className="h-4 bg-gray-200 rounded w-36"></div>
            <div className="h-4 bg-gray-200 rounded w-28"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border-b border-red-200 p-4">
        <div className="flex items-center gap-2 text-red-600">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">Erro ao carregar informações da vaga</span>
        </div>
      </div>
    );
  }

  if (!vaga) return null;

  return (
    <div className="bg-white border-b border-gray-200">
      {/* Informações principais horizontais */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6 text-sm flex-wrap">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">ID:</span>
              <span className="font-medium text-gray-900">#{vaga.id}</span>
            </div>

            {vaga.informacoes_basicas_cliente && (
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Cliente:</span>
                <span className="font-medium text-gray-900">{vaga.informacoes_basicas_cliente}</span>
              </div>
            )}
            
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Local:</span>
              <span className="font-medium text-gray-900">
                {vaga.perfil_vaga_cidade || vaga.perfil_vaga_estado || 'Não especificado'}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Nível:</span>
              <span className="font-medium text-gray-900 capitalize">
                {vaga.perfil_vaga_nivel_profissional || 'Não especificado'}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium px-2 py-1 rounded-full text-xs capitalize ${
                vaga.status_vaga === 'aberta' 
                  ? 'bg-green-100 text-green-700' 
                  : vaga.status_vaga === 'em_andamento'
                  ? 'bg-blue-100 text-blue-700'
                  : vaga.status_vaga === 'finalizada'
                  ? 'bg-gray-100 text-gray-700'
                  : vaga.status_vaga === 'cancelada'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-yellow-100 text-yellow-700'
              }`}>
                {vaga.status_vaga.replace('_', ' ')}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Área:</span>
              <span className="font-medium text-gray-900">
                {vaga.perfil_vaga_areas_atuacao || 'Não especificado'}
              </span>
            </div>
          </div>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <span>{isExpanded ? 'Menos detalhes' : 'Mais detalhes'}</span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Card colapsável com detalhes */}
      {isExpanded && (
        <div className="px-6 pb-4">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Objetivo da Vaga */}
              {vaga.informacoes_basicas_objetivo_vaga && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Objetivo da Vaga
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">{vaga.informacoes_basicas_objetivo_vaga}</p>
                </div>
              )}

              {/* Formação Acadêmica */}
              {vaga.perfil_vaga_nivel_academico && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <GraduationCap className="w-4 h-4" />
                    Nível Acadêmico
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">{vaga.perfil_vaga_nivel_academico}</p>
                </div>
              )}

              {/* Principais Atividades */}
              {vaga.perfil_vaga_principais_atividades && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Principais Responsabilidades
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">{vaga.perfil_vaga_principais_atividades}</p>
                </div>
              )}

              {/* Competências Técnicas - só exibe se for diferente das principais atividades */}
              {vaga.perfil_vaga_competencia_tecnicas_e_comportamentais && 
               vaga.perfil_vaga_competencia_tecnicas_e_comportamentais !== vaga.perfil_vaga_principais_atividades && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <Star className="w-4 h-4" />
                    Competências Técnicas e Comportamentais
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">{vaga.perfil_vaga_competencia_tecnicas_e_comportamentais}</p>
                </div>
              )}
            </div>

            {/* Observações */}
            {vaga.perfil_vaga_demais_observacoes && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="font-medium text-gray-900 mb-2">Observações Adicionais</h4>
                <p className="text-sm text-gray-700 leading-relaxed">{vaga.perfil_vaga_demais_observacoes}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function WorkbookDetails({ workbook, onBack, onDelete, isDeleting = false }: WorkbookDetailsProps) {
  const queryClient = useQueryClient();
  
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Olá! Eu sou seu assistente de recrutamento. Como posso ajudá-lo a encontrar os melhores candidatos para esta vaga?',
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [filteredApplicants, setFilteredApplicants] = useState<Applicant[]>([]);
  const [totalCandidates, setTotalCandidates] = useState<number | undefined>(undefined);
  const [lastFilterQuery, setLastFilterQuery] = useState<string>('');
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showCloseConfirm, setShowCloseConfirm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [showReopenConfirm, setShowReopenConfirm] = useState(false);
  const [isReopening, setIsReopening] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined); // Estado para manter session_id
  
  // Estados para sistema de seleção
  const [selectedApplicants, setSelectedApplicants] = useState<Set<number>>(new Set());
  const [isSavingSelection, setIsSavingSelection] = useState(false);
  
  // Verifica se há candidatos selecionados
  const hasSelectedApplicants = selectedApplicants.size > 0;
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Query para carregar match prospects existentes
  const { data: existingProspects } = useQuery({
    queryKey: ['match-prospects', workbook.id],
    queryFn: () => apiService.getMatchProspects(workbook.id),
    staleTime: 1 * 60 * 1000, // 1 minuto (dados mais voláteis)
    refetchOnWindowFocus: true, // Recarrega quando volta para a aba
  });

  // Effect para carregar seleções existentes
  useEffect(() => {
    if (existingProspects) {
      const selectedIds = new Set(
        existingProspects
          .filter(prospect => prospect.selecionado)
          .map(prospect => prospect.applicant_id)
      );
      setSelectedApplicants(selectedIds);
      
      // Se há prospects existentes, carregar os candidatos correspondentes
      if (existingProspects.length > 0) {
        const loadProspectsAsCandidates = async () => {
          try {
            // Buscar dados completos dos candidatos via API
            const candidateIds = existingProspects.map(p => p.applicant_id);
            const candidates = await apiService.getApplicantsByIds(candidateIds);
            
            if (candidates.length > 0) {
              // Adiciona informações dos prospects aos candidatos
              const candidatesWithProspectInfo = candidates.map(candidate => ({
                ...candidate,
                score_semantico: existingProspects.find(p => p.applicant_id === candidate.id)?.score_semantico || 0.5,
                selecionado: existingProspects.find(p => p.applicant_id === candidate.id)?.selecionado || false
              }));
              
              // Ordena candidatos: selecionados primeiro, depois por score semântico
              const sortedCandidates = candidatesWithProspectInfo.sort((a, b) => {
                if (a.selecionado && !b.selecionado) return -1;
                if (!a.selecionado && b.selecionado) return 1;
                // Dentro do mesmo grupo (selecionado ou não), ordena por score semântico decrescente
                return (b.score_semantico || 0) - (a.score_semantico || 0);
              });
              
              setFilteredApplicants(sortedCandidates);
              setTotalCandidates(sortedCandidates.length);
              setLastFilterQuery('Candidatos salvos anteriormente');
            }
            
          } catch (error) {
            console.error('Erro ao carregar prospects:', error);
          }
        };
        
        loadProspectsAsCandidates();
      }
    }
  }, [existingProspects]);

  // Mutation para salvar seleção de candidatos
  const saveSelectionMutation = useMutation({
    mutationFn: (prospects: MatchProspectData[]) => 
      apiService.updateMatchProspects(workbook.id, prospects),
    onSuccess: () => {
      const count = selectedApplicants.size;
      if (count === 0) {
        alert('🗑️ Todas as seleções foram removidas do workbook.');
        // Limpa os candidatos filtrados se eram prospects salvos
        if (lastFilterQuery === 'Candidatos salvos anteriormente') {
          setFilteredApplicants([]);
          setTotalCandidates(0);
          setLastFilterQuery('');
        }
      } else {
        alert(`✅ Sucesso! ${count} candidato${count !== 1 ? 's' : ''} selecionado${count !== 1 ? 's' : ''} salvo${count !== 1 ? 's' : ''} no workbook.`);
      }
      setIsSavingSelection(false);
    },
    onError: (error) => {
      console.error('Erro ao salvar seleção:', error);
      alert('❌ Erro ao salvar seleção. Tente novamente.');
      setIsSavingSelection(false);
    }
  });

  // Mutation para encerrar workbook
  const closeWorkbookMutation = useMutation({
    mutationFn: () => apiService.updateWorkbook(workbook.id, { 
      status: 'fechado',
      fechado_em: new Date().toISOString()
    }),
    onSuccess: () => {
      alert('✅ Workbook encerrado com sucesso!');
      setIsClosing(false);
      setShowCloseConfirm(false);
      
      // Invalida a query dos workbooks para recarregar a lista
      queryClient.invalidateQueries({ queryKey: ['workbooks'] });
      
      // Volta para a lista de workbooks
      onBack();
    },
    onError: (error) => {
      console.error('Erro ao encerrar workbook:', error);
      alert('❌ Erro ao encerrar workbook. Tente novamente.');
      setIsClosing(false);
      setShowCloseConfirm(false);
    }
  });

  // Mutation para reabrir workbook
  const reopenWorkbookMutation = useMutation({
    mutationFn: () => apiService.updateWorkbook(workbook.id, { 
      status: 'aberto'
    }),
    onSuccess: () => {
      alert('✅ Workbook reaberto com sucesso!');
      setIsReopening(false);
      setShowReopenConfirm(false);
      
      // Invalida a query dos workbooks para recarregar a lista
      queryClient.invalidateQueries({ queryKey: ['workbooks'] });
      
      // Força recarregamento da página para atualizar o estado
      window.location.reload();
    },
    onError: (error) => {
      console.error('Erro ao reabrir workbook:', error);
      alert('❌ Erro ao reabrir workbook. Tente novamente.');
      setIsReopening(false);
      setShowReopenConfirm(false);
    }
  });

  // Funções para gerenciar seleção
  const isWorkbookClosed = workbook.status === 'fechado';
  
  const handleApplicantSelect = (applicantId: number, selected: boolean) => {
    if (isWorkbookClosed) return; // Não permite seleção se workbook estiver fechado
    
    setSelectedApplicants(prev => {
      const newSet = new Set(prev);
      if (selected) {
        newSet.add(applicantId);
      } else {
        newSet.delete(applicantId);
      }
      return newSet;
    });
  };

  const handleSaveSelection = () => {
    if (isWorkbookClosed) return; // Não permite salvar se workbook estiver fechado
    
    setIsSavingSelection(true);
    
    // Se não há candidatos selecionados, limpa todas as seleções (desseleciona tudo)
    if (selectedApplicants.size === 0) {
      // Envia array vazio para limpar todos os prospects
      saveSelectionMutation.mutate([]);
      return;
    }
    
    // Converte apenas os candidatos SELECIONADOS em prospects
    const selectedCandidates = filteredApplicants.filter(applicant => 
      selectedApplicants.has(applicant.id)
    );
    
    const prospects: MatchProspectData[] = selectedCandidates.map(applicant => ({
      applicant_id: applicant.id,
      score_semantico: applicant.score_semantico || 0.5,
      origem: 'manual_selection',
      selecionado: true, // Todos são marcados como selecionados
      observacoes: 'Selecionado manualmente'
    }));

    saveSelectionMutation.mutate(prospects);
  };

  const toggleCardExpansion = (applicantId: number) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(applicantId)) {
        newSet.delete(applicantId);
      } else {
        newSet.add(applicantId);
      }
      return newSet;
    });
  };

  // Mutation para enviar mensagens para o LLM
  const chatMutation = useMutation({
    mutationFn: ({ message }: { message: string }) => 
      apiService.sendChatMessage(message, workbook.id, undefined, sessionId),
    onSuccess: (data, variables) => {
      // Atualiza o session_id se retornado pelo backend
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        filtered_candidates: data.filtered_candidates,
        total_candidates: data.total_candidates,
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
      
      // Se recebeu candidatos filtrados, atualiza a lista
      if (data.filtered_candidates && data.filtered_candidates.length > 0) {
        setFilteredApplicants(data.filtered_candidates);
        setTotalCandidates(data.total_candidates);
        setLastFilterQuery(variables.message);
      }
      
      setIsLoading(false);
    },
    onError: (error) => {
      console.error('Erro no chat:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date(),
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || chatMutation.isPending || isWorkbookClosed) return;

    const currentMessage = inputMessage; // Captura antes de limpar

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Envia mensagem para o LLM usando a API
    chatMutation.mutate({ message: currentMessage });
  };

  const handleDeleteWorkbook = () => {
    if (onDelete) {
      onDelete(workbook);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Modal de confirmação de exclusão */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-mx mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Excluir Workbook</h3>
                <p className="text-sm text-gray-600">Esta ação não pode ser desfeita</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              Tem certeza que deseja excluir o workbook <strong>#{workbook.id.slice(0, 8)}</strong>? 
              Todos os dados e histórico serão perdidos permanentemente.
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  handleDeleteWorkbook();
                  setShowDeleteConfirm(false);
                }}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Excluir Workbook
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmação de encerramento */}
      {showCloseConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-mx mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Encerrar Workbook</h3>
                <p className="text-sm text-gray-600">Finalizar processo de recrutamento</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              Tem certeza que deseja encerrar o workbook <strong>#{workbook.id.slice(0, 8)}</strong>? 
              O status será alterado para "fechado" e não será possível adicionar novos candidatos.
              <br />
              <span className="text-green-700 font-medium">
                {selectedApplicants.size} candidato{selectedApplicants.size !== 1 ? 's' : ''} selecionado{selectedApplicants.size !== 1 ? 's' : ''} será{selectedApplicants.size !== 1 ? 'ão' : ''} mantido{selectedApplicants.size !== 1 ? 's' : ''} no workbook.
              </span>
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowCloseConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  setIsClosing(true);
                  closeWorkbookMutation.mutate();
                }}
                className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Encerrar Workbook
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmação de reabertura */}
      {showReopenConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-mx mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <RotateCcw className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Reabrir Workbook</h3>
                <p className="text-sm text-gray-600">Reativar processo de recrutamento</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              Tem certeza que deseja reabrir o workbook <strong>#{workbook.id.slice(0, 8)}</strong>? 
              O status será alterado para "aberto" e será possível continuar adicionando candidatos.
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowReopenConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  setIsReopening(true);
                  reopenWorkbookMutation.mutate();
                }}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Reabrir Workbook
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  Workbook #{workbook.id.slice(0, 8)}
                </h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  workbook.status === 'fechado' 
                    ? 'bg-gray-100 text-gray-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {workbook.status === 'fechado' ? 'Encerrado' : 'Ativo'}
                </span>
              </div>
              <p className="text-gray-600">{workbook.vaga_titulo}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
              {filteredApplicants.length} candidatos
            </div>
            {workbook.status === 'fechado' ? (
              <button
                onClick={() => setShowReopenConfirm(true)}
                disabled={isReopening}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
              >
                {isReopening ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Reabrindo...
                  </>
                ) : (
                  <>
                    <RotateCcw className="w-4 h-4" />
                    Reabrir
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={() => setShowCloseConfirm(true)}
                disabled={isClosing || !hasSelectedApplicants}
                className="bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                title={!hasSelectedApplicants ? "É necessário selecionar pelo menos um candidato para encerrar o workbook" : ""}
              >
                {isClosing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Encerrando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Encerrar
                  </>
                )}
              </button>
            )}
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              {isDeleting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Excluindo...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  Excluir
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Seção de informações da vaga - horizontal */}
      <VagaInfoHorizontal vagaId={workbook.vaga_id} />

      <div className="flex h-[calc(100vh-160px)]">
        {/* Chat LLM - Lado Esquerdo */}
        <div className="w-1/2 border-r border-gray-200 bg-white flex flex-col">
          {/* Header do Chat */}
          <div className="border-b border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900">Assistente IA</h2>
                <p className="text-sm text-gray-600">
                  {isWorkbookClosed ? 'Workbook encerrado' : 'Filtro inteligente de candidatos'}
                </p>
              </div>
            </div>
            {isWorkbookClosed && (
              <div className="mt-3 p-3 bg-gray-100 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 text-gray-700">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Este workbook está encerrado</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Para continuar adicionando candidatos, reabra o workbook clicando no botão "Reabrir" acima.
                </p>
              </div>
            )}
          </div>

          {/* Mensagens do Chat */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('pt-BR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            ))}
            
            {(isLoading || chatMutation.isPending) && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input do Chat */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder={isWorkbookClosed ? "Workbook encerrado - chat desabilitado" : "Digite sua pergunta ou critério de busca..."}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={isLoading || chatMutation.isPending || isWorkbookClosed}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || chatMutation.isPending || !inputMessage.trim() || isWorkbookClosed}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-2 rounded-lg transition-colors disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Lista de Candidatos - Lado Direito */}
        <div className="w-1/2 bg-gray-50 overflow-y-auto">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">Candidatos Filtrados</h2>
                
                {/* Botão Salvar */}
                {filteredApplicants.length > 0 && !isWorkbookClosed && (
                  <div className="flex items-center gap-4">
                    <span className={`text-sm font-medium ${
                      selectedApplicants.size > 0 ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {selectedApplicants.size} de {filteredApplicants.length} selecionado{selectedApplicants.size !== 1 ? 's' : ''}
                    </span>
                    <button
                      onClick={handleSaveSelection}
                      disabled={isSavingSelection}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                        isSavingSelection
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : selectedApplicants.size === 0
                          ? 'bg-red-600 hover:bg-red-700 text-white shadow-sm hover:shadow-md'
                          : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md'
                      }`}
                      title={selectedApplicants.size === 0 ? 'Remove todas as seleções salvas' : 'Salva apenas os candidatos selecionados'}
                    >
                      {selectedApplicants.size === 0 ? (
                        <>
                          <Trash2 className="w-4 h-4" />
                          {isSavingSelection ? 'Limpando...' : 'Limpar Tudo'}
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4" />
                          {isSavingSelection ? 'Salvando...' : 'Salvar'}
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
              
              <div className="space-y-1">
                <p className="text-gray-600">
                  {filteredApplicants.length} candidato{filteredApplicants.length !== 1 ? 's' : ''} encontrado{filteredApplicants.length !== 1 ? 's' : ''}
                  {totalCandidates !== undefined && totalCandidates !== filteredApplicants.length && 
                    ` de ${totalCandidates} analisado${totalCandidates !== 1 ? 's' : ''}`
                  }
                </p>
                {lastFilterQuery && filteredApplicants.length > 0 && (
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded-lg inline-block">
                      {lastFilterQuery === 'Candidatos salvos anteriormente' ? '📋' : '🔍'} {lastFilterQuery}
                    </p>
                    {existingProspects && existingProspects.length > 0 && lastFilterQuery === 'Candidatos salvos anteriormente' && (
                      <span className="text-xs text-gray-500">
                        (carregados do workbook)
                      </span>
                    )}
                  </div>
                )}
                {filteredApplicants.some(applicant => applicant.score_semantico !== undefined) && (
                  <p className="text-xs text-green-600">
                    ✓ Ordenados por relevância semântica
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-4">
              {filteredApplicants.map((applicant) => (
                <ApplicantCard
                  key={applicant.id}
                  applicant={applicant}
                  isExpanded={expandedCards.has(applicant.id)}
                  onToggle={() => toggleCardExpansion(applicant.id)}
                  isSelected={selectedApplicants.has(applicant.id)}
                  onSelectChange={(selected) => handleApplicantSelect(applicant.id, selected)}
                  isWorkbookClosed={isWorkbookClosed}
                />
              ))}
            </div>

            {filteredApplicants.length === 0 && (
              <div className="text-center py-12">
                <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum candidato encontrado</h3>
                <p className="text-gray-600">
                  Use o chat à esquerda para buscar candidatos específicos
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
