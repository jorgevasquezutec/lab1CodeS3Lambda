# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /serviceconsumer
COPY . .

RUN pip install flask
RUN pip install requests

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]