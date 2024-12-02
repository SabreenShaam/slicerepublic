def map_values_from_service_to_mbo_client_service(service, mbo_client_service):
    mbo_client_service.current = service.Current
    mbo_client_service.count = service.Count
    mbo_client_service.remaining = service.Remaining
    mbo_client_service.payment_date = service.PaymentDate
    mbo_client_service.active_date = service.ActiveDate
    mbo_client_service.expiration_date = service.ExpirationDate
    return mbo_client_service


def map_values_from_mbo_studio_service_to_studio_service(mbo_studio_service, studio_service):
    studio_service.name = mbo_studio_service.Name
    studio_service.mbo_service_id = mbo_studio_service.ID
    studio_service.mbo_product_id = mbo_studio_service.ProductID
    studio_service.price = mbo_studio_service.Price
    studio_service.online_price = mbo_studio_service.OnlinePrice
    studio_service.tax_rate = mbo_studio_service.TaxRate
    studio_service.count = mbo_studio_service.Count
