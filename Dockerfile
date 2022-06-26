FROM python:3.7-alpine

# Default port the webserver runs on
EXPOSE 6000

# Working directory for the application
WORKDIR /usr/src/app

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python3", "./mtgbot.py"]

COPY requirements.txt /usr/src/app/

RUN apk update && apk add --no-cache build-base \
 && pip3 install --no-cache-dir -r requirements.txt \
 && apk del build-base

# Copy everything to the working directory (Python files, templates, config) in one go.
COPY . /usr/src/app/
