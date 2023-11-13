from flask_apscheduler import APScheduler

from booth import db, offers


scheduler = APScheduler()


def sync_offers():
    if not scheduler.app:
        return
    with scheduler.app.app_context():
        scheduler.app.logger.info("Syncing offers...")
        error, products = db.get_all_products()
        if products == []:
            scheduler.app.logger.info(
                "No products to sync."
            )
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
            for updated_offer in updated_offers:
                updated_offer["product_id"] = product["id"]
                existing_offer = next(
                    offer
                    for offer in current_offers
                    if offer["id"] == updated_offer["id"]
                )
                if not existing_offer:
                    error = db.add_offer(
                        updated_offer["id"],
                        updated_offer["product_id"],
                        updated_offer["price"],
                        updated_offer["items_in_stock"],
                    )
                    continue
                if existing_offer != updated_offer:
                    db.update_offer(
                        updated_offer["id"],
                        updated_offer["product_id"],
                        updated_offer["price"],
                        updated_offer["items_in_stock"],
                    )


def init_app(app):
    if not app.config["TESTING"]:
        try:
            interval_seconds = int(app.config["OFFERS_SYNC_INTERVAL_SECONDS"])
        except Exception:
            app.logger.error(
                f"Error parsing OFFERS_SYNC_INTERVAL_SECONDS: {app.config['OFFERS_SYNC_INTERVAL_SECONDS']}, using default of 60 seconds"
            )
            interval_seconds = 60
        app.config.from_mapping(
            JOBS=[
                {
                    "id": "sync_offers",
                    "func": sync_offers,
                    "trigger": "interval",
                    "seconds": interval_seconds,
                }
            ]
        )

        scheduler.init_app(app)
        scheduler.start()
        scheduler.run_job("sync_offers")