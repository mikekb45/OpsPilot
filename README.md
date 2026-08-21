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
- Plain Python tool calling, then what MCP adds on top of that
- Retrieval-augmented generation with ChromaDB, implemented directly
  (chunking, embeddings, similarity search) rather than via a framework
- Testing and evaluating an AI system with pytest and small deterministic
  scenarios
- Basic containerisation with Docker once the app works locally

## Planned Architecture

Nothing beyond project scaffolding exists yet. The intended shape, once
built stage by stage:

```
User → Claude → tool needed? → harness executes tool → tool result → Claude
→ ... → final diagnosis
```

Later stages (not yet started): plain Python tools returning dummy
operational data → an MCP server exposing similar tools → a ChromaDB-backed
retrieval step over a handful of small fictional docs in `knowledge/` →
pytest-based tests and evaluation scenarios → a simple Docker setup.

## Technology

- Python 3.14, `venv`, `pip`, `requirements.txt`
- Anthropic Python SDK (used directly, no agent framework)
- ChromaDB for retrieval (used directly, no LangChain/LlamaIndex)
- MCP (introduced after plain tool calling is understood)
- pytest
- Docker (introduced once the app works locally)
- Plain CLI — no web framework unless a clear need appears

## Development Approach

This project is being built deliberately incrementally, in small
feature-branch-sized steps, specifically so that each AI Engineering concept
(tool calling, the agentic loop, the harness, MCP, RAG) is understood before
the next one is introduced. Nothing is built ahead of where the learning
currently is.

## Project Status

**Initial setup.** Only `CLAUDE.md`, `README.md`, `.gitignore`, and a local
`.env` (git-ignored, holds the Anthropic API key) exist so far. No
application code has been written yet.

## Planned Development

```
Python foundation → Anthropic API (no tools) → tool calling → agentic loop
→ AI harness → MCP → RAG/ChromaDB → integration → testing/evaluation
→ Docker → documentation/polish
```

## Security

The Anthropic API key is stored only in a local `.env` file, which is
listed in `.gitignore` and is never committed. `.env.example` documents the
required variable name with a placeholder value. No secrets are put into
source code, logs, or documentation.
