FROM python:latest

RUN apt update && apt upgrade -y 
RUN mkdir /app 

WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY . /app

ENTRYPOINT ["python",  "/app/geowifi.py"]

