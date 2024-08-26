import rest_framework.response
from django.contrib.auth import authenticate, login
from django.contrib.messages.storage.cookie import MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from unidecode import unidecode

from api.serializers import ProduitSerializer, TailleCommandeSerializer, ProduitDetailSerializer, PanierSerializer, \
    ContenuPanierSerializer
from app_medecin.models import Prescription
from app_medibox.models import Produit, Commande, Panier


@api_view(['GET','POST'])
def index_data(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    produits = Produit.objects.all()
    taille_cmd = Commande.objects.filter(commander=False).count()

    produit_serializer = ProduitSerializer(produits, many=True)
    taille_cmd_serializer = TailleCommandeSerializer({'taille_cmd': taille_cmd})

    data = {
        'produits': produit_serializer.data,
        'taille_cmd': taille_cmd_serializer.data['taille_cmd']
    }

    return rest_framework.response.Response(data)



class ProduitDetailView(RetrieveAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitDetailSerializer


@api_view(['GET'])
def ajouter_au_panier(request, id):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    produit = get_object_or_404(Produit, pk=id)
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    commande, created = Commande.objects.get_or_create(utilisateur=request.user, produit=produit, commander=False)

    messages_data = {
        'error_message': '',
        'success_message': ''
    }

    if request.method == 'POST':
        quantite = int(request.POST.get('quantite'))
        if produit.odronnance:
            messages_data['error_message'] = "Vous ne pouvez pas commander ce médicament sans prescription."
        elif quantite <= 0:
            messages_data['error_message'] = "La quantité doit être supérieure à zéro."
        elif quantite > 2:
            messages_data['error_message'] = "Vous ne pouvez pas commander plus de 2 médicaments de ce type."
        elif quantite + commande.quantite > produit.quantite:
            messages_data['error_message'] = f"La quantité demandée dépasse la quantité en stock pour {produit.nom}."
        else:
            commande.quantite = quantite
            commande.total = quantite * produit.prix
            commande.save()

            if commande not in panier.commandes.all():
                panier.commandes.add(commande)

            panier.total = sum(commande.total for commande in panier.commandes.filter(utilisateur=request.user))
            panier.save()

            messages_data['success_message'] = f"{commande.produit.nom} a été ajouté(e) à votre panier."

        if panier.total == 0:
            c = Commande.objects.filter(commander=False)
            c.delete()
            panier.delete()
    if messages_data['success_message']:
        return rest_framework.response.Response(messages_data['success_message'])
    else:
        return rest_framework.response.Response(messages_data['error_message'])


@api_view(['GET'])
def vider_panier(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    response_data = {}

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        commandes_non_commandees = Commande.objects.filter(utilisateur=request.user, commander=False)

        commandes_non_commandees.delete()
        panier.delete()

        response_data['message'] = "Votre panier a été vidé."
    except Panier.DoesNotExist:
        response_data['message'] = "Votre panier est déjà vide."

    return rest_framework.response.Response(response_data)


@api_view(['GET', 'POST'])
def panier(request, v=None):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    if not user:
        return rest_framework.response.Response({'message': 'Authentication failed'}, status=401)

    if request.method == 'GET':
        v_url = request.GET.get('v')
    else:
        v_url = None
    v = v_url if v_url else v

    response_data = {}

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        contenu_panier = panier.commandes.all()

        panier_serializer = PanierSerializer(panier)
        contenu_panier_serializer = ContenuPanierSerializer(contenu_panier, many=True)

        response_data['panier'] = panier_serializer.data
        response_data['contenu_panier'] = contenu_panier_serializer.data
        response_data['v'] = v
    except Panier.DoesNotExist:
        response_data['panier'] = None
        response_data['contenu_panier'] = None
        response_data['v'] = v

    return rest_framework.response.Response(response_data)


@api_view(['GET'])
def valider_commande(request):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)

    response_data = {}

    commandes = Commande.objects.filter(utilisateur=request.user, commander=False)

    if commandes.exists():
        for commande in commandes:
            produit = commande.produit
            produit.quantite -= commande.quantite
            produit.save()

            commande.commander = True
            commande.save()

        panier = Panier.objects.get(utilisateur=request.user)
        panier.delete()

        response_data['message'] = "Votre commande a été validée avec succès."
    else:
        response_data['message'] = "Aucune commande à valider."

    return rest_framework.response.Response(response_data)


@api_view(['POST', 'GET'])
def valider_commande_directe(request, id):
    user = authenticate(username='Patient', password='Lavieestbelle')
    login(request, user=user)
    produit = get_object_or_404(Produit, pk=id)
    place = 0
    response_data = {}
    error_messages = []  # Liste pour collecter les messages d'erreur

    if request.method == 'POST':
        quantite_demandee = int(request.data.get('quantite'))  # Utilisation de request.data pour POST

        if produit.odronnance:
            error_messages.append("Vous ne pouvez pas commander ce médicament sans prescription")
        if quantite_demandee > produit.quantite:
            error_messages.append(f"La quantité demandée dépasse la quantité en stock pour {produit.nom}.")
        if quantite_demandee > 2:
            error_messages.append(f"Commande refusée, vous ne pouvez pas commander plus de 2 {produit.nom}.")

        if error_messages:
            response_data['errors'] = error_messages  # Ajouter les messages d'erreur à la réponse JSON
        else:
            commande, created = Commande.objects.get_or_create(utilisateur=request.user, produit=produit,
                                                               commander=False)
            commande.quantite = quantite_demandee
            commande.total = commande.quantite * produit.prix
            commande.save()

            produit.quantite -= quantite_demandee
            produit.save()

            commande.commander = True
            commande.save()


            if produit.place == 1:
               place = 1
            elif produit.place == 2:
                place = 2
            elif produit.place == 3:
                place = 3
            else:
                place = 4

            response_data['place'] = place

    return rest_framework.response.Response(response_data,
                                            status=status.HTTP_200_OK if not error_messages else status.HTTP_400_BAD_REQUEST)


class RechercheAPIView(APIView):
    def get(self, request):
        user = authenticate(username='Patient', password='Lavieestbelle')
        login(request, user=user)
        query = request.GET.get('q')
        a = False  # Indicateur pour "je veux" ou similaire
        v = False  # Indicateur pour "valide" ou similaire

        produits = []

        if query:
            query = query.lower()
            query = unidecode(query)

            # Si la requête se termine par un point, retirez-le
            if query.endswith('.'):
                query = query[:-1]

            para_liste = ["palace ta mall", "palace", "parasol", "pas rasta mode", "pas rasta mall"]
            for p in para_liste:
                if p in query:
                    query = query.replace(p, "paracetamol")
            dol_liste = ["dolipran", "dolipanee", "dolipane", "dolipranee"]
            for p in dol_liste:
                if p in query:
                    query = query.replace(p, "doliprane")

            grip_liste = ["grippe", "clipex", "vitesse", "réflexe", "triplex", " répète"]
            for p in grip_liste:
                if p in query:
                    query = query.replace(p, "gripex")

            effe_liste = ["l'efferalgan"]
            for p in effe_liste:
                if p in query:
                    query = query.replace(p, "efferalgan")

            veux_liste = ["l'enfant a", "l'enfant la", "la fois la ", "une fois la ", "lampadaire ", "quoi ma "]
            for p in veux_liste:
                if p in query:
                    query = query.replace(p, " veux ")

            # Liste des mots-clés pour "je veux" ou similaire
            tab_je_veux = ["veux", "ouvre", "ouvre-moi", "wama", "ou", "jeu", "donne", "donner", "donnée", "donné",
                           "ajoute", "donne-moi", "achete-moi", "ajoute-moi", "moi", "mets-moi", "mets", "samba",
                           "mohamed",
                           "mamadou", "maman", "comment", "lance-moi", "lance", "envoie-moi", "envoie", "fala"]
            query = query.split(" ")
            for q in tab_je_veux:
                if q in query:
                    for p in query:
                        produits = Produit.objects.filter(nom=p)
                        for produit in produits:
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

                    a = True

            query = " ".join(query)
            # Liste des mots-clés pour "valide" ou similaire
            tab_valider = ["valide", "valider", "validé", "validée", "vallee"]
            for t in tab_valider:
                if t in query:
                    v = True

                # Liste des mots-clés pour "vide" ou similaire
            tab_vide = ["vide", "alibaba", "vidé", "vider", "vidée", "ville", "montpellier", "bagarre", "raffini",
                        "rafik",
                        "rafini", "rachel", "rafle", "raffin", "hiba"]
            for t in tab_vide:
                if t in query:
                    return rest_framework.response.Response({'message': 'Votre panier a été vidé.'},
                                                            status=status.HTTP_200_OK)

            if a:
                try:
                    Panier.objects.get(utilisateur=request.user)
                    return rest_framework.response.Response({'message': 'Votre panier a été mis à jour.'},
                                                            status=status.HTTP_200_OK)
                except:
                    return rest_framework.response.Response({'message': 'Aucun panier trouvé.'},
                                                            status=status.HTTP_400_BAD_REQUEST)
            if v:
                try:
                    panier = Panier.objects.get(
                        utilisateur=request.user
                    )
                    if panier:
                        return rest_framework.response.Response({'message': 'Votre panier est valide.'},
                                                                status=status.HTTP_200_OK)
                except:
                    return rest_framework.response.Response({'message': 'Vous n\'avez pas de panier valide.'},
                                                            status=status.HTTP_400_BAD_REQUEST)

            if not a and not v:
                produits = Produit.objects.filter(nom__icontains=query)

        serializer = ProduitSerializer(produits, many=True)
        return rest_framework.response.Response({'produits': serializer.data})


class ScanQRCodeAPIView(APIView):
    def post(self, request):
        qr_code_value = request.data.get("qrCodeValue")

        if qr_code_value:
            try:
                prescription = Prescription.objects.get(pk=qr_code_value)
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

                            if commande not in panier.commandes.all():
                                panier.commandes.add(commande)

                            panier.total = sum(
                                commande.total for commande in panier.commandes.filter(utilisateur=request.user))
                            panier.save()

                        except Produit.DoesNotExist:
                            return rest_framework.Response(
                                {"error": f"Le médicament '{med_name}' n'existe pas dans notre base de données."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                return rest_framework.Response({"message": "Prescription scannée avec succès."},
                                               status=status.HTTP_200_OK)
            except Prescription.DoesNotExist:
                return rest_framework.Response({"error": "Erreur lors du scan de la prescription."},
                                               status=status.HTTP_400_BAD_REQUEST)

        return rest_framework.Response({"error": "Le champ 'qrCodeValue' est requis."},
                                       status=status.HTTP_400_BAD_REQUEST)
