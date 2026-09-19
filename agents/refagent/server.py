"""refagent inside AgentCore Runtime: the two endpoints the runtime calls.

`POST /invocations` takes `{"question": "..."}` and returns the raw
observation `agent.answer` writes — the same shape the runner writes on a
PR, so the envelope does not change when the subject moves from the runner
to the deployed runtime (ruling l). `GET /ping` is the health check.

The runtime reads the rights table from DynamoDB
(`AGENTKEEL_RIGHTS_TABLE`, set by `GovernedAgent`), through the VPC's
gateway endpoint. There is no way out of that VPC (ADR-0006), so if the
table is missing the answer says so; it does not fall back to the file,
which is not in the image.

This server judges nothing and writes no envelope (P5).
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import boto3

from agents.refagent import agent

PORT = 8080
REGION = os.environ.get("AWS_REGION", "us-west-2")
MODEL_ID = os.environ.get("AGENTKEEL_MODEL_PROFILE", "us.anthropic.claude-sonnet-5")
TABLE = os.environ.get("AGENTKEEL_RIGHTS_TABLE")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._send(200 if self.path == "/ping" else 404, {"status": "healthy" if self.path == "/ping" else "no"})

    def do_POST(self) -> None:
        if self.path != "/invocations":
            return self._send(404, {"error": "only /invocations"})
        body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        try:
            question = json.loads(body or b"{}")["question"]
        except (ValueError, KeyError) as exc:
            return self._send(400, {"error": f"a JSON object with a question: {exc}"})
        try:
            rows, source = agent.rights_rows(TABLE, boto3.client("dynamodb", region_name=REGION))
            self._send(200, agent.answer(self.bedrock, question, MODEL_ID, rows, source))
        except Exception as exc:  # noqa: BLE001 - a failed call is an observation too
            self._send(200, {"error": f"{type(exc).__name__}: {exc}"})

    @property
    def bedrock(self) -> Any:
        if not hasattr(self.server, "_bedrock"):
            self.server._bedrock = boto3.client("bedrock-runtime", region_name=REGION)
        return self.server._bedrock

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(fmt % args)  # to the log group, not to stderr's default format


if __name__ == "__main__":
    print(f"refagent on :{PORT}, model {MODEL_ID}, table {TABLE or '(none: the file is not in the image)'}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
