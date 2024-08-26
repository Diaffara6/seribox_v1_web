from django.urls import path
from .views import index_data, ProduitDetailView, ajouter_au_panier, vider_panier, panier, valider_commande, \
    valider_commande_directe, RechercheAPIView, ScanQRCodeAPIView

urlpatterns = [
    # Votre autre configuration d'URLs
    path('index_data/', index_data, name='index-data'),
    path('detail/<int:pk>/', ProduitDetailView.as_view(), name='produit-detail-api'),
    path('ajouter_au_panier/<int:id>/', ajouter_au_panier, name='ajouter-au-panier-api'),
    path('vider_panier/', vider_panier, name='vider-panier-api'),
    path('panier/', panier, name='panier-api'),
    path('valider_commande/', valider_commande, name='valider-commande'),
    path('valider_commande_directe/<int:id>/', valider_commande_directe, name='valider-commande-directe'),
    path('recherche/', RechercheAPIView.as_view(), name='recherche-api'),
    path('scan-qr-code/', ScanQRCodeAPIView.as_view(), name='scan-qr-code-api'),

]
