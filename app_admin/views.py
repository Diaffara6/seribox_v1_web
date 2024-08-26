from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from app_medibox.models import *
from app_medecin.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import timedelta, datetime
from django.db.models import Sum
# Create your views here.

def is_superuser(user):
    return user.is_superuser


def connexion(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            if username and password:
                user = authenticate(username=username, password=password)
                if user and user.is_superuser:
                    login(request, user=user)
                    return redirect("accueil")
                else:
                    messages.error(request, "Vous n'êtes pas autorisé à vous connecter.")
            else:
                messages.error(request, "Veuillez fournir l'identifiant et le mot de passe.")
        return render(request=request, template_name="app_admin/index.html")
    return redirect("accueil")  # Redirigez si déjà connecté


@user_passes_test(is_superuser, login_url="Aconnexion")
def deconnexion(request):
    logout(request)
    messages.error(request, "Vous avez été déconnecté(e).")
    return redirect('Aconnexion')


@user_passes_test(is_superuser, login_url="Aconnexion")
def acc(request):
    p = Produit.objects.all().order_by("-created_at")[:3]
    context = {'produits':p}
    return render(request, template_name="app_admin/accueil.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def ajouter_produit(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        prix = request.POST.get("prix")
        desc = request.POST.get("description")
        quantite = int(request.POST.get("quantite"))
        place = int(request.POST.get("place"))
        ordo = request.POST.get("odronnance")  # Utilisez "odronnance" ici
        image = request.FILES.get("image")

        if nom and prix and quantite and place and image:
            p = Produit(nom=nom, prix=prix, quantite=quantite,place=place, image=image)
            if desc:
                p.description = desc
            if ordo:  # Vérifiez si 'odronnance' est défini (coché)
                p.odronnance = True
            p.save()
            messages.success(request, "Ajout effectué avec succès")
            return redirect("produits")
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires (*).")

    return render(request, template_name="app_admin/ajouter_produits.html")



@user_passes_test(is_superuser, login_url="Aconnexion")
def modifier_produit(request, id):
    p = get_object_or_404(Produit, pk=id)
    if request.method == "POST":
        nom = request.POST.get("nom")
        prix = request.POST.get("prix")
        desc = request.POST.get("description")
        quantite = int(request.POST.get("quantite"))
        place = int(request.POST.get("place"))
        ordo = request.POST.get("odronnance")
        image = request.FILES.get("image")

        if ordo:
            p.odronnance = True
        else:
            p.odronnance = False
            p.save()
        if nom:
            p.nom = nom
            p.save()
        if prix:
            p.prix = prix
            p.save()
        if quantite:
            p.quantite = quantite
            p.save()
        if place:
            p.place = place
            p.save()
        if desc:
            p.description = desc
            p.save()
        if image:
            p.image = image
            p.save()

        messages.success(request, "Modification effectuée avec succès")
        return redirect("produits")

    return render(request, template_name="app_admin/ajouter_produits.html", context={'p':p})


@user_passes_test(is_superuser, login_url="Aconnexion")
def produits(request):
    p = Produit.objects.all().order_by("-created_at")
    context = {'produits':p}
    return render(request, template_name="app_admin/produits.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def sup_produit(request, id):
    p = get_object_or_404(Produit, pk=id)
    messages.error(request, f"{p.nom} a été supprimé avec succès.")
    p.delete()



@user_passes_test(is_superuser, login_url="Aconnexion")
def historiques(request):
    histo = Commande.objects.filter(commander=True).order_by("-create_at")
    context={'h': histo}
    return render(request, template_name="app_admin/historiques.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def sup_historique(request, id):
    h = get_object_or_404(Commande, pk=id)
    messages.error(request, "suppression effectuée succès.")
    h.delete()
    return redirect(request.META.get("HTTP_REFERER"))


@user_passes_test(is_superuser, login_url="Aconnexion")
def prescriptions(request):
    presc = Prescription.objects.all().order_by('-pk')
    context={'presc': presc}
    return render(request, template_name="app_admin/prescriptions.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def sup_prescription(request, id):
    p = get_object_or_404(Prescription, pk=id)
    messages.error(request, "Prescription supprimée avec succès.")
    p.delete()
    return redirect(request.META.get("HTTP_REFERER"))


@user_passes_test(is_superuser, login_url="Aconnexion")
def medecins(request):
    medecins = Medecin.objects.all().order_by('-pk')
    context={'m': medecins}
    return render(request, template_name="app_admin/medecins.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def sup_medecin(request, id):
    m = get_object_or_404(Medecin, pk=id)
    messages.error(request, "Medecin supprimé avec succès.")
    m.medecin.delete()
    return redirect(request.META.get("HTTP_REFERER"))


@user_passes_test(is_superuser, login_url="Aconnexion")
def ajouter_medecin(request):
    username=''
    nom=''
    prenom=''
    context ={}
    if request.method == "POST":
        username = request.POST["username"]
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        password = request.POST["password"]
        password1 = request.POST["password1"]

        if username and password and password1:
            if User.objects.filter(username=username).exists():
                    messages.error(request, "ce nom d'utilisateur a deja été utilisé ")
            elif password != password1:
                    messages.error(request, "vos mots de passes ne correspondent pas ")
            elif len(password) < 6:
                    messages.error(request, "votre mot de passe doit avoir au moins 6 caracteres ")
            else:
                user = User.objects.create_user(username=username, password=password)
                Medecin.objects.create(medecin=user)
                if nom:
                    user.last_name = nom
                if prenom:
                    user.first_name = prenom
                user.save()
                if user:
                    messages.success(request, "Medecin ajouté avec succès ")
                    return redirect("medecins")
        else:
            messages.error(request, "Remplissez correctement les champs obligatoires (*)")

        context={'username':username,
                 'nom':nom,
                 'prenom':prenom,
                 }
    return render(request, template_name="app_admin/ajouter_medecin.html", context=context)


@user_passes_test(is_superuser, login_url="Aconnexion")
def modifier_medecin(request, id):
    u = get_object_or_404(User, pk=id)
    if request.method == "POST":
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        password = request.POST["password"]
        password1 = request.POST["password1"]

        if password and password1:
            if password != password1:
                messages.error(request, "Vos mots de passe ne correspondent pas.")
                return redirect(request.META.get('HTTP_REFERER'))
            elif len(password) < 6:
                messages.error(request, "Le mot de passe doit avoir au moins 6 caractères.")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                hashed_password = make_password(password)
                u.password = hashed_password
                u.save()
        if nom:
            u.last_name = nom
            u.save()
        if prenom:
            u.first_name = prenom
            u.save()


        messages.error(request, "modification effectuée avec succès.")
        return redirect("medecins")

    context={'u':u,}
    return render(request, template_name="app_admin/ajouter_medecin.html", context=context)

