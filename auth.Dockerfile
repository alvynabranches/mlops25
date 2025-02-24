FROM python:3.12.7-slim

WORKDIR /app

RUN apt update
RUN apt install build-essential python3-dev libgl1 libglib2.0-0 -y

COPY auth_requirements.txt requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY auth.py auth.py

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1" ]