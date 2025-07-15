#FROM python:3.12-slim
#
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#WORKDIR /app
#
#RUN apt-get update && apt-get install -y gcc g++ python3-venv python3-pip libc-dev libc6-dev && rm -rf /var/lib/apt/lists/*
#
#RUN python -m venv /opt/venv
#ENV PATH="/opt/venv/bin:$PATH"
#
#COPY requirements.txt .
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt --no-cache-dir
#
#COPY . .
#
#CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
