from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import qrcode
from io import BytesIO
from app_medibox.models import *
from .models import *
from django.contrib import messages
from .models import Prescription
from django.contrib.auth.decorators import login_required



def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user:
            try:
                medecin = Medecin.objects.get(medecin=user)  # Check if the user is a Medecin
                if medecin:
                    login(request, user)
                    messages.success(request, f"Bienvenue {username}")
                    return redirect('prescription')
            except Medecin.DoesNotExist:
                messages.error(request, "Vous n'avez pas le droit d'accès.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion') 

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
   # logo = Image.open("static/logo.png")  # Chemin vers le logo
   # logo = logo.resize((50, 50))  # Ajuster la taille du logo
   # img.paste(logo, (100, 100))  # Ajouter le logo au QR code
    
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    return img_io.getvalue()


def prescription_form(request):
    if request.method == 'POST':
        med1 = request.POST.get('med1', '')
        med2 = request.POST.get('med2', '')
        med3 = request.POST.get('med3', '')
        med4 = request.POST.get('med4', '')

        quant1 = 1 if med1 else 0
        quant2 = 1 if med2 else 0
        quant3 = 1 if med3 else 0
        quant4 = 1 if med4 else 0
        if not med1 and not med2 and not med3 and not med4:
            messages.error(request, "Remplissez au moins un champ.")
        else:  
            if any([med1, med2, med3, med4]):
                prescription = Prescription(
                    utilisateur=request.user,
                    med1=med1,
                    med2=med2,
                    med3=med3,
                    med4=med4,
                    quant1=quant1,
                    quant2=quant2,
                    quant3=quant3,
                    quant4=quant4,
                )
                prescription.save()
                messages.success(request, "Prescription effectuée avec succès")
                #encrypted_pk = cryptage(str(prescription.pk))  # Crypte le PK de la prescription
                qr_data = f"{prescription.pk}"
                qr_image = generate_qr_code(qr_data)
                prescription.qr_code.save(f'prescription_{prescription.pk}_qr.png', BytesIO(qr_image))
                return redirect('impression')  # Redirige pour vider le formulaire après soumission réussie
            else:
                messages.error(request, "Au moins un médicament doit être sélectionné.")
                produits = Produit.objects.filter(odronnance=True)
                context = {"produits": produits}
                return render(request, 'prescription.html', context=context)
    produits = Produit.objects.filter(odronnance=True)
    context = {"produits": produits}
    return render(request, 'prescription.html', context=context)


def impression(request):
    p = Prescription.objects.all().last()
    context = {'p': p}
    return render(request, template_name="impression.html", context=context)

