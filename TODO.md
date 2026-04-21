# TODO — Mind Map Generator GPTs

Plano de trabalho priorizado para levar o projeto a um nível profissional, seguindo boas práticas de engenharia.

Legenda: `[ ]` por fazer · `[x]` feito · 🔴 crítico · 🟡 importante · 🟢 melhoria

---

## Fase 0 — Segurança imediata (bloqueante) 🔴

> Fazer **antes** de qualquer outro trabalho. Se o repo for público, estes pontos são urgentes.

- [x] **Revogar a API key do OpenRouter** atualmente em `backend/.env` e gerar uma nova. *(ação do utilizador)*
- [x] Confirmar/reforçar `.gitignore`.
- [ 
  
] Remover a key do histórico do Git com `git filter-repo` ou BFG Repo-Cleaner, e forçar push (coordenar antes com quem tenha clones). *(ação do utilizador — destrutivo)*
- [x] Criar `backend/.env.example` com as variáveis necessárias (sem valores reais).
- [x] Restringir CORS em `backend/app/main.py` — lê origens de `FRONTEND_ORIGINS` (CSV) via `settings.allowed_origins`.
- [x] Validação de input em `backend/app/routers/process.py`:
  - tamanho máximo de ficheiro (`MAX_FILE_SIZE_MB`, default 20);
  - MIME types permitidos (PDF / conjunto de áudio);
  - tamanho máximo de prompt (`MAX_PROMPT_CHARS`, default 10 000).
- [x] `APIKeyManager.js` removido (código morto com risco XSS).

---

## Fase 1 — Fundações de qualidade 🔴

> Infra mínima para trabalhar com confiança.

### Documentação
- [x] `README.md` na raiz: o que é, stack, como correr localmente, variáveis de ambiente, diagrama de arquitetura.
- [x] `backend/README.md`: endpoints, payloads, códigos de erro, modelos suportados, como adicionar novo provider.
- [x] Substituir `frontend/README.md` (antes era o template do CRA).
- [ ] Documentar endpoints via OpenAPI — tipar responses com Pydantic (ex. `ProcessResponse`) para o `/docs` ficar útil.

### Tooling
- [x] Backend: `ruff` (lint + format) e `mypy` configurados em `backend/pyproject.toml`; `backend/requirements-dev.txt` criado.
- [x] Frontend: `.eslintrc.json` (extends `react-app` + `prettier`), `.prettierrc`, `.prettierignore`; scripts `lint`, `lint:fix`, `format`, `format:check`.
- [x] `.editorconfig` na raiz (LF, UTF-8, 2 espaços; 4 em Python; tabs em Makefile).
- [x] `Makefile` na raiz com alvos `install`, `dev-backend`, `dev-frontend`, `lint`, `format`, `typecheck`, `test`, `build`, `clean`.

### CI
- [x] GitHub Actions em `.github/workflows/ci.yml` — jobs backend (`ruff check` + `ruff format --check` + `mypy`) e frontend (`eslint` + `prettier --check` + `build`). Corre em PRs para `main` e em push para `main`. Concurrency com cancel-in-progress. Testes ficam para a Fase 4.

---

## Fase 2 — Robustez do backend 🟡

- [ ] Logging estruturado (JSON) com `structlog` ou `loguru`; substituir todos os `print`. Incluir `request_id` por chamada.
- [ ] Corrigir typo `reponse` → `response` em `backend/llm_client.py:10`.
- [ ] Timeouts explícitos na chamada ao OpenRouter (ex. 60 s) + retry com backoff (`tenacity`) para erros transitórios.
- [ ] Gestão robusta de ficheiros temporários em `backend/file_utils.py`: usar `try/finally` ou context manager custom para garantir cleanup mesmo em exceção.
- [ ] Versionar a API: mover endpoints para `/api/v1/...`.
- [ ] Error handling centralizado com `exception_handler` do FastAPI — respostas JSON consistentes (`{error, code, request_id}`).
- [ ] Rate limiting básico (ex. `slowapi`) por IP no endpoint `/process-file`.
- [ ] Schemas Pydantic para request/response (tipar o output do LLM).
- [ ] Processamento pesado (PDFs grandes, áudio longo) em background task ou com streaming (`StreamingResponse` / SSE) para não bloquear o worker.
- [ ] Health check `/healthz` que verifica conectividade ao OpenRouter.

---

## Fase 3 — UX do frontend 🟡

- [ ] **Error handling visível:** substituir `console.error` em `App.js:195` por Snackbar/Alert MUI com mensagem clara + botão "tentar novamente".
- [ ] Validação client-side antes de submeter: tamanho, tipo, prompt vazio.
- [ ] Estado de loading mais informativo (ex. "a extrair PDF…", "a gerar mapa…") em vez de spinner genérico.
- [ ] Preencher a aba **"Resumo do Modelo"** (campo `model_summary` já vem do backend mas nunca é usado).
- [ ] Toast de sucesso após gerar mapa.
- [ ] Fallback se o modelo default do OpenRouter estiver indisponível — pedir lista de modelos disponíveis ao backend.
- [ ] Persistir último modelo escolhido (em `localStorage`, é aceitável para preferências não-sensíveis).
- [ ] Acessibilidade: rever contraste, `aria-label` em botões só com ícone, navegação por teclado nas abas.
- [ ] Responsividade em mobile (o PDF viewer e o mapa mental precisam de tratamento especial).

---

## Fase 4 — Testes 🟡

- [ ] Backend: `pytest` + `httpx.AsyncClient`. Cobrir:
  - happy path de cada tipo de input (PDF, áudio, prompt);
  - validação de input (ficheiro demasiado grande, MIME inválido);
  - erro do LLM (mockar OpenRouter);
  - cleanup de ficheiros temporários.
- [ ] Frontend: `@testing-library/react`. Cobrir:
  - render inicial;
  - fluxo de submissão com mock do axios;
  - mostrar erro quando o backend falha;
  - troca de aba.
- [ ] Cobertura mínima inicial: 60 % backend, 40 % frontend. Relatar no CI.

---

## Fase 5 — Features & polish 🟢

- [ ] Cache de respostas do LLM por hash de input (Redis ou in-memory + TTL) para poupar custos/latência em repetições.
- [ ] Histórico local de mapas gerados (IndexedDB) com possibilidade de reabrir.
- [ ] Export adicional: SVG e Markdown (o `.md` já existe internamente — expor como download).
- [ ] Tema escuro (MUI `ThemeProvider`).
- [ ] i18n (PT/EN) com `react-i18next`.
- [ ] Suporte a mais inputs: URL de artigo (fetch + extração de texto), imagem (OCR via Tesseract).
- [ ] Permitir edição manual do mapa antes do export.

---

## Fase 6 — Deploy 🟢

- [ ] `Dockerfile` para backend (multi-stage, non-root user).
- [ ] `Dockerfile` para frontend (build + nginx servindo estáticos).
- [ ] `docker-compose.yml` para desenvolvimento local.
- [ ] Script/template de deploy (Fly.io, Railway, ou VPS + Caddy).
- [ ] Variáveis de ambiente geridas por secrets do provider, não por `.env` em produção.
- [ ] Monitorização básica: logs centralizados + alerta em erro 5xx (Sentry ou equivalente).

---

## Ordem de ataque sugerida

1. **Fase 0** (1 sessão) — segurança, não negociável.
2. **Fase 1** (1–2 sessões) — documentação + tooling + CI; torna o resto mais rápido e seguro.
3. **Fase 2 + Fase 3 em paralelo** (2–3 sessões) — robustez e UX.
4. **Fase 4** (1–2 sessões) — testes só depois de a API estabilizar, senão reescrevem-se.
5. **Fase 5 e 6** — quando o core estiver sólido.

---

## Convenções para os próximos commits

- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- 1 PR = 1 tema; nada de PRs gigantes que misturam segurança, features e refactor.
- Cada PR fecha 1+ itens desta lista (referenciar a linha no corpo do PR).
