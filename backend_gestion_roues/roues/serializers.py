from rest_framework import serializers
from .models import EntreeStock, Roue, Vente, VenteItem

class RoueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roue
        fields = '__all__'

class EntreeStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntreeStock
        fields = '__all__'


class VenteItemSerializer(serializers.ModelSerializer):
    nom_produit = serializers.SerializerMethodField()

    def get_nom_produit(self, obj):
        return f"{obj.roue.marque} {obj.roue.modele}"

    class Meta:
        model = VenteItem
        fields = [
            'id',
            'nom_produit',
            'quantite',
            'prix_unitaire',
            'benefice'  # 🔥 AJOUT
        ]

class VenteSerializer(serializers.ModelSerializer):
    vendeur_nom = serializers.CharField(source='vendeur.username', read_only=True)
    items = VenteItemSerializer(many=True, read_only=True)

    class Meta:
        model = Vente
        fields = [
            'id',
            'vendeur',
            'vendeur_nom',  # 🔥 IMPORTANT
            'date_vente',
            'total',
            'items',
        ]
   