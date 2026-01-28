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

EXPOSE 8030

ENV API_KEY=changeme
ENV ADMIN_API_KEY=changeme

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8030"]
