# Telarch Recall CLI and Tool Interface

This reference describes the recall interfaces for Kibisis and Harpe.

## Tool Interface

When operating inside Hermes, recall is performed via the `kibisis_recall` tool:

```python
kibisis_recall(
    query="keyword search terms",
    category="decision",      # Optional: decision, convention, project_state, etc.
    epistemic_state="verified", # Default: verified (or candidate)
    limit=10,
    match="any"               # 'any' or 'all'
)
```

## CLI Interface

From the terminal environment on Greg / Docker container:

```bash
# Query active verified memories
python3 -m kibisis query "Telarch roadmap" --category project_state

# Query candidates pending admission
python3 -m kibisis query "candidate" --state candidate --limit 20

# Query with bitemporal point-in-time evaluation
python3 -m kibisis query "phase" --as-of 1730600000
```

## Harpe Context Synthesis

Harpe packs context deterministically within token budgets:

```bash
# Evaluate context budget
python3 -m harpe budget --target-tokens 8000

# Synthesize context blocks
python3 -m harpe synthesize --items /path/to/context.json
```
