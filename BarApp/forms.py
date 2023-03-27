
from django.contrib.auth.models import User
from django import forms
from BarApp.models import *
from operator import itemgetter

def get_users():
    """get_users()
    Returns sorted list for all users which are in Saldo table
    :return: _description_
    """
    return sorted([(i.id,i.username) for i in User.objects.filter(id__in=Saldo.objects.values_list('user_id'))],key=itemgetter(1))

class AddMoney(forms.Form):
    """Add Money to saldo
    Form which allows users to deposit money.
    :param forms: _description_
    """
    amount = forms.DecimalField(label="Hoeveel geld wil je storten:",max_digits=5, decimal_places=2)
    user = forms.ModelChoiceField(label="Bij wie moet dit op de rekening:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)).order_by("username"))
        
class OrderDrink(forms.Form):
    """OrderDrink form which is list of checkboxes which one for each user.

    :param forms: _description_
    """
    user = forms.MultipleChoiceField(
        choices = get_users,
        widget  = forms.CheckboxSelectMultiple,
    )
    
class AddDrink(forms.ModelForm):
    """ModelForm AddDrink
    Bases on the Drankjes tabel
    Supplies all field except date and Time
    :param forms: _description_
    """
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
        
class UpdateDrink(forms.Form):
    """UpdateDrink
    Form which allows users to select one of all drinks
    :param forms: _description_
    """
    drink = forms.ModelChoiceField(label="Welk drankje wil je aanpassen?",queryset=Drankjes.objects.all())
class UpdateDrinkModel(forms.ModelForm):
    """Model based on Drankjes 
    Form which allows users to update drinks

    :param forms: _description_
    """
    class Meta:
        model = Drankjes
        fields = ["naam","prijs","description","active","img","ratio"]
        labels = {
        "img": "Afbeelding (Optioneel)",
        "description": "Omschrijving (Optioneel)",
        "active": "Is het drankje te koop?"
        }
        widgets = {
            'description': forms.Textarea,
        }
class DeleteDrink(forms.Form):
    """DeleteDrink
    Drinkselector form for drink deletion

    :param forms: _description_
    """
    drink = forms.ModelChoiceField(label="Welk drankje wil je verwijderen",queryset=Drankjes.objects.all())
    
class DateInput(forms.DateInput):
    """Form to supply date

    :param forms: _description_
    """
    input_type = 'date'


class UserStortingLog(forms.Form):
    """Form which allows users to enter 
    two users and date
    Used for Storting log
    :param forms: _description_
    """
    usr = forms.ModelChoiceField(label="Saldo van:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)).order_by("username"),required=False)
    exe = forms.ModelChoiceField(label="Uitgevoerd door",queryset=User.objects.all(),required=False)
    dT = forms.DateField(label="Datum",widget=DateInput,required=False)
    
class UserSaldoLog(forms.Form):
    """Form which allows users to select user for SaldoLog

    :param forms: _description_
    """
    usr = forms.ModelChoiceField(label="Saldo van:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)).order_by("username"),required=False,empty_label="Alle gebruikers")

class DateDrinkLog(forms.Form):
    """Allows users to select date for DrinkLog
    :param forms: _description_
    """
    dT = forms.DateField(label="Datum (Leeg laten voor alles)",widget=DateInput,required=False)
    
    
        
    

    

