from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from BarApp.models import *
from BarApp.forms import *
from django.templatetags.static import static
from datetime import datetime,timedelta
import pandas as pd
from operator import itemgetter
from image_cropping.utils import get_backend
from django.db.models import Q
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from bokeh.models import HoverTool


pd.set_option("colheader_justify", "left")


def get_storting_table(objects,maxRows=25):
    """Converts a Storting Queryset into a panda's html table. Sorted on date and time.

    :param objects: Stortingen queryset retrieved from database!
    :param maxRows: Maximum number of rows to display, defaults to 25
    :return: _description_
    """
    if Stortingen.objects.exists():
        df = pd.DataFrame(list(objects.values("date","time","user_id","saldo_voor","amount","saldo_na","done_by_id")))
        df.sort_values(by=["date","time"],ascending=False,inplace=True)
        df["user_id"] = [User.objects.get(id=i) for i in df["user_id"]]
        df["done_by_id"] = [User.objects.get(id=i) for i in df["done_by_id"]]
        df['date'] = [i.strftime("%A %d-%B") for i in df["date"]]
        df['time'] = [i.strftime("%X") for i in df["time"]]
        df.columns = ["Datum","Tijd","Saldo van","Saldo voor","Bedrag","Saldo Na","Uitgevoerd door"]
        html_table = df.to_html(classes="table table-striped table-bordered",index=False,max_rows=maxRows)
    else:
        html_table = "Het logboek is nog leeg"
    return html_table

# Create your views here.


@login_required
def index(request):
    """Index function
    @login_required decorator Only usable after login. 
    If request is GET it will get all active drinks from database and put them into dictonary for client to render. 
    
    If request is POST it will collect data send by the client and substract it from the supplied users saldo. And add a transaction for them

    Uses index.html as template
    Uses OrderDrink form from forms.py
    :param request: _description_
    :return: Webpage
    """
    if request.method == "POST":
        user_id_list = request.POST.getlist("user")
        selectedUsers = User.objects.filter(id__in=user_id_list)
        drinkId = request.POST.get("drinkId")
        drinkObj = Drankjes.objects.filter(drankjes_id=drinkId)
        if len(drinkObj) > 0:
            drinkObj = drinkObj[0]
            for user in selectedUsers:
                userSaldo = Saldo.objects.get(user=user)
                saldoVoor = userSaldo.saldo
                userSaldo.saldo -= drinkObj.prijs
                saldoNa = userSaldo.saldo
                transactie = Transacties(
                    user=user,
                    drankje=drinkObj,
                    date = datetime.now().date(),
                    time = datetime.now().time().replace(microsecond=0),
                    saldo_voor = saldoVoor,
                    amount = -drinkObj.prijs,
                    saldo_na = saldoNa,
                    done_by= request.user
                )
                transactie.save()
                userSaldo.save()
            messages.success(request,f"{request.user} je hebt {drinkObj.naam} besteld voor: {', '.join([str(i) for i in selectedUsers])}")
        
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
            drinks_dict["img"] = static('img/basic_bottle.svg')
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
    drinks = sorted(drinks,key=itemgetter("naam"))
    order_form = OrderDrink(initial={'user' : [request.user.id]})
    return render(request,"index.html", {
    "drinks": drinks,
    "form": order_form
    })


def register(request):
    """register function
    Lets users register an account. If request is POST checks if username is taken and if passwords match. 
    If credentials are valid Utilises Django backend to generate a user with salted and hashed password.
    It also logs this user in.
    
    If request GET renders the plain HTML. 
    
    Uses register.html as template

    :param request: _description_
    :return: _description_
    """
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
    """Logs current user in
    Users get send to this page if they are not logged in with a page that has the 
    @login_required decorator. 
    Uses Django backend to authenticate user password. 
    If authentication is valid user gets logged in. 
    
    Utilises login.html as template

    :param request: _description_
    :return: _description_
    """
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
    """Log current user out
    Logs out the currently logged in user.
    If no user is logged in does nothing.
    redirects to the homepage after logout. 
    :param request: _description_
    :return: _description_
    """
    logout(request)
    messages.success(request,"Je bent nu uitgelogt!")
    return redirect(index)



    
@login_required
def add_saldo(request):
    """Page for users to deposit saldo.
    Utilises AddMoney form from forms.py to generate form to deposit saldo. 
    Will only allow to deposit to users which have an entry in the Saldo database. 
    Also renders the latest Tikkielink that was stored in the database.
    Finally it utilises the get_storting_table() function table to get the last 25 stortingen
    
    If request is POST it will add the supplied saldo to the supplied users saldo. 
    It will also track who made the transaction and what the exact statistics were.
    
    Uses add_saldo.html as template
    :param request: _description_
    :return: _description_
    """
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
                date=datetime.now().date(),
                time= datetime.now().replace(microsecond=0).time())
            
            saldo.saldo = new_saldo
            saldo.save()
            storting.save()
    html_table = get_storting_table(Stortingen.objects.all())
    
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
    
@login_required    
def tikkie_change(request):
    """changes the Tikkie link in the database
    Utilises the @login_required decorator
    Only accepts POST request. GET will redirect to add_saldo()
    If request is post it will change the link in the database. It also stores who made the change.


    Since it only accepts POST it has no HTML template
    :param request: _description_
    :return: _description_
    """
    if request.method == "POST":
        link = request.POST.get("link")
        t = Tikkie(link=link,user=request.user)
        t.save()
        
    return redirect(add_saldo)


@login_required
def bar_admin_add(request):
    """Allows users to add drinks that can be ordered. 
    utilises the @login_required decorator.
    If request is GET it will use the AddDrink() form from forms.py to give options
    If request is POST it will save everything including the image to the database. 
    Current date and time is stored alongside data.

    Uses baradmin_add.html as template
    :param request: _description_
    :return: _description_
    """
    if request.method == "POST":        
        form = AddDrink(request.POST,request.FILES)
        
        if form.is_valid():  
            final = form.save(commit=False) 
            final.date = datetime.now().date()
            final.time = datetime.now().replace(microsecond=0).time()
            final.done_by = request.user
            final.save()
            messages.success(request,f"{request.POST['naam']} is toegevoegd voor €{request.POST['prijs']}")
    return render(request,"baradmin_add.html",{'form':AddDrink()})

@login_required
def bar_admin_update(request):
    """Allows users to make changes to drinks
    Utilises the @login_required decorator 
    On GET checks if a drink was selected. If this was the case render the UpdateDrinkModel() form for that specific drink. 
    
    ON POST Utilises the AddDrink() form to update the drink in the database by supplying the instance
    Uses baradmin_update.html as template
    :param request: _description_
    :return: _description_
    """
    if request.method == "POST":
        drinkModel = Drankjes.objects.filter(drankjes_id=request.POST.get("drinkId"))
        if drinkModel:
            form = AddDrink(request.POST,request.FILES,instance=drinkModel[0])
            if form.is_valid():  
                final = form.save(commit=False) 
                final.date = datetime.now().date()
                final.time = datetime.now().replace(microsecond=0).time()
                final.done_by = request.user
                final.active = request.POST.get('active') == 'on'
                final.save()
                messages.success(request,f"{request.POST['naam']} is succesvol aangepast!")
        
    updateDrinkForm = None
    drink_id = request.GET.get("drink")
    drinkForm = UpdateDrink(initial={"drink":drink_id})
    if drink_id:
        drinkModel = Drankjes.objects.filter(drankjes_id=drink_id)
        if drinkModel:
            updateDrinkForm = UpdateDrinkModel(instance=drinkModel[0])
    return render(request,"baradmin_update.html",{
        "drinkId": drink_id,
        "drinkForm": drinkForm,
        "updateDrinkForm": updateDrinkForm
        
    })


@login_required
def bar_admin_delete(request):
    """Allows users to delete drinks
    Utilises the @login_required decorator
    On GET render page with DeleteDrink() form from forms.py 
    
    On POST delete supplied drink. 

    Uses baradmin_delete.html as template
    :param request: _description_
    :return: _description_
    """
    if request.method == "POST":
        drink = request.POST.get("drink")
        drankje = Drankjes.objects.get(drankjes_id=drink)
        messages.success(request,f"{drankje} Sucessvol verwijderd!")
        drankje.delete()
        
        
    return render(request,"baradmin_delete.html",{'form': DeleteDrink()})

def log_storting(request):
    """Generate a table about stortingen based on queries. 
    
    Allows users to supply users to see deposits for certain users and who did those. 
    Utilises the UserStortingLog() form for selection of users. 
    
    IF GET request has arguments it also executes a database query to fetch results. 
    Then uses the get_storting_table() function to render these objects into an html table
    
    Uses log_storting.html as template

    :param request: _description_
    :return: _description_
    """
    getTuple = request.GET.get("usr"),request.GET.get("exe"),request.GET.get("dT")
    if any(getTuple):
        usr,exe,dT = getTuple
        query = Q()
        if usr:
            query &= Q(user=usr)
        if exe: 
            query &= Q(done_by=exe)        
        if dT:
            dT=datetime.strptime(dT, '%Y-%m-%d').date()
            query &= Q(date=dT)

        selected = Stortingen.objects.filter(query)
        html_table = get_storting_table(selected,100)
        form = UserStortingLog(initial={'usr':usr,'exe':exe,"dT":request.GET.get("dT")})
    else: 
        html_table = get_storting_table(Stortingen.objects.all())
        form = UserStortingLog()
        
        
    return render(request,"log_storting.html",{
        "form": form,
        "table": html_table
        
        
    })

def log_saldo(request):
    """Gets the Saldo log for users
    Utilises UserSaldoLog from Forms.py for user selection
    If no users is selected it returns a table of all Saldo's and a barplot of all saldo's 
    
    If a user is selected it joins the Transacties and Stortingen database to make a line grapth to depict their saldo over time. 
    It also displays these values in a table

    Uses log_saldo.html as template
    :param request: _description_
    """
    usr = request.GET.get('usr')
    if not usr:
        usr = None
    user = User.objects.filter(id=usr)
    plotTitle,html_table,script,div = "Geen data beschikbaar",None,None,None
    if len(user) == 0: #No users were supplied 
        if Saldo.objects.exists():
            #Reading and converting database into pandas table
            df = pd.DataFrame(list(Saldo.objects.all().values("user","saldo")))
            df = df.sort_values(by="user",ascending=True)
            df["user"] = [User.objects.get(id=i).username for i in df["user"]]
            df["saldo"] = [float(i) for i in df["saldo"]]
            df.style.set_properties(**{'text-align': 'left'})
            #Code to generate vbar plot of saldo's
            p = figure(x_range=df["user"],y_range=(df.saldo.min()-1,df.saldo.max()+5),toolbar_location=None)
            df["colors"] = ["green" if i > 0 else "red" for i in df['saldo']]
            p.vbar(x="user",top="saldo",color="colors", source=df, width=0.9)
            ht = HoverTool(
                tooltips = [
                ("Gebruiker","@user"),
                ("Saldo","€@saldo{0.00}"),],)           
            p.line(x=(-1,len(df["user"])+5), y=0,color="black",width=5)
            p.toolbar.active_drag = None
            p.toolbar.active_scroll = None
            p.toolbar.active_tap = None
            p.add_tools(ht)
            # Rendering and formatting of plot and table into HTML
            plotTitle = "Plot van alle saldo's van alle gebruikers!"
            script, div = components(p)
            df["saldo"] = [f"€{i}" for i in df["saldo"]]
            df.columns = ["Gebruiker","Saldo","Kleur"]
            html_table = df.to_html(classes="table table-striped table-bordered table-sm mt-3",index=False,columns=df.columns[0:2])
    else: # A users was selected
        user = user[0]
        stortingen = pd.DataFrame(list(Stortingen.objects.filter(user=user).values("storting_id","date","time","saldo_voor","amount","saldo_na","done_by")))
        transacties = pd.DataFrame(list(Transacties.objects.filter(user=user).values("transactie_id","date","time","saldo_voor","amount","saldo_na","drankje","done_by")))
        if not stortingen.empty or not transacties.empty: # If user has no Deposits or Transactions Skis this code 
            stortingen["drankje"] = [float("NaN")]*len(stortingen)
            stort_trans = pd.concat([stortingen,transacties]) # Join stortingen & Transacties table
            drinks = []
            for i in stort_trans["drankje"]:
                if i.is_integer():
                    drinks.append(Drankjes.objects.get(drankjes_id=i).naam)
                else:
                    drinks.append("NaN")
            stort_trans["drankje"] = drinks        
            stort_trans.sort_values(by=["date","time"],inplace=True)
            stort_trans["done_by"] = [User.objects.get(id=i).username for i in stort_trans["done_by"]]
            stort_trans.saldo_voor = stort_trans.saldo_voor.astype(float)
            stort_trans.amount = stort_trans.amount.astype(float)
            stort_trans.saldo_na = stort_trans.saldo_na.astype(float)
            ids,st_type = [],[]
            #If one ot the tables is empty add their Id as NaN which is expected by future code
            if stortingen.empty:
                stort_trans["storting_id"] = [float('NaN')]*len(stort_trans)
            if transacties.empty:
                stort_trans["transactie_id"] = [float('NaN')]*len(stort_trans)    
            #Get all id's and save the valid ID to the ID column
            for s,t in zip(stort_trans["storting_id"],stort_trans["transactie_id"]):
                if isinstance(s,int) or s.is_integer():
                    st_type.append("Storting")
                    ids.append(int(s))
                elif isinstance(t,int) or t.is_integer():
                    st_type.append("Transactie")
                    ids.append(int(t))
            stort_trans.drop(columns=["storting_id","transactie_id"],inplace=True)
            stort_trans.insert(0,"id",ids)
            stort_trans.insert(1,"type",st_type)
            #Combines the Date and Time objects for sorting on dateTime
            stort_trans["dT"] = [datetime.combine(d,t) for d,t in zip(stort_trans["date"],stort_trans["time"])]
            r1 = [0,"Storting",user.date_joined.replace(tzinfo=None,microsecond=0).date(),user.date_joined.replace(tzinfo=None,microsecond=0).time(),0.0,0.0,0.0,"admin","NaN",user.date_joined.replace(tzinfo=None,microsecond=0)]
            d = {k:v for k,v in zip(stort_trans.columns,r1)}
            stort_trans = pd.concat([pd.DataFrame(d,index=[0]),stort_trans],ignore_index=True)
            #Generate Bokeh plot on Panda's dataframe stort_trans
            tools = "pan,reset,xwheel_zoom"
            dt_range = (stort_trans.dT.min()-timedelta(hours=6),stort_trans.dT.max()+timedelta(hours=6))
            p = figure(x_range=dt_range,y_range=(stort_trans.saldo_na.min()-5,stort_trans.saldo_na.max()+5),tools=tools, active_scroll='xwheel_zoom')
            colormap = {"Storting":"green","Transactie":"red"}
            stort_trans["colors"] = [colormap[x] for x in stort_trans['type']]
            p.line("dT","saldo_na",source=stort_trans,line_width=2,color="black")
            p.circle("dT","saldo_na",source=stort_trans,size=10,color="colors")
            p.xaxis.formatter = DatetimeTickFormatter(minutes="%H:%M:%S",hours="%H:%M:%S",days="%d-%b %Hh",months="%d-%m-%Y",years="%d-%m-%Y")
            ht = HoverTool(
                tooltips = [
                ("Id","@id"),
                ("Type","@type"),
                ("Drankje","@drankje"),
                ("Saldo voor","€@saldo_voor{00.00}"),
                ("Bedrag","€@amount{00.00}"),
                ("Saldo na","€@saldo_na{00.00}"),
                ("Datum","@date{%d-%m-%Y}"),
                ("Tijd","@time{%H:%M:%S}"),
                ("Uitgevoerd door","@done_by"),
                ],formatters={'@date': 'datetime','@time': 'datetime'})
            p.add_tools(ht)
            plotTitle = f"Saldoverloop van {user.username}"
            script, div = components(p)
            colnames = ["Id","Type","Datum","Tijd","Saldo Voor","Bedrag","Saldo Na","Uitgevoerd door","Drankje","DateTime","cols"]
            stort_trans.columns = colnames
            html_table = stort_trans.to_html(classes="table table-striped table-bordered table-sm mt-3",index=False,columns=colnames[0:9])
    
    form = UserSaldoLog(initial={"usr":usr})
    return render(request,"log_saldo.html",{
        "form": form,
        "table": html_table,
        "plotTitle": plotTitle,
        "script": script,
        "div": div,
    })
    

def log_drink(request):
    """Makes a plot of total drinks sold
    Allows users to supply a date. Returns all drinks sold on that date. 
    If no date is supplied returns stats of all time. 
    If no drinks are sold on date. Skips generating plot
    Uses DateDrinkLog() as form
    
    Uses log_drinks.html as template

    :param request: _description_
    :return: _description_
    """
    plotTitle,script,div = "Geen data beschikbaar",'',''
    dT = request.GET.get("dT")
    
    if dT:
        orders = Transacties.objects.filter(date=datetime.strptime(dT, '%Y-%m-%d').date())
        plotTitle = f"Drankjes verkocht op {'-'.join(dT.split('-')[::-1])}"
    else:
        orders = Transacties.objects.all()
        plotTitle = "Verkochte drankjes"
    
    if len(orders) > 0:
        count_dict = {}
        for i in orders:
            if i.drankje is not None:
                if i.drankje.naam not in count_dict:
                    count_dict[i.drankje.naam] = 1
                else:
                    count_dict[i.drankje.naam] +=1

        p = figure(x_range=list(count_dict.keys()),y_range=(0,max(count_dict.values())+1),toolbar_location=None)


        p.vbar(x=list(count_dict.keys()),top=list(count_dict.values()), width=0.9)

        ht = HoverTool(
        tooltips = [
        ("Drankje","@x"),
        ("Aantal verkocht","@top"),
        ],)           
        p.toolbar.active_drag = None
        p.toolbar.active_scroll = None
        p.toolbar.active_tap = None
        p.add_tools(ht)

        script, div = components(p)

    else:
        plotTitle = f"Er zijn geen drankjes verkocht op {'-'.join(dT.split('-')[::-1])}"
    form = DateDrinkLog(initial={"dT":dT})
    return render(request,"log_drinks.html",{
        "form": form,
        "plotTitle": plotTitle,
        "div": div,
        "script": script,
    })