from urllib import request

from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_protected(request):
    return Response({
        "message": "Tu es connecté !",
        "user": request.user.username,
        "role": request.user.role
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_vendeur(request):
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)

    username = request.data.get('username')
    password = request.data.get('password')

    user = User.objects.create_user(
        username=username,
        password=password,
        role='vendeur'
    )

    return Response({'message': 'Vendeur créé'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_vendeurs(request):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)

    vendeurs = User.objects.filter(role='vendeur')

    data = [
        {
            "id": v.id,
            "username": v.username
        }
        for v in vendeurs
    ]

    return Response(data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vendeur(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)

    user = User.objects.get(pk=pk)
    user.delete()

    return Response({'message': 'Supprimé'})