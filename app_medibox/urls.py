from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('panier/', panier, name='panier'),
    path('valider/', valider, name='valider'),
    path('panier/<str:v>/',panier, name='panier_with_v'),
    path('supp_med/<int:id>/',supp_med, name='supp_med'),
    path('panier/<str:s>/',panier, name='panier_s'),
    path('panier/<str:f>/',panier, name='panier_f'),
    path('panier/<str:p>/',panier, name='panier_p'),
    path('recherche/', recherche, name='recherche'),
    path('detail/<str:id>', detail, name='detail'),
    path('valider_commande/', valider_commande, name='valider_commande'),
    path('vider_panier/', vider_panier, name='vider_panier'),
    path('ajouter_au_panier/<str:id>', ajouter_au_panier, name='ajouter_au_panier'),
    path('valider_commande_directe/<str:id>', valider_commande_directe, name='valider_commande_directe'),
    path('scan_qr_code/', scan_qr_code, name='scan_qr_code'),
]