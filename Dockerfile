FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY libertymon.py ./

ENV PYTHONUNBUFFERED TRUE
ENTRYPOINT [ "python", "./libertymon.py" ]