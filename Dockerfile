FROM python:3.11-alpine3.24@sha256:f2cdc43fcddbabe870f53750cbdcc01ae4aa75b1959351252457fde88f91d20f AS dependencies
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r requirements.txt && /opt/venv/bin/pip uninstall --yes pip setuptools wheel

FROM python:3.11-alpine3.24@sha256:f2cdc43fcddbabe870f53750cbdcc01ae4aa75b1959351252457fde88f91d20f AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
RUN pip uninstall --yes pip setuptools wheel && addgroup -g 10001 app && adduser -D -u 10001 -G app app
WORKDIR /srv
COPY --from=dependencies /opt/venv /opt/venv
COPY --chown=10001:10001 app ./app
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "20"]
