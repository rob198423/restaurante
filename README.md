# Gideão AI

Protótipo web em português do Brasil para um assistente pessoal avançado em estilo
Jarvis, com foco em Android, PC, produtividade, automação, estudos e segurança.

## Recursos

- Comando por texto e voz, quando o navegador expõe `SpeechRecognition`.
- Resposta por voz natural em pt-BR usando `speechSynthesis`.
- Memória inteligente persistida em `localStorage`.
- Cronogramas de estudos e concursos adaptados por matéria, nível e tempo.
- Simulação de automações para abrir apps, organizar arquivos e preencher cadastros.
- Preenchimento automático com confirmação para dados sensíveis como CPF.
- Análise visual simulada de tela com detecção de botões e formulário.
- Modo pesquisa com prioridade para opções gratuitas e depois custo-benefício.
- Regras de segurança para bloquear compras, transferências, senhas e exclusões sem
  confirmação explícita.
- Referência de arquitetura para APK Android com Flutter, acessibilidade,
  notificações e execução em background.

## Prioridade de IA

1. Gemini Flash
2. DeepSeek
3. OpenRouter
4. OpenAI

## Como executar

Abra `index.html` diretamente no navegador ou sirva a pasta com:

```bash
python3 -m http.server 4173
```

Depois acesse `http://localhost:4173`.
