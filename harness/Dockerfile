# OpsPilot harness - containerised.
#
# Build context is the repo root (see docker-compose.yml), not this
# harness/ directory - so paths below are relative to the root, same
# as before the restructure, just with harness/ prefixed now.

FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY harness/main.py .

CMD ["python", "main.py"]
