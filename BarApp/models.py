from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Saldo(models.Model):
    user = models.OneToOneField(get_user_model(),primary_key=True,on_delete=models.CASCADE)
    # username = models.ForeignKey(get_user_model().username,on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        db_table = 'Saldo'
        
class Stortingen(models.Model):
    storting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    saldo_voor = models.DecimalField(max_digits=5, decimal_places=2)
    storing_amount = models.DecimalField(max_digits=5, decimal_places=2)
    saldo_na = models.DecimalField(max_digits=5, decimal_places=2)
    dateTime = models.DateTimeField()
    
    class Meta:
        db_table = 'Stortingen'

class Drankjes(models.Model):
    drankjes_id = models.AutoField(primary_key=True)
    naam = models.CharField(max_length=128)
    prijs = models.DecimalField(max_digits=5,decimal_places=2)
    class Meta:
        db_table = 'Drankjes'
    

class Transacties(models.Model):
    transactie_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    drankje = models.ForeignKey('Drankjes',on_delete=models.CASCADE)
    dateTime = models.DateTimeField()
    
    class Meta:
        db_table = 'Transacties'
    
    