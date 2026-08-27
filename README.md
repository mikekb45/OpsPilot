# OpsPilot

A simulated AI incident-investigation assistant, built as a hands-on AI
Engineering learning project.

## Project Goal

I'm building OpsPilot to genuinely understand how agentic AI applications
work under the hood — not by using an agent framework, but by writing the
Claude API calls, tool calling, and the agentic control loop myself. The
target scenario: a user reports something like "Orders have stopped
processing," and OpsPilot investigates a simulated environment (dummy data
only), gathers evidence via tools, consults some reference documentation, and
produces a diagnosis with supporting evidence, likely root cause, confidence,
and a recommended next step.

This is a portfolio/learning project. It does not connect to any real
production system, infrastructure, database, or monitoring tool.

## Learning Objectives

- The Anthropic Messages API directly (system prompts, messages, tool
  definitions/calls/results, stop reasons, tokens)
- What makes an application "agentic": the relationship between an LLM,
  tools, state, the control loop, and the harness that runs it
- Writing my own agentic loop and AI harness from scratch (state, tool
  execution, error handling, iteration limits, completion detection)
- Persisting agent conversation history in Redis, once the in-memory
  harness is built and understood — a deliberate detour to pick up a
  widely-used piece of backend infrastructure, on top of (not instead of)
  understanding conversation state as plain Python data first
- Plain Python tool calling, then what MCP adds on top of that
- Retrieval-augmented generation with ChromaDB, implemented directly
  (chunking, embeddings, similarity search) rather than via a framework
- Testing and evaluating an AI system with pytest and small deterministic
  scenarios
- Basic containerisation with Docker once the app works locally

## Planned Architecture

The core loop is built and working:

```
User → Claude → tool needed? → harness executes tool → tool result → Claude
→ ... → final diagnosis
```

`harness/main.py` implements this today with a hand-rolled agentic loop
(iteration cap included), talking to a separate `mcp_server/server.py`
process over the Model Context Protocol instead of calling local Python
functions directly. Two dummy tools (`get_queue_status`, `get_recent_errors`)
are defined once, on the MCP server, and discovered dynamically by the
harness at startup - no tool schemas or dispatch logic hardcoded on the
client side. Unknown-tool and tool-execution error handling live on the
server side of that boundary now too, reported back via the protocol's own
`is_error` field.

Conversation history is no longer memory-only: it's persisted to a local
Redis instance at every safe checkpoint, so an interrupted run can be
resumed rather than losing all progress, and a finished conversation can be
reloaded and shown without re-calling the API.

All three pieces - `harness`, `mcp-server`, and `redis` - run as their own
Docker Compose service, each in its own top-level directory
(`harness/`, `mcp_server/`), talking to each other over the network by
Compose service name rather than `localhost`.

Later stages (not yet started): a ChromaDB-backed retrieval step over a
handful of small fictional docs in `knowledge/` → pytest-based tests and
evaluation scenarios.

## Technology

- Python 3.14, `venv`, `pip`, `requirements.txt`
- Anthropic Python SDK (used directly, no agent framework)
- Redis, for persisting conversation history across runs — introduced
  after the in-memory harness was built and understood; one `redis`
  service in `docker-compose.yml`, alongside the harness and MCP server
- ChromaDB for retrieval (used directly, no LangChain/LlamaIndex)
- MCP, via the official Python SDK's `MCPServer`/`Client` classes - tools
  defined once on a standalone server, discovered and called by the
  harness over HTTP rather than hardcoded on the client side
- pytest
- Docker - every service (`harness`, `mcp-server`, `redis`) containerised
  and orchestrated via a single `docker-compose.yml`
- Plain CLI — no web framework unless a clear need appears

## Development Approach

This project is being built deliberately incrementally, in small
feature-branch-sized steps, specifically so that each AI Engineering concept
(tool calling, the agentic loop, the harness, MCP, RAG) is understood before
the next one is introduced. Nothing is built ahead of where the learning
currently is.

## Project Status

The following stages are complete:

- A plain call to the Anthropic Messages API (no tools).
- Tool calling: one manual request → `tool_use` → execute → `tool_result`
  round-trip.
- The agentic loop: the round-trip above, repeated until Claude stops
  asking for tools, with an iteration cap.
- The AI harness: dispatching to the correct tool by name (not just a
  single hardcoded function), and error handling around tool execution
  (an unknown tool name or a failing tool call both produce a graceful
  error result instead of crashing).
- Redis-backed conversation persistence: the conversation survives across
  separate runs, checkpointed at every safe point, and an interrupted
  investigation can be resumed rather than restarted.
- MCP: tool definitions and execution moved off the harness entirely, onto
  a standalone `mcp-server` the harness talks to over HTTP. Both tools
  (`get_queue_status`, `get_recent_errors`) are discovered dynamically, not
  hardcoded client-side.
- Full containerisation: `harness`, `mcp-server`, and `redis` each run as
  their own Docker Compose service.

Not yet started: RAG/ChromaDB and testing/evaluation.

## Planned Development

```
Python foundation → Anthropic API (no tools) → tool calling → agentic loop
→ AI harness → Redis-backed conversation persistence → MCP → RAG/ChromaDB
→ integration → testing/evaluation → Docker → documentation/polish
```

## Security

Running locally, the Anthropic API key is stored only in a local `.env`
file, which is listed in `.gitignore` and is never committed. `.env.example`
documents the required variable name with a placeholder value.

Running containerised, the key is instead injected as a Docker Compose file
secret, sourced from a local, git-ignored `anthropic_api_key.txt`
(`anthropic_api_key.txt.example` documents the placeholder). Deliberately
not passed as an environment variable in this case: anything that resolves
a container's final config (`docker compose config`, `docker inspect`, ...)
prints environment variables in plaintext, which is exactly how this key
was exposed once during development. A file-based secret was never
represented as an environment variable in the first place, so there's
nothing for those commands to leak.

No secrets are put into source code, logs, or documentation.
