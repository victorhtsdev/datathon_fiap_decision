import { Briefcase, FileText, Sparkles, BarChart3 } from 'lucide-react';

interface HeaderProps {
  onNavigate?: (view: string) => void;
}

export function Header({ onNavigate }: HeaderProps) {
  const getButtonClasses = () => {
    // Todos os botões sempre com o estilo que era do botão ativo (texto branco + fundo branco transparente)
    return "flex items-center gap-2 font-medium transition-all duration-200 px-3 py-2 rounded-lg text-white bg-white bg-opacity-20 hover:bg-opacity-30";
  };

  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-white bg-opacity-20 rounded-xl backdrop-blur-sm">
              <Briefcase className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                DataThon Decision
                <Sparkles className="w-5 h-5 text-yellow-300" />
              </h1>
              <p className="text-blue-100 font-medium">Sistema Inteligente de Matching de Candidatos</p>
            </div>
          </div>
          
          <nav className="flex items-center space-x-8">
            <button
              onClick={() => onNavigate?.('workbooks')}
              className={getButtonClasses()}
            >
              <FileText className="w-5 h-5" />
              Workbooks
            </button>
            
            <button
              onClick={() => onNavigate?.('analytics')}
              className={getButtonClasses()}
            >
              <BarChart3 className="w-5 h-5" />
              Analytics
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
