from django.contrib import admin
from BarApp.models import Saldo,Stortingen,Drankjes,Transacties,Tikkie

# Register your models here.
admin.site.register(Saldo)
admin.site.register(Stortingen)
admin.site.register(Drankjes)
admin.site.register(Transacties)
admin.site.register(Tikkie)