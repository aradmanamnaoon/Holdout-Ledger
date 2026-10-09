FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 10001 ledger && mkdir /data && chown ledger:ledger /data
COPY requirements-runtime.lock ./
RUN python -m pip install --no-cache-dir -r requirements-runtime.lock
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir --no-deps .
USER ledger
EXPOSE 8000
CMD ["holdout-ledger", "serve", "--host", "0.0.0.0", "--database", "/data/audits.sqlite3"]
