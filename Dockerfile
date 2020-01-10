# Base image
FROM python:3.7-alpine as python
LABEL maintainer=william16180@gmail.com


# Build stage
FROM python as build

RUN apk update && apk add --no-cache \
        bash \
        make \
        linux-headers \
        musl-dev \
        gcc \
        pcre \
        pcre-dev

COPY requirements.txt Makefile /app/
WORKDIR /app

RUN make init


# Test stage
FROM build as test

COPY . /app

ENTRYPOINT ["make", "test"]


# Production stage
FROM python as prod

RUN apk update && apk add --no-cache pcre

RUN addgroup -S flask && adduser -S flask -G flask
USER flask

COPY --from=build /app /app
COPY . /app
WORKDIR /app

HEALTHCHECK --timeout=5s --start-period=10s \
  CMD ["/app/p3_7env/bin/python", "/app/healthcheck.py"]

ENTRYPOINT ["/app/p3_7env/bin/uwsgi", "--ini", "/app/uwsgi/ecfaapi.ini"]
