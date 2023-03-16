from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm 
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
# Create your views here.

def index(request):
    return render(request,"index.html")


def register(request):  
    if request.POST == 'POST':  
        form = UserCreationForm()  
        if form.is_valid():  
            form.save()  
            messages.add_message(request,messages.SUCCESS,'Account sucessvol aangemaakt!')  
    else:  
        form = UserCreationForm()  
    context = {  
        'form':form  
    }  
    return render(request, 'register.html', context)  

def v_login(request):
    renderdict = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request,user)
            renderdict["message"] = f"{user.username} is nu ingelogt"
        else:
            renderdict["message"] = "Ongeldige combinatie van username of wachtwoord"
            
    return render(request,"login.html",renderdict)

def v_logout(request):
    logout(request)
    logmsg="Je bent sucessvol uitgelogt!"
    return render(request,"logout.html",{
        "logoutmsg": logmsg
    })
    
def add_saldo(request):
    return render(request,"add_saldo.html")