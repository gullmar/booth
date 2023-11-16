# syntax=docker/dockerfile:1

FROM python:3.11-bookworm
ARG WHL_FILE=booth-0.0.1-py2.py3-none-any.whl
COPY dist/$WHL_FILE /$WHL_FILE
RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install /$WHL_FILE
RUN pip install waitress
RUN flask --app booth init-db
CMD waitress-serve --call 'booth:create_app'