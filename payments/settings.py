from django.conf import settings

# YooKassa settings
YOOKASSA_SHOP_ID = getattr(settings, 'YOOKASSA_SHOP_ID', '1093778')
YOOKASSA_SECRET_KEY = getattr(settings, 'YOOKASSA_SECRET_KEY', 'test_vqMWojDGaXP63ub1qhfWll50f-VbBOye4jfwIji8Kjo')

# Payment settings
PAYMENT_RETURN_URL = getattr(settings, 'PAYMENT_RETURN_URL', 'https://mytournament.ru/payment/success/')
PAYMENT_CANCEL_URL = getattr(settings, 'PAYMENT_CANCEL_URL', 'https://mytournament.ru/payment/cancel/')

# Payment statuses
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_WAITING_FOR_CAPTURE = 'waiting_for_capture'
PAYMENT_STATUS_SUCCEEDED = 'succeeded'
PAYMENT_STATUS_CANCELED = 'canceled' 