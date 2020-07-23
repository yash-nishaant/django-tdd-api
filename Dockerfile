# Docker image and maintainer
FROM python:3.7-alpine 
LABEL maintainer = "Yash Nishaant"

# Environment variable to ensure Python runs in unbuffered mode, recommended for Docker containers
ENV PYTHONUNBUFFERED 1

# requirements.txt file to install necessary packages, automated through pip 
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps 

# create app directory on creation and change that to standard working directory 
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create user for application purposes only, prevent users from accessing root directory
RUN adduser -D user
USER user

