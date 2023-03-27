from django.contrib import admin
from BarApp.models import Saldo,Stortingen,Drankjes,Transacties,Tikkie
from django.contrib import admin
from image_cropping import ImageCroppingMixin

# Register your models here.
admin.site.register(Saldo)
admin.site.register(Stortingen)
admin.site.register(Transacties)
admin.site.register(Tikkie)

class MyModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(Drankjes, MyModelAdmin)