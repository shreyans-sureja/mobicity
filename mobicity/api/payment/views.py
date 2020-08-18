import json
import requests
from rest_framework import viewsets
from .serializers import PaymentCardSerializer
from .models import PaymentCards
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required

class PaymentCardsViewSet(viewsets.ModelViewSet):
    queryset = PaymentCards.objects.all().order_by('number')
    serializer_class = PaymentCardSerializer

@csrf_exempt
def userCards(request,id):
    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(pk=id)
        card = PaymentCards.objects.filter(user=user).values().first()
    except:
        return JsonResponse({'error' : 'Invalid Request'})

    return JsonResponse({'card': card})

def validate_user_session(id,token):
    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(pk=id)
        if user.session_token == token:
            return True
        return False
    except UserModel.DoesNotExist:
        return False

@csrf_exempt
def get_card(request,id,token):

    if not validate_user_session(id,token):
        return JsonResponse({'error' : 'Invalid, Please login again!'},status=401)

    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a post request with valid parameter only'},status=400)

    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=id)
        card = PaymentCards.objects.filter(user=user).values().first()
        return JsonResponse({"card": card})
    except:
        return JsonResponse({"card" : {}},status=404)

def generate_token(obj,session_token):

    payload = {
        "merchantRefNum": session_token,
        "transactionType": "PAYMENT",
        "card": {
            "cardNum": obj['cardNum'],
            "cardExpiry": {
                "month": obj['expiry_month'],
                "year": obj['expiry_year']
            },
            "cvv": obj['cvv'],
            "holderName": obj['name']
        },
        "paymentType": "CARD",
        "amount": int(obj['amount']),
        "currencyCode": "USD",
        "billingDetails": {
            "street": "100 Queen Street West",
            "city": "Toronto",
            "state": "ON",
            "country": "CA",
            "zip": "M5H 2N2"
        },
        "returnLinks": [
            {
                "rel": "on_completed",
                "href": "https://www.google.com/",
                "method": "GET"
            },
            {
                "rel": "on_failed",
                "href": "https://www.amazon.in/",
                "method": "GET"
            },
            {
                "rel": "default",
                "href": "https://www.spacex.com/",
                "method": "GET"
            }
        ]
    }

    url = "https://api.test.paysafe.com/paymenthub/v1/paymenthandles"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic {}'.format(settings.BASE64_KEY),
        'Simulator': '"EXTERNAL"'
    }

    payload = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    r = response.json()
    if response.status_code == 201:
        return r['paymentHandleToken']
    print(response.status_code)
    print(response.text.encode('utf8'))
    return None


def make_payment(obj,token,client_token):
    url = "https://api.test.paysafe.com/paymenthub/v1/payments"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic {}'.format(settings.BASE64_KEY),
        'Simulator': '"EXTERNAL"'
    }
    payload = {
        "merchantRefNum": token,
        "amount": int(obj['amount']),
        "currencyCode": "USD",
        "dupCheck": "true",
        "settleWithAuth": "true",
        "paymentHandleToken": client_token,
        "description": "description"
    }
    payload = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


@csrf_exempt
def pay(request,id,token):
    if not validate_user_session(id,token):
        return JsonResponse({'error' : 'Invalid session, Please login again!'},status=401)

    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a post request with valid parameter only'},status=400)

    UserModel = get_user_model()
    user = UserModel.objects.get(pk=id)

    obj = {}
    obj['cardNum'] = "4530910000012345"
    obj['expiry_month'] = "11"
    obj['expiry_year'] = "2027"
    obj['cvv'] = "202"
    obj['name'] = user.name
    obj['amount'] = "200"
    
    client_token = generate_token(obj,token)

    if client_token is None:
        return JsonResponse({'error': 'Send a post request with valid parameter only'}, status=400)

    payment = make_payment(obj,token,client_token)

    res = payment.json()
    if payment.status_code == 201 and res['status'] == 'COMPLETED':
        return JsonResponse({'payment': "sucessful"})
    else:
        return JsonResponse({'payment':'unsucessful, something went wrong!'},status=404)



