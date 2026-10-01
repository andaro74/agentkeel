# An agent from the template's runtime image (SPEC/06 section 6, R3). Security
# seat. Built by deploy.yml on main in a job that holds no AWS credentials,
# from the agent repository's folder, which deploy.yml checks out as data at
# agents/<name>/; pushed to agentkeel/<name> by digest in the job that does.
#
# The platform's Dockerfile, not the agent's: an agent repository's own
# Dockerfile, if it has one, is never read, so nothing the developer writes
# runs at build time. What is copied is the bundle refagent's image carries
# (manifest, prompt, tool contract, the agent and its server), from the
# agent's folder, into the package `agent`; the example agent the template
# ships imports its own module relatively for that reason. Not data/: the
# runtime reads its rights table through the VPC's gateway endpoint.
#
# arm64, as refagent's: AgentCore Runtime runs arm64 images only.
FROM --platform=linux/arm64 public.ecr.aws/docker/library/python:3.14-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install --no-cache-dir "boto3>=1.43.97" "jsonschema>=4.26.0"

ARG AGENT
COPY agents/${AGENT}/__init__.py agents/${AGENT}/agent.py agents/${AGENT}/server.py agents/${AGENT}/prompt.txt agents/${AGENT}/manifest.yaml agent/
COPY agents/${AGENT}/tools/ agent/tools/

RUN useradd --create-home --uid 10001 agent && chown -R agent /app
USER agent

EXPOSE 8080
CMD ["python", "-m", "agent.server"]
