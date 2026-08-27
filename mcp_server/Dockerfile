# OpsPilot MCP server - containerised.
# Same shape as harness/Dockerfile - see that one for the reasoning
# behind the instruction ordering (requirements before code, for layer
# caching) and why not COPY . .. Build context is the repo root (see
# docker-compose.yml), not this mcp_server/ directory - so paths below
# are relative to the root, same pattern as harness/Dockerfile.

FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server/server.py .

EXPOSE 8000

CMD ["python", "server.py"]
