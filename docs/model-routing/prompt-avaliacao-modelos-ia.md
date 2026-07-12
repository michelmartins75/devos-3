# Prompt de Auto-Avaliação de Modelos — DevOS 3.0

**Propósito:** este prompt é executado, *sem alterações*, em cada engine/modelo do stack (Claude Code, Codex, Gemini, modelos locais via Ollama no Terra, e o(s) modelo(s) selecionado(s) no Cursor). A saída estruturada de cada execução alimenta o `capabilities-matrix.md` que o orchestrator do DevOS 3 usa para decidir qual modelo acionar por tipo de tarefa.

**Importante ao rodar:** não edite o prompt entre execuções — a comparabilidade das respostas depende de todas responderem exatamente à mesma pergunta. Rode uma vez por modelo subjacente real (não por ferramenta — se o Cursor está configurado com um modelo que já foi avaliado via outra via, não repita).

---

## O prompt (copiar e colar integralmente)

```
Você está sendo avaliado como um candidato a "worker model" dentro do
DevOS 3.0, o motor de consolidação de projetos da ForgeWorks Digital
(Portalliz, zev-lur, NAU, albaTours Cockpit, entre outros).

Contexto da arquitetura que você está avaliando seu encaixe:
- CT130: ambiente de desenvolvimento principal, multi-tenant com isolamento
  nativo (PostgreSQL 16 + RLS), acesso distribuído via Tailscale.
- CT172: loop de validação interno — API Fastify, análise semântica via
  Ollama local, SEM credenciais de push/write/deploy. Sua única função é
  validar/testar, nunca gravar.
- Loop externo de release: gera as entregas finais para o cliente.
- Terra: nó de compute dedicado (Proxmox, Tesla P40). Restrição de design:
  qualquer workload que toque dado real de tenant de cliente DEVE rodar
  localmente no Terra (compliance DSGVO). Isso é um hard gate, não uma
  preferência de qualidade.

Sua tarefa: responda com precisão técnica e SEM linguagem de marketing.
Se você não sabe um valor exato, diga "não sei" ou dê uma estimativa
marcada como tal — não invente números. Responda TODO o bloco abaixo em
YAML, dentro de um único bloco de código, seguindo exatamente este schema:

---
model_id: ""                # nome exato do modelo/versão, ex: "claude-sonnet-4-6"
provider: ""                 # Anthropic / OpenAI / Google / Meta / Mistral / outro
accessed_via: ""             # Claude Code / Codex CLI / Gemini CLI / Ollama / Cursor / API direta
deployment: ""               # "local" ou "cloud"
dsgvo_local_eligible: true/false   # pode processar dado real de tenant cliente sem violar DSGVO?
context_window_tokens: 0     # número, ou "unknown"
max_output_tokens: 0
agentic_tool_use:
  supports_function_calling: true/false
  can_drive_shell_autonomously: true/false
  can_edit_files_autonomously: true/false
  can_run_multi_step_plans_unsupervised: true/false
code_capabilities:
  strong_languages: []       # ex: [python, typescript, sql]
  weak_or_unreliable_in: []
  good_at_refactor: true/false
  good_at_greenfield_generation: true/false
  good_at_code_review_static_analysis: true/false
reasoning_profile:
  good_at_architecture_decisions: true/false
  good_at_spec_compilation: true/false   # transformar spec/issue em plano de execução
  good_at_semantic_test_validation: true/false  # papel tipo CT172
  known_failure_modes: []    # ex: ["alucina paths inexistentes em specs grandes"]
performance:
  latency_tier: ""           # baixa / média / alta
  cost_tier: ""              # gratuito(local) / baixo / médio / alto
  determinism_for_validation_tasks: ""  # alta / média / baixa
recommended_devos_roles: []  # dentre: ["spec_compiler","ct172_validator",
                              #  "codegen_client_facing","codegen_internal",
                              #  "refactor_large_context","architecture_review",
                              #  "docs_generation","none"]
not_recommended_for: []
self_assessed_confidence_in_this_answer: ""  # alta / média / baixa
notes: ""                    # qualquer ressalva relevante, 1-3 frases
---

Regras de resposta:
1. Só o bloco YAML. Sem texto antes ou depois.
2. Se accessed_via for Ollama, informe o nome exato do modelo/tag local
   (ex: "llama3.1:70b-instruct-q4"), não "Ollama" como model_id.
3. dsgvo_local_eligible só é true se deployment for "local" E o modelo
   rodar inteiramente no Terra sem chamada de rede externa.
4. Seja rigoroso em known_failure_modes — isso é o campo mais importante
   para decisões de roteamento seguras. Não omita fraquezas conhecidas.
```

---

## Onde rodar

| Ferramenta/Interface | Modelo(s) subjacente(s) a avaliar separadamente |
|---|---|
| Claude Code | modelo Claude ativo na sessão |
| Codex (CLI/API) | modelo GPT ativo |
| Gemini (CLI/API) | modelo Gemini ativo |
| Cursor | verificar qual modelo está selecionado — pode coincidir com um já avaliado acima |
| Ollama (Terra) | um YAML **por modelo local instalado**, não um genérico para "Ollama" |

## Depois de rodar

Cole cada bloco YAML retornado na seção correspondente do `capabilities-matrix-template.md` (arquivo companheiro). Não edite os valores manualmente antes de revisar — se um modelo mentir ou errar sobre si mesmo (comum em context window e limites), corrija com fonte oficial e marque `self_assessed_confidence_in_this_answer` como divergente nos notes.
