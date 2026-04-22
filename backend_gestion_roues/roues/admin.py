from django.contrib import admin
# Register your models here.
from django.contrib import admin
from .models import Roue , EntreeStock
from .models import Vente, VenteItem

admin.site.register(Roue)
admin.site.register(EntreeStock)
admin.site.register(Vente)
admin.site.register(VenteItem)
