import requests
import uuid
from django.conf import settings
from textblob import TextBlob

def get_momo_token():
    url = f"{settings.MOMO_BASE_URL}/collection/token/"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.MOMO_PRIMARY_KEY
    }
    auth = (settings.MOMO_API_USER_ID, settings.MOMO_API_KEY)

    response = requests.post(url, headers=headers, auth=auth)
    response.raise_for_status()
    auth = (settings.MOMO_API_USER_ID, settings.MOMO_API_KEY)

    print(f"🔐 Requesting token with USER_ID: {auth[0]}")
    print(f"🔐 Using PRIMARY_KEY: {settings.MOMO_PRIMARY_KEY[:5]}...")

    response = requests.post(url, headers=headers, auth=auth)
    print(f"🛠 Status Code: {response.status_code}, Response: {response.text}")

    response.raise_for_status()
    return response.json()["access_token"]
    return response.json()["access_token"]



def make_momo_payment(amount, phone_number):
    token = get_momo_token()
    if not token:
        raise Exception("Failed to retrieve MTN MoMo token.")

    payment_url = f"{settings.MOMO_BASE_URL}/collection/v1_0/requesttopay"
    reference_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": settings.MOMO_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key": settings.MOMO_PRIMARY_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "amount": str(amount),
        "currency": "RWF",  # or "RWF" if MTN supports Rwandan Franc directly
        "externalId": "123456",  # Can be any ID
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone_number  # Must be in format like 25078XXXXXXX
        },
        "payerMessage": "Payment for your order",
        "payeeNote": "Thanks for shopping"
    }

    response = requests.post(payment_url, headers=headers, json=data)
    response.raise_for_status()
    return reference_id  # You can store this in DB to track payment



def analyze_sentiment(text):
    analysis = TextBlob(text)
    return 'positive' if analysis.sentiment.polarity >= 0 else 'negative'
    
