from rest_framework import viewsets
from .serializers import PaymentCardSerializer
from .models import PaymentCards
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

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


@csrf_exempt
def pay(request,id,token):
    if not validate_user_session(id,token):
        return JsonResponse({'error' : 'Invalid session, Please login again!'},status=401)

    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a post request with valid parameter only'},status=400)

    return JsonResponse({'payment' : "sucessful"})

