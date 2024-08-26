import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import *
from app_medecin.models import Prescription
from unidecode import unidecode

#ne rien touché à part la fonction (valider_commande et l'adresse ip de l'ESP)


# Create your views here.


def index(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    context = {'produits': Produit.objects.all(), 'taille_cmd': Commande.objects.filter(commander=False)}
    return render(request, template_name="app_medibox/index.html", context=context)


def detail(request, id):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    produit = get_object_or_404(Produit, pk=id)
    pall = Produit.objects.exclude(pk=produit.pk)
    try:
        cmd = Commande.objects.get(utilisateur=request.user, produit=produit, commander=False)
    except:
        cmd = ''
    context = {"produit": produit, 'pall': pall, 'cmd': cmd, 'taille_cmd': Commande.objects.filter(commander=False)}
    return render(request, template_name="app_medibox/detail.html", context=context)


def ajouter_au_panier(request, id):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    produit = get_object_or_404(Produit, pk=id)
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    commande, created = Commande.objects.get_or_create(utilisateur=request.user, produit=produit, commander=False)

    if request.method == 'POST':
        quantite = int(request.POST.get('quantite'))

        if produit.odronnance:
            messages.error(request, "Vous ne pouvez pas commander ce médicament sans prescription.")
        elif quantite <= 0:
            messages.error(request, "La quantité doit être supérieure à zéro.")
        elif quantite > 2:
            messages.error(request, "Vous ne pouvez pas commander plus de 2 médicaments de ce type.")
        elif quantite + commande.quantite > produit.quantite:
            messages.error(request, f"La quantité demandée dépasse la quantité en stock pour {produit.nom}.")
        else:
            commande.quantite = quantite
            commande.total = quantite * produit.prix
            commande.save()

            if commande not in panier.commandes.all():
                panier.commandes.add(commande)

            panier.total = sum(commande.total for commande in panier.commandes.filter(utilisateur=request.user))
            panier.save()

            messages.success(request, f"{commande.produit.nom} a été ajouté(e) à votre panier.")

        if panier.total == 0:
            c = Commande.objects.filter(commander=False)
            c.delete()
            panier.delete()

    return redirect(request.META.get('HTTP_REFERER'))


def vider_panier(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    try:
        panier = Panier.objects.get(utilisateur=request.user)
        commandes_non_commandees = Commande.objects.filter(utilisateur=request.user, commander=False)

        commandes_non_commandees.delete()
        panier.delete()

        messages.success(request, "Votre panier a été vidé.")
    except Panier.DoesNotExist:
        messages.error(request, "Votre panier est déjà vide.")

    return redirect('index')


def panier(request, v=None, s=None, f=None, p=None):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    if request.method == 'GET':
        v_url = request.GET.get('v')
        s_url = request.GET.get('s')
        f_url = request.GET.get('f')
        p_url = request.GET.get('p')
    else:
        v_url = None
        s_url = None
        f_url = None
        p_url = None
    v = v_url if v_url else v
    s = s_url if s_url else s
    f = f_url if f_url else f
    p = p_url if p_url else p

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        contenu_panier = panier.commandes.all()
    except:
        panier = ''
        contenu_panier = ''

    context = {'panier': panier, 'contenu_panier': contenu_panier,
               'taille_cmd': Commande.objects.filter(commander=False), 'v': v, 'f': f, 'p': p, 's': s}

    return render(request=request, template_name="app_medibox/panier.html", context=context)

#l'adresse ip de l'ESP à ecrire exactement sous la forme suivante : "http://adresse_ip:80"
adresse_ip_esp ="http://192.168.0.233:80"

def valider_commande(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    commandes = Commande.objects.filter(utilisateur=request.user, commander=False)
    for commande in commandes:
        produit = commande.produit
        produit.quantite -= commande.quantite
        produit.save()

        commande.commander = True
        commande.save()
        #la valeur de data varie en fonction des compartiments
        # exemple si le compartiment oû se trouve le produit est egal à 1 alors le programme enverra (1) à l'ESP
        #en suite l'ESP tournera le moteur qu'il doit controler lorsqu'il recoit la valeur (1)
        if produit.place == 1:
            data = {'data': '1'}
        elif produit.place == 2:
            data = {'data': '2'}
        elif produit.place == 3:
            data = {'data': '3'}
        else:
            data = {'data': '4'}

        commande.commander = True
        commande.save()
        url = f"{adresse_ip_esp}/envoyer_donnees"
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("connection reussie")
        else:
            print("connection reussie")

    panier = Panier.objects.get(utilisateur=request.user)
    panier.delete()

    messages.success(request, f"Votre commande a été validée avec succes.")
    return redirect('index')


def valider(request):
    if request.method == 'POST':
        place = request.POST.get('place', None)
        if place is not None:
            # Traitez la valeur de place selon vos besoins
            return JsonResponse({'place': place})
        else:
            # Si "place" n'est pas spécifié, renvoyez une réponse JSON par défaut
            return JsonResponse({'place': 0})
    else:
        # Redirigez vers la vue index si la méthode n'est pas POST
        return redirect('index')


#l'adresse ip de l'ESP à ecrire exactement sous la forme suivante : "http://adresse_ip:80"
adresse_ip_esp ="http://192.168.0.233:80"

def valider_commande_directe(request, id):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    produit = get_object_or_404(Produit, pk=id)
    if request.method == 'POST':
        quantite_demandee = int(request.POST.get('quantite'))
        if produit.odronnance:
            messages.error(request, "Vous ne pouvez pas commander ce medicament sans prescription")
            return redirect(request.META.get('HTTP_REFERER'))
        elif quantite_demandee > produit.quantite:
            messages.error(request, f"La quantité demandée dépasse la quantité en stock pour {produit.nom}.")
            return redirect(request.META.get('HTTP_REFERER'))
        elif quantite_demandee > 2:
            messages.error(request, f"Commande refusée , Vous ne pouvez pas commander plus que 2 {produit.nom} .")
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            commande, created = Commande.objects.get_or_create(utilisateur=request.user, produit=produit,
                                                               commander=False)
            commande.quantite = quantite_demandee
            commande.total = commande.quantite * produit.prix
            commande.save()

            produit.quantite -= quantite_demandee
            produit.save()
            #la valeur de data varie en fonction des compartiments
            # exemple si le compartiment oû se trouve le produit est egal à 1 alors le programme enverra (1) à l'ESP
            #en suite l'ESP tournera le moteur qu'il doit controler lorsqu'il recoit la valeur (1)

            if produit.place == 1:
                data = {'data' : '1'}
            elif produit.place == 2:
                data = {'data' : '2'}
            elif produit.place == 3:
                data = {'data' : '3'}
            else:
                data = {'data' : '4'}

            commande.commander = True
            commande.save()
            url = f"{adresse_ip_esp}/envoyer_donnees"
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("connection reussie")
            else:
                print("connection reussie")

            messages.success(request, f"Votre commande pour {produit.nom} a été validée.")
            return redirect('index')

    context = {"produit": produit, 'taille_cmd': Commande.objects.filter(commander=False)}
    return render(request, template_name="app_medibox/detail.html", context=context)


def supp_med(request, id):
    p = get_object_or_404(Produit, pk=id)
    com = Commande.objects.get(produit=p, commander=False)
    com.delete()

    messages.success(request, f'{p.nom} a été retiré de votre panier')
    return redirect(request.META.get("HTTP_REFERER"))



def recherche(request):
    query = request.GET.get('q')
    a = False  # Indicateur pour "je veux" ou similaire
    v = False  # Indicateur pour "valide" ou similaire
    s = False
    p = False
    f = False
    m = False

    produits = []

    if query:
        query = query.lower()
        query = unidecode(query)

        # Si la requête se termine par un point, retirez-le
        if query.endswith('.'):
            query = query[:-1]
        if query.endswith(' '):
            query = query[:-1]
        prox_liste = ['proxim','proxin','proxi', 'proxy','toxine',"l'approxene",'proxene']
        for p in prox_liste:
            if p in query:
                query = query.replace(p, " proxen ")
        effe_liste = ['fergan','gitan']
        for p in effe_liste:
            if p in query:
                query = query.replace(p, " efferalgan ")
        para_liste = ["marco", "rasta malko", "palace ta mall", "palace", "parasol", "pas rasta mode", "pas rasta mall",'rastaman','castorama']
        for p in para_liste:
            if p in query:
                query = query.replace(p, "paracetamol")
        dol_liste = ["le prendre","nipprone", "dolipran", "dolipanee", "dolipane ","dolipane  ", "dolipranee","pastoral"]
        for p in dol_liste:
            if p in query:
                query = query.replace(p, " doliprane ")

        grip_liste = ["m'agripex","ipex","gri plex","gripex,","grip,","grip","grippe", "clipex", "vitesse", "reflexe", "triplex", "bipex", " repete"]
        for p in grip_liste:
            if p in query:
                query = query.replace(p, " gripex ")

        soussou_liste = ["obama ", "moi ma", "moi", "ou", "ou est ma", "samba", "mohamed", "voir ma", "quoi ma ",
                         "mamadou", "maman","wam" ]
        malinke_liste = ["dis-moi", "debarrassa", "neba", "corps", "co", "mets", "score", "d'imma", "dimanche",
                         "dumas", "dima", "dimma"]
        peul_liste = ["l'info,","l'info","l'impala,","l'impala","l'enfant a", "l'enfant", "l'enfant la", "la fois la ","la fois " "une fois la ", "lampadaire "]
        fr_liste = ["ouvre-moi", "jeu", "donne", "donner", "donnée", "donné",
                    "ajoute", "donne-moi", "achete-moi", "ajoute-moi", "mets-moi", "comment",
                    "lance-moi", "lance", "envoie-moi", "envoie",'veux' ]

        for p in fr_liste:
            if p in query:
                query = query.replace(p, " veux ")

        for p in malinke_liste:
            if p in query:
                query = query.replace(p, " fee ")

        for p in peul_liste:
            if p in query:
                query = query.replace(p, " fala ")

        for p in soussou_liste:
            if p in query:
                query = query.replace(p, " wama ")

        effe_liste = ["l'efferalgan",'logan','frele']
        for p in effe_liste:
            if p in query:
                query = query.replace(p, "efferalgan")

        # Liste des mots-clés pour "je veux" ou similaire
        tab_je_veux = ["veux", "wama", "fala", "fee"]
        query = query.split(" ")
        print(query)
        for q in tab_je_veux:
            if q in query:
                for item in query:
                    produits = Produit.objects.filter(nom=item)
                    for produit in produits:
                        if produit.odronnance:
                            messages.error(request, 'commande impossible')
                            return redirect('index')
                        else:
                            panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
                            commande, created = Commande.objects.get_or_create(
                                utilisateur=request.user, produit=produit, commander=False
                            )
                            commande.quantite = 1
                            commande.total = commande.quantite * produit.prix
                            commande.save()
                            if commande not in panier.commandes.all():
                                panier.commandes.add(commande)

                            panier.total = sum(
                                commande.total for commande in panier.commandes.filter(utilisateur=request.user))
                            panier.save()
                    if item == 'veux':
                        f = True
                        print('f vrai')
                    elif item == 'wama':
                        s = True
                        print('s vrai')
                    elif item == 'fala':
                        print('p vrai')
                        p = True

                a = True

        query = " ".join(query)
        # Liste des mots-clés pour "valide" ou similaire
        tab_valider = ["valide", "valider", "validé", "validée", "vallee"]
        for t in tab_valider:
            if t in query:
                v = True

            # Liste des mots-clés pour "vide" ou similaire
        tab_vide = ["vide", "aviser", "alibaba","ivan","avidite", "vidé", "vider", "vidée", "ville", "montpellier", "bagarre", "raffini",
                    "rafik","Magan","alban","reagan","ibada","iban","aiba","aegon","iba","bagan"
                    "rafini", "rachel", "rafle", "raffin", "hiba","yvan",'Dragon',"hagan","airbag","ibadan"]
        for t in tab_vide:
            if t.lower() in query:
                return redirect("vider_panier")

        if a:
            try:
                Panier.objects.get(utilisateur=request.user)
                if s:
                    return redirect("panier_s", s='s')
                elif f:
                    return redirect("panier_f", f='f')
                elif p:
                    return redirect("panier_p", p='p')
                else:
                    return redirect("panier")
            except:
                return redirect(recherche)
        if v:
            try:
                panier = Panier.objects.get(
                    utilisateur=request.user
                )
                if panier:
                    return redirect("panier_with_v", v='v')
            except:
                messages.error(request, f"Vous n'avez pas de panier valide.")
                return redirect(request.META.get("HTTP_REFERER"))

        if not a and not v:
            produits = Produit.objects.filter(nom__icontains=query)

    context = {'produits': produits, 'query': query, 'taille_cmd': Commande.objects.filter(commander=False)}
    return render(request, template_name="app_medibox/recherche.html", context=context)


def scan_qr_code(request):
    if request.method == 'POST':
        qrCodeValue = request.POST.get("qrCodeValue")
        print(qrCodeValue)

        if qrCodeValue:
            try:
                prescription = Prescription.objects.get(pk=qrCodeValue)
                meds = [prescription.med1, prescription.med2, prescription.med3, prescription.med4]

                panier, _ = Panier.objects.get_or_create(utilisateur=request.user)

                for med_name in meds:
                    if med_name:
                        try:
                            produit = Produit.objects.get(nom=med_name)
                            commande, created = Commande.objects.get_or_create(
                                utilisateur=request.user, produit=produit, commander=False
                            )

                            commande.quantite = 1

                            commande.total = commande.quantite * produit.prix
                            commande.save()

                            panier.commandes.add(commande)

                            panier.total = sum(
                                commande.total for commande in panier.commandes.filter(utilisateur=request.user))
                            panier.save()

                        except Produit.DoesNotExist:
                            messages.error(request,
                                           f"Le médicament '{med_name}' n'existe pas dans notre base de données.")
                            return redirect("panier")
                return redirect("panier")
            except Prescription.DoesNotExist:
                messages.error(request, "Erreur lors du scan de la prescription.")
                return redirect(request.META.get("HTTP_REFERER"))

    return render(request, 'app_medibox/scan_qr_code.html')
