
from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Produit)
class AdminProd(admin.ModelAdmin):
    pass
@admin.register(Commande)
class AdminCom(admin.ModelAdmin):
    pass
@admin.register(Panier)
class AdminPanier(admin.ModelAdmin):
    pass



