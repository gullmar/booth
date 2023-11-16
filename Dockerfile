# syntax=docker/dockerfile:1

FROM python:3.11-bookworm
ARG WHL_FILE=booth-0.0.1-py2.py3-none-any.whl
RUN python -m venv .venv
RUN . .venv/bin/activate
COPY . /.
RUN pip install build
RUN python -m build --wheel
RUN pip install /dist/$WHL_FILE
RUN pip install waitress
RUN flask --app booth init-db
EXPOSE 8080
CMD waitress-serve --call 'booth:create_app'