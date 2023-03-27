from django.db import models
from django.contrib.auth import get_user_model
import os
from image_cropping import ImageRatioField,ImageCropField

def img_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.naam, ext)
    return os.path.join('drinks', filename)

# Create your models here.

class Saldo(models.Model):
    """Saldo table in database
    Users either have 1 entry or no entry.
    One gets created automatically on account creation. 
    So usually only admin account has no Entry
    If user gets deleted delete their entry

    :param models: _description_
    :return: _description_
    """
    user = models.OneToOneField(get_user_model(),primary_key=True,on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        db_table = 'Saldo'
        verbose_name_plural = "Saldo's"
    def __str__(self) -> str:
        return f"{self.user} | €{self.saldo}"
        
class Stortingen(models.Model):
    """Stortingen
    Keeps track of the data amount and user who made the deposit. 
    Also saves the Saldo changes.
    :param models: _description_
    :return: _description_
    """
    storting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    saldo_voor = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    saldo_na = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    time = models.TimeField()
    done_by =  models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="Executed_by")
    
    class Meta:
        db_table = 'Stortingen'
        verbose_name_plural = "Stortingen"
    def __str__(self) -> str:
        
        return f"{self.date.strftime('%A %d-%B')} {self.time.strftime('%X')} | {self.user} +€{self.amount} by {self.done_by}"

class Drankjes(models.Model):
    """Drankjes
    Table which stores the drankjes. 
    Stores their price description and creation date. 

    :param models: _description_
    :return: _description_
    """
    drankjes_id = models.AutoField(primary_key=True)
    naam = models.CharField(max_length=128)
    prijs = models.DecimalField(max_digits=5,decimal_places=2)
    description = models.CharField(max_length=512,blank=True)
    img = ImageCropField(upload_to=img_filename,blank=True,null=True)
    ratio = ImageRatioField('img','286x180')
    date = models.DateField()
    time = models.TimeField()
    done_by =  models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="Added_by")
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Drankjes'
        verbose_name_plural = "Drankjes"
    def __str__(self) -> str:
        return f"{self.naam} | €{self.prijs}"
    
    

class Transacties(models.Model):
    """Transacties
    Stores which drink was bought and what effect this had on saldo. 
    If drink gets deleted field gets set to NULL

    :param models: _description_
    :return: _description_
    """
    transactie_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    drankje = models.ForeignKey('Drankjes',null=True,on_delete=models.SET_NULL)
    date = models.DateField()
    time = models.TimeField()
    done_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="Bought_by")
    saldo_voor = models.DecimalField(max_digits=5,decimal_places=2)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    saldo_na = models.DecimalField(max_digits=5,decimal_places=2)
    class Meta:
        db_table = 'Transacties'
        verbose_name_plural = "Transacties"
    def __str__(self):
        return f"{self.transactie_id}|{self.date}{self.time}|{self.user}|{self.drankje}"
        
class Tikkie(models.Model):
    """Saves the latest Tikkie link

    :param models: _description_
    :return: _description_
    """
    id = models.AutoField(primary_key=True)
    link = models.CharField(max_length=128)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Tikkies'
        verbose_name_plural = "Tikkies"
        
    def __str__(self):
        return f"{self.link} by {self.user}"
    
    
    