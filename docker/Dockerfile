FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY .git /app/.git
COPY . /app

EXPOSE 8000

