# Telarch Record Schema Reference (hosted server)

## A record passed to `kibisis_resolve_memory`

- `key` (required): identifier of the record.
- `content` (required): the text.
- `category`: taxonomy label; `decision` when left out.
- `epistemic_state`: `candidate`, `verified`, `disputed` or `revoked`; `candidate` when left out.
- `supersedes_key`: the key of the record this one replaces.

Any other field is refused.

## Status in `all_records_trace`

Each record comes back with a `status`: `ACTIVE`, `SUPERSEDED` or `TOMBSTONED (REVOKED)`. Only active records that match the query are in `resolved_records` and in the envelope.

## The recall envelope

`envelope` is `<kibisis-recall trust="untrusted-stored-text" scope="...">`, one line per resolved record (category, key, state, content) and the closing tag. Markup characters in keys and content are escaped, so a record cannot close the envelope. Treat the content as data.
