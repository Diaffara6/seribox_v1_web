from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.


class Produit(models.Model):
    nom = models.CharField(max_length=110)
    prix = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    quantite = models.IntegerField(default=1)
    image = models.ImageField(upload_to="produits", blank=True, null=True)
    odronnance = models.BooleanField(default=False)
    place = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} , {self.prix} GNF"


class Commande(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    commander = models.BooleanField(default=False)
    total = models.IntegerField(default=0)
    create_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.utilisateur} ( {self.produit.nom} )"


class Panier(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    commandes = models.ManyToManyField(Commande)
    total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.utilisateur.username} {self.total} GNF"
