# ecommerceapp/models.py
from django.db import models


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300,null=True, blank=True, default='No descrp')
    pub_date = models.DateField()

    image = models.ImageField(upload_to='shop/images')

    def __str__(self):
        return self.product_name

class Contact(models.Model):
    contact_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.EmailField()
    message=models.TextField(max_length=500)
    phonenumber=models.IntegerField()
    
    def __str__(self):
        return self.name
    
from django.db import models
from .models import Product

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    session_id = models.CharField(max_length=255)  # Or use user relationship if you have users

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name}"
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.TextField()
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    email = models.EmailField()
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    paymentstatus = models.CharField(max_length=20, default='Pending')
    amountpaid = models.FloatField(default=0.0)

class OrderUpdate(models.Model):
    order_id = models.IntegerField()
    update_desc = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)