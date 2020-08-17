from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'',views.PaymentCardsViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('user/<int:id>/', views.userCards, name='payment.usercard'),
    path('pay/<int:id>/<str:token>/', views.pay, name="payment.pay"),
    path('<int:id>/<str:token>/',views.get_card,name="payment.getCard")
]
