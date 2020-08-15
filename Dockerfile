# Base image
FROM python:3.8-alpine as base
LABEL maintainer=william16180@gmail.com


# Build stage
FROM base as build

RUN apk update && apk add --no-cache \
        bash \
        make \
        git \
        linux-headers \
        musl-dev \
        gcc \
        pcre \
        pcre-dev \
        jpeg-dev \
        zlib-dev

COPY requirements.prod.txt Makefile /app/
WORKDIR /app

RUN make init env=prod


# Deployment image
FROM base as deploy

RUN apk update && apk add --no-cache pcre

RUN addgroup -S flask && adduser -S flask -G flask
USER flask

COPY --from=build /app /app
COPY . /app
WORKDIR /app

ENV ENV=prod

HEALTHCHECK --timeout=5s --start-period=10s \
  CMD ["/app/p3_8env/bin/python", "/app/healthcheck.py"]

ENTRYPOINT ["/app/p3_8env/bin/uwsgi", "--ini", "/app/uwsgi/ecfaapi.ini"]
