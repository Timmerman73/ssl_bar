from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from BarApp.models import Saldo,Stortingen,Drankjes,Transacties,Tikkie
from django import forms
from django.contrib.auth.decorators import login_required
from datetime import datetime
import pandas as pd
import locale
locale.setlocale(locale.LC_ALL,"nl-nl")

# Create your views here.

@login_required
def index(request):
    return render(request,"index.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if User.objects.filter(username=username).exists():
            messages.warning(request,"Er bestaat al een gebruiker met deze gebruikersnaam!")
        elif len(password1)  < 4:
            messages.warning(request,"Wachtwoord moet minimaal 4 tekens lang zijn!")
        elif password1 != password2:
            messages.warning(request,"Wachtwoorden komen niet overeen")
        else:
            user = User.objects.create_user(username=username,password=password1)
            logout(request)
            login(request,user)
            saldo_entry = Saldo(user=user,saldo=0)
            saldo_entry.save()
            messages.success(request,f"Account met username: {username} sucessvol aangemaakt")    
    return render (request=request, template_name="register.html") 

def v_login(request):
    renderdict = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request,user)
            messages.success(request,"Login successvol")
            return redirect(index)
        else:
            messages.warning(request,"Ongeldige combinatie van username of wachtwoord")
    return render(request,"login.html")

def v_logout(request):
    logout(request)
    messages.success(request,"Je bent nu uitgelogt!")
    return redirect(index)


class AddMoney(forms.Form):
    amount = forms.DecimalField(label="Hoeveel geld wil je storten:",max_digits=5, decimal_places=2)
    user = forms.ModelChoiceField(label="Bij wie moet dit op de rekening:",queryset=User.objects.filter(id__in=Saldo.objects.values_list('user_id',flat=True)))

    
    
@login_required
def add_saldo(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        if amount != 0:
            user = User.objects.get(id=request.POST.get("user"))
            executed_by = request.user
            saldo = Saldo.objects.get(user=user)
            old_saldo = float(saldo.saldo)
            new_saldo = float(saldo.saldo) + amount
            storting = Stortingen(
                user=user,
                done_by=executed_by,
                amount=amount,
                saldo_voor=old_saldo,
                saldo_na=new_saldo,
                dateTime=datetime.now().replace(microsecond=0))
            
            saldo.saldo = new_saldo
            saldo.save()
            storting.save()
    df = pd.DataFrame(list(Stortingen.objects.all().values("dateTime","user_id","saldo_voor","amount","saldo_na","done_by_id")))
    df = df.sort_values(by="dateTime",ascending=False)
    df["user_id"] = [User.objects.get(id=i) for i in df["user_id"]]
    df["done_by_id"] = [User.objects.get(id=i) for i in df["done_by_id"]]
    df['dateTime'] = [i.strftime("%A %d-%B %X") for i in df["dateTime"]]
    df = df.rename(columns={
        "dateTime":"Datum & Tijd",
        "user_id":"Saldo van",
        "saldo_voor":"Saldo voor",
        "amount":"Bedrag",
        "saldo_na":"Saldo na",
        "done_by_id":"Uitgevoerd door"
               })
    html_table = df.to_html(classes="table table-striped table-bordered",index=False,max_rows=25)
    
    money_form = AddMoney(initial= {'amount': 0.00,
                                    'user': request.user})
    
    if Tikkie.objects.exists():
        tikkie = Tikkie.objects.latest("id")
    else:
        tikkie = "Nog geen link in database Voeg er een toe!"
    
    return render(request,"add_saldo.html",{
        "tikkie": tikkie,
        "form": money_form,
        "table": html_table
                                            })
    
    
def tikkie_change(request):
    if request.method == "POST":
        link = request.POST.get("link")
        t = Tikkie(link=link,user=request.user)
        t.save()
        
    return redirect(add_saldo)

def bar_admin(request):
    return render(request,"bar_admin.html",{'form':Add_drink()})

class Add_drink(forms.ModelForm):
    class Meta:
        model = Drankjes
        exclude = ["dateTime",""]

