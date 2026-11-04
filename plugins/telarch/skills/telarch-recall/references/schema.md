# Telarch Memory and OKF Schema Reference

This reference details the schema conventions for Telarch memories and OKF projections.

## Kibisis Memory Schema

Memories stored in the Kibisis vault follow standard attributes:

- `category`: Taxonomy category (e.g., `decision`, `convention`, `project_state`, `research_triage`).
- `key`: Unique identifier string within the category.
- `epistemic_state`: `verified`, `candidate`, `disputed`, or `revoked`.
- `content`: Plain markdown or structured summary text.
- `valid_from` / `valid_until`: Bitemporal validity timestamps.
- `sensitivity`: `normal` or `confidential`.

## OKF v0.2 Projection (P13 / P14)

Under Open Knowledge Format (OKF) v0.2:

1. **Concept Bundles**: Exported memory concepts with YAML frontmatter containing:
   - `okf_version: "0.2.0"`
   - `type: "Concept"`
   - `title`: Short title string.
   - `description`: 1-2 sentence description.
2. **Attested Computation Cards**: Computation execution sidecars (`*.card.json`).
3. **Index and Log**: Every bundle exports an `index.md` listing concept digests and a `log.md` detailing change history.
