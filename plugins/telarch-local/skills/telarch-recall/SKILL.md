---
name: telarch-recall
description: Use when recalling Telarch context from Kibisis or Harpe. Query memories, inspect projections, and synthesize scoped context.
---

# Telarch Recall

Query durable facts, decisions, and project state from the Telarch Suite (TCI) cognitive infrastructure.

## Operational Rules

1. **Always query Kibisis for durable project facts**: Read vault memories via `kibisis_recall` rather than guessing or parsing flat files.
2. **Filter by Category**: Narrow recall queries by category (`decision`, `project_state`, `convention`, `research_triage`).
3. **Respect Epistemic States**: Verified memories represent established ground truth; candidate memories represent unpromoted model writes.
4. **Deterministic Budgeting**: When preparing large context blocks, use Harpe knapsack pruning to avoid context overflow.

## Supporting References

- See [Recall CLI Reference](references/cli.md) for terminal and Python commands.
- See [Schema Reference](references/schema.md) for Kibisis attributes and OKF projections.
