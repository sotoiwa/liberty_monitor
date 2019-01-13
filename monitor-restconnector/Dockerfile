FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor_restConnector.py ./

ENV PYTHONUNBUFFERED TRUE
ENTRYPOINT [ "python", "./monitor_restConnector.py" ]