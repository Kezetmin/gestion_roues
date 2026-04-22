from django.urls import path
from .views import create_vendeur, delete_vendeur, list_vendeurs, test_protected

urlpatterns = [
    path('test/', test_protected),
    path('vendeurs/', list_vendeurs),
    path('vendeurs/create/', create_vendeur),
    path('vendeurs/<int:pk>/', delete_vendeur),
]