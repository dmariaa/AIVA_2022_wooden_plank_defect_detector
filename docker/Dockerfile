# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster

WORKDIR /defect_detector
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN python -m pip install -U pip
RUN python -m pip install -r requirements.txt
COPY src src
ENV PYTHONPATH /defect_detector
CMD [ "python", "-u", "src/server.py"  ]