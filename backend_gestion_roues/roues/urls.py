from django.urls import path
from .views import ajouter_entree, historique_ventes, roues_list_create, roue_detail, stock_faible, total_benefice, ventes_par_jour
from .views import ajouter_entree_stock
from .views import creer_vente
from .views import (
    liste_ventes,
    ventes_du_jour,
    ventes_du_mois,
    ventes_par_vendeur
)
from .views import dashboard
from .views import historique_entrees
from .views import total_benefice

urlpatterns = [
    path('', roues_list_create),
   
    path('entree/', ajouter_entree_stock),
    path('ventes/', creer_vente),
    path('ventes/liste/', liste_ventes),
    path('ventes/jour/', ventes_du_jour),
    path('ventes/mois/', ventes_du_mois),
    path('ventes/me/', ventes_par_vendeur),
    path('dashboard/', dashboard),
    path('dashboard/chart/', ventes_par_jour),
    path('stock/faible/', stock_faible),
    path('ventes/historique/', historique_ventes),
    path('stock/entree/', ajouter_entree),
    path('stock/historique/', historique_entrees),
    path('dashboard/benefice/', total_benefice),
    path('<int:pk>/', roue_detail),
]