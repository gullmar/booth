from flask import current_app

from booth import offers_api


# FIXME: this mechanism is not easily scalable and requires a specific
# implementation in each function calling the offers API.
# A more sophisticated solution relying on the JWT expiration could be preferred.
def evaluate_and_renovate_token(error) -> tuple[str | None, bool]:
    """
    Checks if the obtained error is a "bad authentication" error;
    if that is the case, renovate the access token using the refresh token.

    :param error: the error obtained calling the offers API
    """
    if error != offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE:
        return error, False
    baseurl = current_app.config["OFFERS_BASEURL"]
    refresh_token = current_app.config["OFFERS_REFRESH_TOKEN"]
    error, access_token = offers_api.fetch_access_token(baseurl, refresh_token)
    if access_token and not error:
        current_app.config.update(OFFERS_ACCESS_TOKEN=access_token)
        return error, True
    return error, False


def register_product(product_id, name, description):
    op = lambda: offers_api.register_product(
        current_app.config["OFFERS_BASEURL"],
        current_app.config["OFFERS_ACCESS_TOKEN"],
        product_id,
        name,
        description,
    )
    error = op()
    error, retry = evaluate_and_renovate_token(error)
    if retry:
        error = op()
    return error


def get_offers(product_id):
    op = lambda: offers_api.get_offers(
        current_app.config["OFFERS_BASEURL"],
        current_app.config["OFFERS_ACCESS_TOKEN"],
        product_id,
    )
    error, offers = op()
    error, retry = evaluate_and_renovate_token(error)
    if retry:
        error, offers = op()
    return error, offers
