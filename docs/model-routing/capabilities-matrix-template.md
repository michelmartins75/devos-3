# DevOS 3.0 — Model Capabilities Matrix

> Documento de referência para o orchestrator do DevOS 3.0. Consumido para
> decidir qual modelo acionar por tipo de tarefa. Gerado a partir das
> respostas ao `prompt-avaliacao-modelos-ia.md`, rodado individualmente em
> cada modelo do stack.
>
> **Última atualização:** PREENCHER
> **Atualizado por:** Michel Martins
> **Versão do schema:** 1.0

---

## 1. Regra de precedência (leia antes da tabela)

O orchestrator deve aplicar os critérios **nesta ordem**, parando no primeiro
que decide:

1. **Gate DSGVO** — se a tarefa toca dado real de tenant de cliente
   (não sintético, não fixture de teste), somente modelos com
   `dsgvo_local_eligible: true` são elegíveis. Isso descarta qualquer
   modelo cloud, independente de qualidade. Sem exceção.
2. **Papel funcional** — dentro do conjunto elegível, filtrar por
   `recommended_devos_roles` compatível com a tarefa (`spec_compiler`,
   `ct172_validator`, `codegen_client_facing`, `codegen_internal`,
   `refactor_large_context`, `architecture_review`, `docs_generation`).
3. **Desempate** — entre os que sobraram: menor `latency_tier` para tarefas
   do loop interno (CT172), maior qualidade de reasoning para o loop externo
   de release, menor `cost_tier` em caso de empate real.

---

## 2. Tabela-resumo

| Model ID | Provider | Via | Deployment | DSGVO-eligible | Context (tokens) | Papéis recomendados | Latência | Custo |
|---|---|---|---|---|---|---|---|---|
| PREENCHER | | | local/cloud | true/false | | | | |

*(uma linha por modelo real avaliado — não por ferramenta)*

---

## 3. Mapeamento tarefa → modelo preferido

| Tarefa DevOS | Modelo preferido | Fallback | Motivo |
|---|---|---|---|
| Spec Compiler (issue → plano) | PREENCHER | PREENCHER | |
| CT172 — validação semântica (loop interno) | PREENCHER | PREENCHER | deve ser local; foco em determinismo, não criatividade |
| Codegen — projeto cliente com dado real | PREENCHER (obrigatoriamente DSGVO-eligible) | PREENCHER | gate DSGVO |
| Codegen — projeto interno ForgeWorks | PREENCHER | PREENCHER | |
| Refactor de contexto grande | PREENCHER | PREENCHER | |
| Architecture review / decisões de design | PREENCHER | PREENCHER | |
| Geração de docs / specs legíveis | PREENCHER | PREENCHER | |

---

## 4. Perfis detalhados por modelo

> Cole aqui o bloco YAML retornado por cada modelo, um por sub-seção.
> Revise valores que pareçam incorretos (context window e limites são os
> mais comumente errados por auto-relato) e documente a correção em `notes`.

### 4.1 PREENCHER (model_id)

```yaml
model_id: ""
provider: ""
accessed_via: ""
deployment: ""
dsgvo_local_eligible: 
context_window_tokens: 
max_output_tokens: 
agentic_tool_use:
  supports_function_calling: 
  can_drive_shell_autonomously: 
  can_edit_files_autonomously: 
  can_run_multi_step_plans_unsupervised: 
code_capabilities:
  strong_languages: []
  weak_or_unreliable_in: []
  good_at_refactor: 
  good_at_greenfield_generation: 
  good_at_code_review_static_analysis: 
reasoning_profile:
  good_at_architecture_decisions: 
  good_at_spec_compilation: 
  good_at_semantic_test_validation: 
  known_failure_modes: []
performance:
  latency_tier: ""
  cost_tier: ""
  determinism_for_validation_tasks: ""
recommended_devos_roles: []
not_recommended_for: []
self_assessed_confidence_in_this_answer: ""
notes: ""
```

*(duplicar esta sub-seção para cada modelo avaliado: Claude via Claude Code,
GPT via Codex, Gemini, cada modelo local no Ollama/Terra, e o modelo ativo
no Cursor se distinto dos anteriores)*

---

## 5. Notas de manutenção

- Revalidar esta matriz sempre que: (a) um provider lançar nova versão de
  modelo já em uso, (b) um novo modelo local for instalado no Terra, ou
  (c) o orchestrator relatar taxa de erro/retry anormal associada a um
  papel específico.
- Auto-relato de modelo não é fonte confiável para `context_window_tokens`
  e `max_output_tokens` — cruzar com documentação oficial do provider antes
  de usar esses valores em lógica de chunking do orchestrator.
- `dsgvo_local_eligible` é o único campo que o orchestrator deve tratar
  como **hard constraint**. Todos os outros são heurísticas de ranking.
