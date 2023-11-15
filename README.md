# Booth

_Applifting Python asessment._

A REST API Python microservice which allows users to browse a product catalogue and which automatically updates prices from the offer service.

## Requirements

- Python 3.11.5

## Install dependencies

```
pip install .
```

## Build

```
pip install build
python -m build --wheel
```

The output file is in the `dist` folder. You can then install it on another system with `pip install <WHEEL_FILE>`.

## Run locally

### Initialize

Run only once to initialize database:

```
python -m flask --app booth init-db
```

### Start

Run in debug mode:

```
python -m flask --app run --debug
```

Run in production:

```
pip install waitress
waitress-serve --call 'booth:create_app'
```

## Run with Docker Compose

Environment variables can be customized in the `compose.yaml` file.

Secret variables can be specified as environment variables when starting the container: they will be passed as Docker secrets.

```
SECRET_KEY=... OFFERS_REFRESH_TOKEN=... docker-compose up
```
