from BarApp.models import Saldo

def saldo(request):
    saldo = Saldo.objects.filter(user_id=request.user.id)
    if len(saldo) > 0:
        return {'saldo': saldo[0].saldo}
    else:
        return {'saldo': "NaN"}