from BarApp.models import Saldo

def saldo(request):
    """
    context_processor which makes saldo variable available for all user.
    If no user is logged in return NaN

    :param request: django request object
    :return: current user's saldo if logged in else NaN
    """
    saldo = Saldo.objects.filter(user_id=request.user.id)
    if len(saldo) > 0:
        return {'saldo': saldo[0].saldo}
    else:
        return {'saldo': "NaN"}