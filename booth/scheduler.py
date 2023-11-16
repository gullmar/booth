from flask_apscheduler import APScheduler
import time

from booth import db, offers


app_scheduler = APScheduler()


def find_offer(offers_list, id):
    for offer in offers_list:
        if offer["id"] == id:
            return offer
    return None


def sync_offers(local_scheduler: APScheduler | None = None):
    """
    :param local_scheduler: used for tests
    """
    scheduler = local_scheduler or app_scheduler
    if not scheduler.app:
        return
    with scheduler.app.app_context():
        scheduler.app.logger.info("Syncing offers...")
        error, products = db.get_all_products()
        if products == []:
            scheduler.app.logger.info("No products to sync.")
            return
        if error or not products:
            scheduler.app.logger.info(
                "Offers sync aborted: cannot get products from db."
            )
            return
        for product in products:
            error, updated_offers = offers.get_offers(product["id"])
            if error or not updated_offers:
                scheduler.app.logger.info(
                    "Offers sync aborted: cannot get product offers from API."
                )
                return
            error, current_offers = db.get_product_offers(product["id"])
            if error or not current_offers:
                scheduler.app.logger.info(
                    "Offers sync aborted: cannot get product offers from db."
                )
                return
            # Remove offers that do not exist anymore
            for current_offer in current_offers:
                if not any(
                    [offer["id"] == current_offer["id"] for offer in updated_offers]
                ):
                    db.delete_offer(current_offer["id"])
            for updated_offer in updated_offers:
                updated_offer["product_id"] = product["id"]
                existing_offer = next(
                    (
                        offer
                        for offer in current_offers
                        if offer["id"] == updated_offer["id"]
                    ),
                    None,
                )
                # Add new offers
                if not existing_offer:
                    error = db.add_offer(
                        updated_offer["id"],
                        updated_offer["product_id"],
                        updated_offer["price"],
                        updated_offer["items_in_stock"],
                    )
                    continue
                # Update changed offers
                if existing_offer != updated_offer:
                    db.update_offer(
                        updated_offer["id"],
                        updated_offer["product_id"],
                        updated_offer["price"],
                        updated_offer["items_in_stock"],
                    )


def update_price_history(local_scheduler: APScheduler | None = None):
    """
    :param local_scheduler: used for tests
    """
    scheduler = local_scheduler or app_scheduler
    if not scheduler.app:
        return
    with scheduler.app.app_context():
        scheduler.app.logger.info("Updating price history...")

        now = int(time.time())

        error, products = db.get_all_products()
        if products == []:
            scheduler.app.logger.info("No products for updating the price history.")
            return
        if error or products is None:
            scheduler.app.logger.info(
                "Updating the price history aborted: cannot get products from db."
            )
            return
        if not products:
            scheduler.app.logger.info(
                "Updating the price history interrupted: there are no products."
            )
            return
        for product in products:
            error, offers = db.get_product_offers(product["id"])
            if error or not offers:
                scheduler.app.logger.info(
                    "Updating the price history aborted: cannot get product offers from db."
                )
                continue
            min_price = offers[0]["price"]
            total_price = 0
            total_quantity = 0
            for offer in offers:
                total_price += offer["price"] * offer["items_in_stock"]
                total_quantity += offer["items_in_stock"]
                if offer["price"] < min_price:
                    min_price = offer["price"]
            mean_price = total_price / total_quantity

            db.add_price_record(now, product["id"], mean_price, min_price)

            # Allow a maximum number of records per product
            try:
                max_product_records = int(scheduler.app.config["MAX_PRODUCT_RECORDS"])
            except Exception:
                scheduler.app.logger.error(
                    f"Error parsing MAX_PRODUCT_RECORDS: {scheduler.app.config['MAX_PRODUCT_RECORDS']}, using default of 100"
                )
                max_product_records = 100
            if len(offers) + 1 > max_product_records:
                db.delete_oldest_price_record(product["id"])


def init_app(app):
    if not app.config["TESTING"]:
        try:
            sync_interval_seconds = int(app.config["OFFERS_SYNC_INTERVAL_SECONDS"])
        except Exception:
            app.logger.error(
                f"Error parsing OFFERS_SYNC_INTERVAL_SECONDS: {app.config['OFFERS_SYNC_INTERVAL_SECONDS']}, using default of 60 seconds"
            )
            sync_interval_seconds = 300
        try:
            update_history_interval_seconds = int(
                app.config["UPDATE_PRICE_HISTORY_INTERVAL_SECONDS"]
            )
        except Exception:
            app.logger.error(
                f"Error parsing UPDATE_PRICE_HISTORY_INTERVAL_SECONDS: {app.config['UPDATE_PRICE_HISTORY_INTERVAL_SECONDS']}, using default of 60 seconds"
            )
            update_history_interval_seconds = 300
        app.config.from_mapping(
            JOBS=[
                {
                    "id": "sync_offers",
                    "func": sync_offers,
                    "trigger": "interval",
                    "seconds": sync_interval_seconds,
                },
                {
                    "id": "update_price_history",
                    "func": update_price_history,
                    "trigger": "interval",
                    "seconds": update_history_interval_seconds,
                },
            ]
        )

        app_scheduler.init_app(app)
        app_scheduler.start()
        app_scheduler.run_job("sync_offers")
        app_scheduler.run_job("update_price_history")
