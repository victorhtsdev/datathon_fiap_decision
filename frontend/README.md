## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
## Variáveis de Ambiente

Para integração correta com o backend, configure as variáveis de ambiente no arquivo `.env` do backend, usando valores genéricos como exemplo:

```env
LLM_BACKEND=ollama
OLLAMA_MODEL=seu_modelo_aqui
DEEPSEEK_API_KEY=sk-sua-chave-aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/seu_banco
CHUNK_SIZE=5000
DEBUG=True
SAVE_LOGS=false
APP_LOG_ENABLED=true
APP_LOG_LEVEL=INFO
APP_LOG_FILE=app.log
LLM_LOG=True
OPENAI_API_KEY="sk-sua-chave-openai-aqui"
```

Certifique-se de ajustar as chaves e URLs conforme seu ambiente, nunca expondo dados sensíveis em arquivos públicos.
# Frontend - Datathon Decision

Este frontend foi desenvolvido em React com Vite e Tailwind CSS, proporcionando uma interface moderna para interação com as APIs do backend.

## Funcionalidades

- Visualização e filtragem de candidatos
- Consulta e gerenciamento de vagas
- Chat com LLM para análise semântica
- Dashboard de performance

## Instalação

1. Instale as dependências:
   ```bash
   npm install
   ```
2. Execute o frontend:
   ```bash
   npm run dev
   ```

## Estrutura de Pastas
- `src/components/`: Componentes React reutilizáveis
- `src/services/`: Integração com APIs do backend
- `src/hooks/`: Hooks customizados
- `src/types/`: Tipos TypeScript
- `public/`: Assets públicos

## Exemplos de Uso
- Para consultar candidatos:
  ```js
  import { getApplicants } from './services/api';
  getApplicants().then(...);
  ```
- Para enviar mensagem ao chat:
  ```js
  import { sendChatMessage } from './services/chat';
  sendChatMessage('Quais vagas estão abertas?').then(...);
  ```

## Dependências
- React
- Vite
- Tailwind CSS
- Axios
- Outros (ver `package.json`)

## Testes
Execute os testes com:
```bash
npm test
```

## Documentação
Consulte o backend para detalhes dos endpoints disponíveis.

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```
