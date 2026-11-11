# Telarch Hosted Server: Endpoint Reference

## Endpoint

- `https://telarch.ai/mcp`: MCP Streamable HTTP, JSON-RPC 2.0, no authentication, no session.
- Stateless: nothing from a call is stored, and no call can read another call's data.
- This plugin runs nothing on your machine and has no environment variables. Local storage is what the separate local plugin provides.

## Requests

- `POST` with `Content-Type: application/json`; the answer is JSON. A `POST` with another content type is refused (415); an `Accept` header that excludes JSON is refused (406).
- `MCP-Protocol-Version`: an unsupported value is refused (400).
- `GET` with `Accept: text/event-stream` opens an event stream; any other `GET` gets 405.
- A request with an `Origin` header is served only for the origins the server lists (the Telarch and Perseus Computing sites and ChatGPT); other origins get 403. Requests without `Origin` (server-to-server clients) are served.

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

- Unknown tool, or arguments that do not match the tool's input schema: JSON-RPC error -32602.
- A message that is not a valid JSON-RPC request: -32600.
- A rule of the tool refuses the call (for example `ScopeIsolationError`, `EpistemicTrustViolation`, `StaleFencingTokenError`, `FloatPayloadError`): a tool result with `isError: true` and the rule's own sentence.
