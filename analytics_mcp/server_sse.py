#!/usr/bin/env python

"""SSE transport entry point for deploying the MCP server on Render.com."""

import json
import os
import tempfile

import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

import analytics_mcp.coordinator as coordinator


def _setup_credentials():
    """Write service account JSON from env var to a temp file.

    Render.com stores the JSON key content in GOOGLE_APPLICATION_CREDENTIALS_JSON.
    google.auth.default() reads from the file path in GOOGLE_APPLICATION_CREDENTIALS.
    """
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if creds_json and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        tmp.write(creds_json)
        tmp.flush()
        tmp.close()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name


def create_app() -> Starlette:
    """Create the Starlette ASGI app with SSE transport."""
    _setup_credentials()

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await coordinator.app.run(
                streams[0],
                streams[1],
                coordinator.app.create_initialization_options(),
            )

    app = Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
