from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EntreeStock, Roue, Vente, VenteItem
from .serializers import EntreeStockSerializer, RoueSerializer, VenteSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from datetime import datetime
from django.utils.timezone import now
from django.db.models import Sum
from django.utils.timezone import now
from django.db.models.functions import TruncDate


# 📋 Liste + création
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def roues_list_create(request):
    if request.method == 'GET':
        roues = Roue.objects.all()
        serializer = RoueSerializer(roues, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RoueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔍 détail / update / delete
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def roue_detail(request, pk):
    try:
        roue = Roue.objects.get(pk=pk)
    except Roue.DoesNotExist:
        return Response({'error': 'Roue non trouvée'}, status=404)

    if request.method == 'GET':
        serializer = RoueSerializer(roue)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = RoueSerializer(roue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        roue.delete()
        return Response({'message': 'Supprimé'}, status=204)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajouter_entree_stock(request):
    serializer = EntreeStockSerializer(data=request.data)
    if request.user.role != 'admin':
      return Response({'error': 'Accès refusé'}, status=403)

    if serializer.is_valid():
        entree = serializer.save()

        # 🔥 Mise à jour automatique du stock
        roue = entree.roue
        roue.quantite_stock += entree.quantite
        roue.save()

        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

from django.db import transaction

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_vente(request):
    data = request.data
    items_data = data.get('items', [])

    if not items_data:
        return Response({'error': 'Aucun produit'}, status=400)

    with transaction.atomic():
        vente = Vente.objects.create(
            vendeur=request.user,
            total=0
        )

        total = 0

        for item in items_data:
            roue_id = item.get('roue')
            quantite = int(item.get('quantite'))

            try:
                roue = Roue.objects.get(id=roue_id)
            except Roue.DoesNotExist:
                return Response({'error': 'Roue introuvable'}, status=404)

            # ⚠️ Vérifier stock
            if roue.quantite_stock < quantite:
                return Response({'error': f'Stock insuffisant pour {roue.marque}'}, status=400)

            # 🔥 diminuer stock
            roue.quantite_stock -= quantite
            roue.save()

            prix = roue.prix_vente
            prix_vente = roue.prix_vente
            prix_achat = roue.prix_achat or 0
            benefice_unitaire = prix_vente - prix_achat
            benefice_total = benefice_unitaire * quantite
            VenteItem.objects.create(
            vente=vente,
            roue=roue,
            quantite=quantite,
            prix_unitaire=prix_vente,
            benefice=benefice_total  # 🔥 AJOUT
        )
            total += prix * quantite

        vente.total = total
        vente.save()

        return Response({'message': 'Vente créée', 'total': total})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_ventes(request):

    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(vendeur=request.user)
    else:
        ventes = Vente.objects.all()

    serializer = VenteSerializer(ventes, many=True)
    return Response(serializer.data)

from django.utils.timezone import now

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventes_du_jour(request):
    today = now().date()

    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(vendeur=request.user, date_vente__date=today)
    else:
        ventes = Vente.objects.filter(date_vente__date=today)

    serializer = VenteSerializer(ventes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventes_du_mois(request):
    today = now()

    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(
            vendeur=request.user,
            date_vente__year=today.year,
            date_vente__month=today.month
        )
    else:
        ventes = Vente.objects.filter(
            date_vente__year=today.year,
            date_vente__month=today.month
        )

    serializer = VenteSerializer(ventes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventes_par_vendeur(request):
    ventes = Vente.objects.filter(vendeur=request.user)
    serializer = VenteSerializer(ventes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    today = now().date()
    current_month = now()

    # 🔥 filtrage selon rôle
    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(vendeur=request.user)
    else:
        ventes = Vente.objects.all()

    # 💰 CA total
    total_ca = ventes.aggregate(total=Sum('total'))['total'] or 0

    # 📅 ventes du jour
    ventes_jour = ventes.filter(date_vente__date=today)
    ca_jour = ventes_jour.aggregate(total=Sum('total'))['total'] or 0

    # 📆 ventes du mois
    ventes_mois = ventes.filter(
        date_vente__year=current_month.year,
        date_vente__month=current_month.month
    )
    ca_mois = ventes_mois.aggregate(total=Sum('total'))['total'] or 0

    # 📦 stock total (admin seulement)
    stock_total = 0
    if request.user.role == 'admin':
        stock_total = Roue.objects.aggregate(total=Sum('quantite_stock'))['total'] or 0

    # 🛞 top produits (selon rôle)
    if request.user.role == 'vendeur':
        top_produits = (
            VenteItem.objects
            .filter(vente__vendeur=request.user)
            .values('roue__marque', 'roue__modele')
            .annotate(total_vendu=Sum('quantite'))
            .order_by('-total_vendu')[:5]
        )
    else:
        top_produits = (
            VenteItem.objects
            .values('roue__marque', 'roue__modele')
            .annotate(total_vendu=Sum('quantite'))
            .order_by('-total_vendu')[:5]
        )

    return Response({
        "chiffre_affaires_total": total_ca,
        "chiffre_affaires_jour": ca_jour,
        "chiffre_affaires_mois": ca_mois,
        "stock_total": stock_total,
        "top_produits": list(top_produits)
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventes_par_jour(request):
    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(vendeur=request.user)
    else:
        ventes = Vente.objects.all()

    data = (
        ventes
        .annotate(date=TruncDate('date_vente'))
        .values('date')
        .annotate(total=Sum('total'))
        .order_by('date')
    )

    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_faible(request):
    seuil = 5  # ⚠️ tu peux modifier

    roues = Roue.objects.filter(quantite_stock__lt=seuil)

    data = [
        {
            "id": r.id,
            "marque": r.marque,
            "modele": r.modele,
            "stock": r.quantite_stock
        }
        for r in roues
    ]

    return Response(data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_ventes(request):

    if request.user.role == 'vendeur':
        ventes = Vente.objects.filter(vendeur=request.user)
    else:
        ventes = Vente.objects.all()

    ventes = ventes.order_by('-date_vente')

    serializer = VenteSerializer(ventes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajouter_entree(request):

    roue_id = request.data.get('roue')
    quantite = int(request.data.get('quantite'))
    prix = float(request.data.get('prix_achat') or 0)

    roue = Roue.objects.get(id=roue_id)

    # 📦 ajouter stock
    roue.quantite_stock += quantite
    roue.prix_achat = prix  # 🔥 ICI
    roue.save()

    # 🧾 enregistrer entrée
    EntreeStock.objects.create(
        roue=roue,
        quantite=quantite,
        prix_achat=prix,  # 🔥 AJOUT
        utilisateur=request.user
    )

    return Response({'message': 'Stock ajouté'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_entrees(request):
    entrees = EntreeStock.objects.all().order_by('-date_entree')

    data = [
        {
            "produit": f"{e.roue.marque} {e.roue.modele}",
            "quantite": e.quantite,
            "prix_achat": e.prix_achat,  # 🔥 AJOUT ICI
            "date": e.date_entree,
            "user": e.utilisateur.username
        }
        for e in entrees
    ]

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_benefice(request):

    if request.user.role == 'vendeur':
        items = VenteItem.objects.filter(vente__vendeur=request.user)
    else:
        items = VenteItem.objects.all()

    total = items.aggregate(total=Sum('benefice'))['total'] or 0

    return Response({"benefice_total": total})