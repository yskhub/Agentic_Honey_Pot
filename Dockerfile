FROM python:3.11-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Use virtual env inside container
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Healthcheck and non-root runtime user for better production posture
RUN useradd --create-home --shell /bin/false sentinel || true

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD ["/bin/sh", "-c", "wget -qO- http://127.0.0.1:8030/health || exit 1"]

EXPOSE 8030

ENV API_KEY=changeme
ENV ADMIN_API_KEY=changeme

EXPOSE 8030

# Run as non-root user
USER sentinel

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8030"]
