from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Prescription)
class AdminPres(admin.ModelAdmin):
    pass

@admin.register(Medecin)
class AdminMed(admin.ModelAdmin):
    pass