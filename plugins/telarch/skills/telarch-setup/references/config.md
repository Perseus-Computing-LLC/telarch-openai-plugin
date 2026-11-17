# Telarch Hosted Server: Endpoint Reference

## Endpoint

- `https://telarch.ai/mcp`: MCP Streamable HTTP, JSON-RPC 2.0, no authentication, no session.
- Stateless: nothing from a call is stored, and no call can read another call's data.
- This plugin runs nothing on your machine and has no environment variables. Local storage is what the separate local plugin provides.

## Requests

- `POST` with `Content-Type: application/json`; the answer is JSON. A `POST` with another content type is refused (415); an `Accept` header that excludes JSON is refused (406).
- `MCP-Protocol-Version`: an unsupported value is refused (400).
- `GET` with `Accept: text/event-stream` opens an event stream; any other `GET` gets 405.
- A request with an `Origin` header is served only for the origins the server lists (the Telarch and Perseus Computing sites, ChatGPT, and the frame ChatGPT renders the inspector in); other origins get 403. Requests without `Origin` (server-to-server clients) are served.

## Limits

A call above a limit is refused with an error that names the limit; nothing is cut down silently.

| limit | value |
|---|---|
| request body | 1,048,576 bytes |
| JSON nesting depth | 64 |
| messages in one batch | 16 |
| items, records or events in one call | 4,096 |
| `knapsack_dp` table cells (candidates x budget steps) | 4,000,000 |
| token quantities (`total_budget`, reserves) | 2,147,483,647 |

## Errors

- Unknown tool: JSON-RPC error -32602.
- Arguments that do not match the tool's input schema: JSON-RPC error -32602 with `error.data = {"code": "InvalidArguments", "path": ...}`. `path` is written from the arguments, as in `items[0].role`; it is `""` when the arguments object itself is at fault (an undeclared argument, or arguments that are not an object).
- A message that is not a valid JSON-RPC request: -32600.
- A rule of the tool refuses the call: a tool result with `isError: true`, the rule's own sentence as text, and `structuredContent.error = {"code", "path", "message"}`. `message` is that sentence. `path` names the argument at fault and is `null` when no single argument is.

The codes do not change between versions; a code is the error name its sentence starts with, without a trailing `Error`.

| code | refused because | path |
|---|---|---|
| `InvalidArguments` | the arguments do not match the input schema (error -32602) | the value at fault |
| `FloatPayload` | a payload holds a number that is not an integer | the number, as in `events[0].payload.n` |
| `UnsafeInteger` | a payload holds an integer beyond 2**53 - 1 | the number |
| `PayloadTooDeep`, `UnsupportedPayload` | a payload is nested too deeply, or holds a value JSON cannot carry | the value |
| `PrevHashFormat` | `prev_hash` is not 64 lowercase hex characters or `GENESIS` | `prev_hash` |
| `SequenceRequired` | a chain continued from a `prev_hash` has no `sequence` on its first event | `events[0].sequence` |
| `SequenceOrder` | a `sequence` does not follow the one before it | that `sequence` |
| `DuplicateItemId` | two items share an id | the second `id` |
| `KnapsackTooLarge` | `knapsack_dp` would need more than 4,000,000 table cells | `null` |
| `UnknownPolicy` | the policy is not one the server has | `policy` |
| `ScopeIsolation` | `requested_scope` differs from `active_scope` | `requested_scope` |
| `EpistemicTrustViolation` | a write with origin `model` asks for `verified` | `write_attempt.epistemic_state` |
| `DuplicateRecordKey` | two records share category and key | the second `key` |
| `SupersessionLoop` | records supersede each other in a loop | one `supersedes_key` of the loop |
| `StaleFencingToken` | the token is below `highest_token_seen` | `fencing_token` |
| `LeaseClockMissing` | an expiry was given without `now_epoch` | `now_epoch` |
| `LeaseExpired` | the lease expired before `now_epoch` | `lease_expires_epoch` |

A chain that fails `argus_audit_verify` is not a refusal: the call succeeds and reports `valid: false` with `first_broken_sequence` and `error_detail`.
