
from django.contrib.auth.models import User
from django import forms
from BarApp.models import *
from operator import itemgetter

def get_users():
    return sorted([(i.id,i.username) for i in User.objects.filter(id__in=Saldo.objects.values_list('user_id'))],key=itemgetter(1))

class AddMoney(forms.Form):
    amount = forms.DecimalField(label="Hoeveel geld wil je storten:",max_digits=5, decimal_places=2)
    user = forms.ModelChoiceField(label="Bij wie moet dit op de rekening:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)).order_by("username"))
        
class Delete_drink(forms.Form):
    drink = forms.ModelChoiceField(label="Welk drankje wil je verwijderen",queryset=Drankjes.objects.all())
    
class OrderDrink(forms.Form):
    user = forms.MultipleChoiceField(
        choices = get_users, # this is optional
        widget  = forms.CheckboxSelectMultiple,
    )

    

class Add_drink(forms.ModelForm):
    class Meta:
        model = Drankjes
        fields = ["naam","prijs","description","img","ratio"]
        labels = {
        "img": "Afbeelding (Optioneel)",
        "description": "Omschrijving (Optioneel)"
        }
        widgets = {
            'description': forms.Textarea,
        }
