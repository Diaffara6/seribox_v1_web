from django.urls import path
from .views import *
urlpatterns = [
   path('', connexion, name="Aconnexion"),
   path('deconnexion', deconnexion, name="Adeconnexion"),
   path('accueil', acc, name="accueil"),
   path('produits/', produits, name="produits"),
   path('ajouter_produit/', ajouter_produit, name="ajouter_produit"),
   path('sup_produit/<int:id>', sup_produit, name="sup_produit"),
   path('historique/', historiques, name="historiques"),
   path('sup_historique/<int:id>', sup_historique, name="sup_historique"),
   path('prescriptions/', prescriptions, name="prescriptions"),
   path('sup_prescription/<int:id>', sup_prescription, name="sup_prescription"),
   path('medecins/', medecins, name="medecins"),
   path('sup_medecin/<int:id>', sup_medecin, name="sup_medecin"),
   path('ajouter_medecin/', ajouter_medecin, name="ajouter_medecin"),
   path('modifier_produit/<int:id>', modifier_produit, name="modifier_produit"),
   path('modifier_medecin/<int:id>', modifier_medecin, name="modifier_medecin"),
  
]
