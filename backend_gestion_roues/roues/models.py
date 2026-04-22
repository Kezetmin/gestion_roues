from django.db import models

from accounts.views import User

class Roue(models.Model):
    TYPE_CHOICES = (
        ('neuve', 'Neuve'),
        ('occasion', 'Occasion'),
    )

    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    diametre = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)

    quantite_stock = models.IntegerField(default=0)

    date_ajout = models.DateTimeField(auto_now_add=True)
    
    photo = models.ImageField(upload_to='roues/', null=True, blank=True)

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.diametre})"
    

class EntreeStock(models.Model):
    roue = models.ForeignKey(Roue, on_delete=models.CASCADE, related_name='entrees')
    quantite = models.IntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    date_entree = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"Entrée {self.quantite} - {self.roue.marque}"

from django.conf import settings

class Vente(models.Model):
    vendeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_vente = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Vente #{self.id} - {self.vendeur}"
    
class VenteItem(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='items')
    roue = models.ForeignKey(Roue, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    benefice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.roue} x {self.quantite}"