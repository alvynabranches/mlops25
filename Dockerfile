FROM python:3.12.7-slim

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY emotion_detection.py app.py

ARG ARG_WORKERS=1
ARG ARG_PORT=80
ENV WORKERS=${ARG_WORKERS}
ENV PORT=${ARG_PORT}
EXPOSE ${PORT}

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "${PORT}", "--workers", "${WORKERS}" ]