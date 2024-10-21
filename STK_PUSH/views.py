import json

import requests
from django.shortcuts import render
from django.http import HttpResponse
import logging
from django.views.decorators.csrf import csrf_exempt

from STK_PUSH import Mpesa

logger = logging.getLogger(__name__)


# Create your views here.
@csrf_exempt
def initiate_payment(request):
    if request.method == "POST":
        phone = request.POST["phone"]
        amount = request.POST["amount"]
        logger.info(f"{phone} {amount}")

        data = {
            "BusinessShortCode": Mpesa.get_business_shortcode(),
            "Password": Mpesa.generate_password(),
            "Timestamp": Mpesa.get_current_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": Mpesa.get_business_shortcode(),
            "PhoneNumber": phone,
            "CallBackURL": Mpesa.get_callback_url(),
            "AccountReference": "Test",
            "TransactionDesc": "Test"
        }

        headers = Mpesa.generate_request_headers()  # contains extra info in the http request which provide
        # additional info to the server

        resp = requests.post(Mpesa.get_payment_url(), json=data, headers=headers)

        logger.debug(resp.json())
        json_resp = resp.json()

        if "ResponseCode" in json_resp:
            code = json_resp["ResponseCode"]
            if code == "0":
                mid = json_resp["MerchantRequestID"]
                cid = json_resp["CheckoutRequestID"]
                logger.info(f"{mid} {cid}")
            else:
                logger.error(f"An error occurred while initiating the transaction {code} ")
        elif "errorCode" in json_resp:
            errorCode = json_resp["errorCode"]
            logger.error(f"An error with code {errorCode} occurred")

    return render(request, "Payments.html")


# callback url
@csrf_exempt
def callback(request):
    result = json.loads(request.data)  # convert the callback from saf into a json dictionary
    mid = result["Body"]["stkCallBack"]["MerchantRequestID"]
    cid = result["Body"]["stkCallBack"]["CheckoutRequestID"]
    code = result["Body"]["stkCallBack"]["ResponseCode"]
    logger.info(f"From Callback Result {mid} {cid} {code}")
    return HttpResponse({"message": "Successfully received"})
