FROM python:3.8-slim-buster

RUN apt -y update
RUN apt -y install git graphviz

RUN mkdir /app
COPY ./src /app
RUN python3 -m pip install -r /app/requirements.txt

RUN mkdir /remote
WORKDIR /app

ENTRYPOINT ["python3", "/app/main.py"]
