import base64
import requests
from datetime import datetime
from flask import current_app

SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
LIVE_BASE = "https://api.safaricom.co.ke"


def _base_url():
    return LIVE_BASE if current_app.config["MPESA_ENV"] == "live" else SANDBOX_BASE


def normalize_phone(raw_phone):
    """Convert any Kenyan phone format to 2547XXXXXXXX / 2541XXXXXXXX."""
    phone = raw_phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if phone.startswith("7") or phone.startswith("1"):
        phone = "254" + phone
    return phone


def get_access_token():
    consumer_key = current_app.config["MPESA_CONSUMER_KEY"]
    consumer_secret = current_app.config["MPESA_CONSUMER_SECRET"]

    resp = requests.get(
        f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials",
        auth=(consumer_key, consumer_secret),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def stk_push(phone, amount, account_reference="SummitStakes", description="Wallet deposit"):
    """Initiate an STK push and return Safaricom's response (includes CheckoutRequestID)."""
    shortcode = current_app.config["MPESA_SHORTCODE"]
    passkey = current_app.config["MPESA_PASSKEY"]
    callback_url = current_app.config["MPESA_CALLBACK_URL"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    token = get_access_token()
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": normalize_phone(phone),
        "PartyB": shortcode,
        "PhoneNumber": normalize_phone(phone),
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": description,
    }

    resp = requests.post(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
