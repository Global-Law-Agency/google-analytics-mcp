FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY analytics_mcp/ analytics_mcp/

RUN pip install --no-cache-dir . uvicorn starlette sse-starlette

EXPOSE 8000

CMD ["uvicorn", "analytics_mcp.server_sse:app", "--host", "0.0.0.0", "--port", "8000"]
