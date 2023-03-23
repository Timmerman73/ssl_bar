from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from BarApp.models import Saldo,Stortingen,Drankjes,Transacties,Tikkie
from BarApp.forms import Add_drink,AddMoney,Delete_drink,OrderDrink
from datetime import datetime
import pandas as pd
import locale
from operator import itemgetter
locale.setlocale(locale.LC_ALL,"nl-nl")

# Create your views here.
from image_cropping.utils import get_backend


@login_required
def index(request):
    active_drinks = Drankjes.objects.filter(active=1)
    drinks = []
    for drink in active_drinks:
        drinks_dict = {
            "id": drink.drankjes_id,
            "naam": drink.naam,
            "prijs": drink.prijs,
            "desc": drink.description,
        }
        if not drink.img:
            drinks_dict["img"] = 'static/img/basic_bottle.svg'
        else:
            drinks_dict["img"] = get_backend().get_thumbnail_url(
        drink.img,
        {
            'size': (286, 180),
            'box': drink.ratio,
            'crop': True,
            'detail': True,
        }
            )           
        drinks.append(drinks_dict)
        
        
    order_form = OrderDrink()
    print(vars(order_form))
    return render(request,"index.html", {
    "drinks": drinks,
    "form": order_form
    })


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
    if Stortingen.objects.exists():
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
    else:
        html_table = "Het logboek is nog leeg"
    
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


@login_required
def bar_admin_add(request):
    if request.method == "POST":        
        form = Add_drink(request.POST,request.FILES)
        
        if form.is_valid():  
            final = form.save(commit=False) 
            final.dateTime = datetime.now().replace(microsecond=0)
            final.done_by = request.user
            final.save()
            messages.success(request,f"{request.POST['naam']} is toegevoegd voor €{request.POST['prijs']}")
    return render(request,"baradmin_add.html",{'form':Add_drink()})

@login_required
def bar_admin_change(request):
    return redirect(bar_admin_add)


@login_required
def bar_admin_delete(request):
    if request.method == "POST":
        drink = request.POST.get("drink")
        drankje = Drankjes.objects.get(drankjes_id=drink)
        messages.success(request,f"{drankje} Sucessvol verwijderd!")
        drankje.delete()
        
        
    return render(request,"baradmin_delete.html",{'form': Delete_drink()})

