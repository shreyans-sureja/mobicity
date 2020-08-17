from rest_framework import serializers
from .models import PaymentCards

class PaymentCardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentCards
        fields = ('number','expiry')
