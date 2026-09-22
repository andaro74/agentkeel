# refagent's runtime image (SPEC/01 §6). Built and pushed by deploy.yml,
# pulled by digest: the repository is tag-immutable, so a digest is the
# bytes and cannot be moved to others.
#
# What is in it: the bundle (manifest, prompt, tool contract, the agent and
# its server) and boto3. What is not: data/, so nothing in the image can
# answer from a copy of the rights table. The deployed runtime reads the
# table through the VPC's gateway endpoint or it does not answer.
#
# arm64, pinned here and not left to the machine that builds it: AgentCore
# Runtime runs arm64 images only (M02 PR 2). deploy.yml builds on an arm64
# runner and refuses any other architecture before it pushes.
FROM --platform=linux/arm64 public.ecr.aws/docker/library/python:3.14-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install --no-cache-dir "boto3>=1.43.97" "jsonschema>=4.26.0"

COPY agents/__init__.py agents/__init__.py
COPY agents/refagent/__init__.py agents/refagent/agent.py agents/refagent/server.py agents/refagent/prompt.txt agents/refagent/manifest.yaml agents/refagent/
COPY agents/refagent/tools/ agents/refagent/tools/

# Not root: the runtime does not need it and the boundary does not care.
RUN useradd --create-home --uid 10001 refagent && chown -R refagent /app
USER refagent

EXPOSE 8080
CMD ["python", "-m", "agents.refagent.server"]
