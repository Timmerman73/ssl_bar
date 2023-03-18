from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from BarApp.models import Saldo,Stortingen,Drankjes,Transacties
from django import forms
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
            dateTime=datetime.now())
        
        saldo.saldo = new_saldo
        saldo.save()
        storting.save()

    
    
    money_form = AddMoney(initial= {'amount': 0.00,
                                    'user': request.user})
    
    return render(request,"add_saldo.html",{"form": money_form })