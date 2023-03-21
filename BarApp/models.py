from django.db import models
from django.contrib.auth import get_user_model
import os

def img_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_.%s" % (instance.naam, ext)
    return os.path.join('drinks', filename)

# Create your models here.

class Saldo(models.Model):
    user = models.OneToOneField(get_user_model(),primary_key=True,on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        db_table = 'Saldo'
        verbose_name_plural = "Saldo's"
    def __str__(self) -> str:
        return f"{self.user} | €{self.saldo}"
        
class Stortingen(models.Model):
    storting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    saldo_voor = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    saldo_na = models.DecimalField(max_digits=5, decimal_places=2)
    dateTime = models.DateTimeField()
    done_by =  models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="Executed_by")
    
    class Meta:
        db_table = 'Stortingen'
        verbose_name_plural = "Stortingen"
    def __str__(self) -> str:
        
        return f"{self.dateTime.strftime('%A %d-%B %X')} | {self.user} +€{self.amount} by {self.done_by}"

class Drankjes(models.Model):
    drankjes_id = models.AutoField(primary_key=True)
    naam = models.CharField(max_length=128)
    prijs = models.DecimalField(max_digits=5,decimal_places=2)
    img = models.ImageField(upload_to=img_filename)
    dateTime = models.DateTimeField()
    done_by =  models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="Added_by")
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Drankjes'
        verbose_name_plural = "Drankjes"
    def __str__(self) -> str:
        return f"{self.naam} | €{self.prijs}"
    
    

class Transacties(models.Model):
    transactie_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    drankje = models.ForeignKey('Drankjes',on_delete=models.CASCADE)
    dateTime = models.DateTimeField()
    
    class Meta:
        db_table = 'Transacties'
        verbose_name_plural = "Transacties"
    def __str__(self):
        return f"{self.transactie_id}|{self.dateTime}|{self.user}|{self.drankje}"
        
class Tikkie(models.Model):
    id = models.AutoField(primary_key=True)
    link = models.CharField(max_length=128)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Tikkies'
        verbose_name_plural = "Tikkies"
        
    def __str__(self):
        return f"{self.link} by {self.user}"
    
    
    