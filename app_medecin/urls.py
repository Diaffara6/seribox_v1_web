from django.urls import path
from .views import *

urlpatterns = [
    path('prescription', prescription_form, name='prescription'),
    path('impression', impression, name='impression'),
    path('', connexion, name='connexion'),
    path('deconnexion', deconnexion, name='deconnexion'),
   
   
  
]