import sqlite3
from uuid import uuid4

import click
from flask import current_app, g

from booth import constants


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        script = f.read().decode("utf-8")
        print("sql script", script)
        db.executescript(script)


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# SQL helpers


def _create(table, params: dict):
    keys = params.keys()
    values = params.values()
    db = get_db()
    db.execute(
        f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({', '.join(['?' for _ in keys])})",
        tuple(values),
    )
    db.commit()
    current_app.logger.info(f"DB: table {table}, create row {params}")


def _read(table, project: list, query: dict):
    keys = query.keys()
    values = query.values()
    row = (
        get_db()
        .execute(
            f"SELECT {', '.join(project)} FROM {table} WHERE {', '.join([f'{key} = ?' for key in keys])}",
            tuple(values),
        )
        .fetchone()
    )
    current_app.logger.info(f"DB: table {table}, read row where {query}")
    return row


def _read_all(table, project: list, order_by=None):
    rows = (
        get_db()
        .execute(
            f"SELECT {', '.join(project)} FROM {table}"
            + (f" ORDER BY {order_by}" if order_by else "")
        )
        .fetchall()
    )
    current_app.logger.info(
        f"DB: table {table}, read all rows"
        + (f", order by {order_by}" if order_by else "")
    )
    return rows


def _read_bulk(table, project: list, query: dict, order_by=None):
    keys = query.keys()
    values = query.values()
    rows = (
        get_db()
        .execute(
            f"SELECT {', '.join(project)} FROM {table} WHERE {', '.join([f'{key} = ?' for key in keys])}"
            + (f" ORDER BY {order_by}" if order_by else ""),
            tuple(values),
        )
        .fetchall()
    )
    current_app.logger.info(
        f"DB: table {table}, read rows in bulk where {query}"
        + (f", order by {order_by}" if order_by else "")
    )
    return rows


def _update(table, query: dict, updates: dict):
    query_keys = query.keys()
    query_values = list(query.values())
    update_keys = updates.keys()
    update_values = list(updates.values())
    db = get_db()
    db.execute(
        f"UPDATE {table} SET {', '.join([f'{key} = ?' for key in update_keys])} WHERE {', '.join([f'{key} = ?' for key in query_keys])}",
        tuple(update_values + query_values),
    )
    db.commit()
    current_app.logger.info(
        f"DB: table {table}, update row {query} with values {updates}"
    )


def _delete(table, query: dict):
    keys = query.keys()
    print(f"DELETE FROM {table} WHERE {', '.join([f'{key} = ?' for key in keys])}")
    values = query.values()
    db = get_db()
    db.execute(
        f"DELETE FROM {table} WHERE {', '.join([f'{key} = ?' for key in keys])}",
        tuple(values),
    )
    db.commit()
    current_app.logger.info(f"DB: table {table}, delete row where {query}")


# Model


def register_product(name, description):
    error = None
    product_id = str(uuid4())

    try:
        _create(
            "products", {"id": product_id, "name": name, "description": description}
        )
    except sqlite3.IntegrityError as e:
        current_app.logger.error(e)
        error = f'Name "{name}" is already used by another product.'
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    if error:
        product_id = None

    return error, product_id


def get_all_products():
    error, products = None, None

    try:
        products = _read_all("products", ["id", "name", "description"], order_by="name")

        if products is None:
            error = "Error retrieving products."
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error, products


def get_product(id):
    error, product = None, None

    try:
        product = _read("products", ["id", "name", "description"], {"id": id})

        if product is None:
            error = f"Product id {id} does not exist"
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error, product


def update_product(id, name, description):
    error = None

    try:
        _update("products", {"id": id}, {"name": name, "description": description})
    except sqlite3.IntegrityError as e:
        current_app.logger.error(e)
        error = f'Name "{name}" is already used by another product.'
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error


def delete_product(id):
    error = None

    try:
        _delete("products", {"id": id})
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error


def get_product_offers(product_id):
    error, product_offers = None, None

    try:
        product_offers = _read_bulk(
            "offers",
            ["id", "product_id", "price", "items_in_stock"],
            {"product_id": product_id},
        )

        if product_offers is None:
            error = "Error retrieving product offers"
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error, product_offers


def add_offer(id, product_id, price, items_in_stock):
    error = None

    try:
        _create("offers", {"id": id, "product_id": product_id, "price": price, "items_in_stock": items_in_stock})
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    if error:
        product_id = None

    return error


def update_offer(id, product_id, price, items_in_stock):
    error = None

    try:
        _update("offers", {"id": id}, {"product_id": product_id, "price": price, "items_in_stock": items_in_stock})
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error


def delete_offer(id):
    error = None

    try:
        _delete("offers", {"id": id})
    except Exception as e:
        current_app.logger.error(e)
        error = constants.GENERIC_ERROR_MESSAGE

    return error
