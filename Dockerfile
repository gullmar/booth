# syntax=docker/dockerfile:1

FROM python:3.11-bookworm
COPY . /app
RUN pip install /app
RUN pip install waitress
RUN flask --app booth init-db
EXPOSE 8080
CMD waitress-serve --call 'booth:create_app'