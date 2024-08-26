from rest_framework import serializers
from app_medibox.models import Produit, Commande, Panier


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'


class TailleCommandeSerializer(serializers.Serializer):
    taille_cmd = serializers.IntegerField()


class ProduitDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'


class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = '__all__'


class PanierSerializer(serializers.ModelSerializer):
    commandes = CommandeSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = '__all__'


class ContenuPanierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = '__all__'





