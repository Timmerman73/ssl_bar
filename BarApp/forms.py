
from django.contrib.auth.models import User
from django import forms
from BarApp.models import *

def drink_img_filename(instance, filename):
    path = "drinks/"
    format = f"{instance.naam}_ID{instance.drankjes_id}" + instance.instance.file_extension
    print(format)
    return path + format


class AddMoney(forms.Form):
    amount = forms.DecimalField(label="Hoeveel geld wil je storten:",max_digits=5, decimal_places=2)
    user = forms.ModelChoiceField(label="Bij wie moet dit op de rekening:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)))



class Add_drink(forms.ModelForm):
    class Meta:
        model = Drankjes
        exclude = ["dateTime","done_by","active"]
        widgets = {
            "naam": forms.TextInput(attrs={"class":"form-control"}),
            "prijs": forms.NumberInput(attrs={"class":"form-control"}),
            "img": forms.FileInput(attrs={"class":"form-control"})
        }

