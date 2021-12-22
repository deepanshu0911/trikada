from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

# fs = FileSystemStorage(location='/media/photos')
import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/products', filename)

class Customer(models.Model):
    username=models.CharField(max_length=30)
    gender=models.CharField(max_length=10)
    phone=models.IntegerField()
    email=models.CharField(max_length=200)
    addressline1=models.CharField(max_length=200)
    addressline2=models.CharField(max_length=150,null=True,blank=True)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=150)
    pincode=models.CharField(max_length=20)
    objects=models.Manager()
    def __str__(self):
        return self.username
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50,default="Trikada")
    seller = models.IntegerField(null=True,blank=True)
    title = models.CharField(max_length=150,null=True,blank=True)
    sku = models.CharField(max_length=150,null=True,blank=True)
    sellingPrice = models.IntegerField(null=True,blank=True)
    mrp = models.IntegerField(null=True,blank=True)
    off=models.IntegerField(null=True,blank=True)
    category = models.CharField(max_length=50,null=True,blank=True)
    subCategory = models.CharField(max_length=100,null=True,blank=True)
    subSubCategory = models.CharField(max_length=100,null=True,blank=True)
    suitableForMen = models.CharField(max_length=10,default="No",null=True,blank=True)
    suitableForWomen = models.CharField(max_length=10,default="No",null=True,blank=True)
    suitableForKids = models.CharField(max_length=10,default="No",null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    featureName1 = models.CharField(max_length=50,null=True,blank=True)
    featureName2 = models.CharField(max_length=50,null=True,blank=True)
    featureName3 = models.CharField(max_length=50,null=True,blank=True)
    featureName4 = models.CharField(max_length=50,null=True,blank=True)
    featureName5 = models.CharField(max_length=50,null=True,blank=True)
    featureName6 = models.CharField(max_length=50,null=True,blank=True)
    feature1 = models.CharField(max_length=100,null=True,blank=True)
    feature2 = models.CharField(max_length=100,null=True,blank=True)
    feature3 = models.CharField(max_length=100,null=True,blank=True)
    feature4 = models.CharField(max_length=100,null=True,blank=True)
    feature5 = models.CharField(max_length=100,null=True,blank=True)
    feature6 = models.CharField(max_length=100,null=True,blank=True)
    size1 =  models.CharField(max_length=15,null=True,blank=True)
    size2 =  models.CharField(max_length=15,null=True,blank=True)
    size3 =  models.CharField(max_length=15,null=True,blank=True)
    size4 =  models.CharField(max_length=15,null=True,blank=True)
    size5 =  models.CharField(max_length=15,null=True,blank=True)
    size6 =  models.CharField(max_length=15,null=True,blank=True)
    size7 =  models.CharField(max_length=15,null=True,blank=True)
    size8 =  models.CharField(max_length=15,null=True,blank=True)
    size9 =  models.CharField(max_length=15,null=True,blank=True)
    size10 =  models.CharField(max_length=15,null=True,blank=True)
    color1 = models.CharField(max_length=30,null=True,blank=True)
    color2 = models.CharField(max_length=30,null=True,blank=True)
    color3 = models.CharField(max_length=30,null=True,blank=True)
    color4 = models.CharField(max_length=30,null=True,blank=True)
    color5 = models.CharField(max_length=30,null=True,blank=True)
    color6 = models.CharField(max_length=30,null=True,blank=True)
    color7 = models.CharField(max_length=30,null=True,blank=True)
    color8 = models.CharField(max_length=30,null=True,blank=True)
    color9 = models.CharField(max_length=30,null=True,blank=True)
    color10 = models.CharField(max_length=30,null=True,blank=True)
    image1 = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    image2 = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    image3 = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    image4 = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    image5 = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    length = models.IntegerField(null=True,blank=True)
    breadth = models.IntegerField(null=True,blank=True)
    height = models.IntegerField(null=True,blank=True)
    weight = models.IntegerField(null=True,blank=True)
    warranty = models.CharField(max_length=100,null=True,blank=True)
    cod = models.CharField(null=True,blank=True,max_length=5,default="No")
    refund = models.CharField(null=True,blank=True,max_length=10,default="No")
    offers = models.CharField(max_length=200,null=True,blank=True)
    stock = models.IntegerField(null=True,blank=True)
    avgrating = models.IntegerField(null=True,blank=True,default=0)
    totalratings = models.IntegerField(null=True,blank=True)
    keywords = models.TextField(null=True,blank=True)
    approved = models.CharField(max_length=10,null=True,blank=True,default="No")
    objects=models.Manager()
    def __str__(self):
        return str(self.product_id)   
    def get_absolute_url(self):
        return reverse("product-edit",kwargs={"pk":self.pk})   
    def get_stock_url(self):
        return reverse("add-stock",kwargs={"pk":self.pk})    
    def view_product(self):
        return reverse("view-product",kwargs={"pk":self.pk})     

class Seller(models.Model):
    seller_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    brandName = models.CharField(max_length=50)
    sellerName = models.CharField(max_length=100)
    mobile = models.IntegerField()
    email = models.CharField(max_length=200)
    fromTime = models.TimeField(null=True,blank=True)
    toTime = models.TimeField(null=True,blank=True)
    businessName = models.CharField(max_length=100)
    businessDescription = models.TextField()
    tan = models.CharField(max_length=100,null=True,blank=True)
    gstin = models.CharField(max_length=100)
    businessLocation = models.CharField(max_length=100)
    addressline1 = models.CharField(max_length=150)
    addressline2 = models.CharField(max_length=150,null=True,blank=True)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    state =models.CharField(max_length=100)
    acHolderName = models.CharField(max_length=100)
    bankName = models.CharField(max_length=100)
    acNo = models.CharField(max_length=150)
    ifsc = models.CharField(max_length=150)
    approved = models.CharField(max_length=10,default="No")
    objects=models.Manager()
    def __str__(self):
        return self.brandName

class Rating(models.Model):
    username = models.CharField(max_length=50)
    product_id = models.IntegerField(null=True,blank=True)
    rating = models.IntegerField()
    date = models.DateField()
    objects=models.Manager()
    def __str__(self):
        return self.username

class Review(models.Model):
    username=models.CharField(max_length=50)
    name = models.CharField(max_length=100,null=True,blank=True)
    gender = models.CharField(max_length=20,null=True,blank=True)
    product_id = models.IntegerField(null=True,blank=True)
    review = models.TextField()
    rating = models.IntegerField(null=True,blank=True)
    date = models.DateField()
    objects=models.Manager()
    def __str__(self):
        return self.username

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    itemsjson = models.CharField(max_length=500,null=True,blank=True)
    totalPrice = models.IntegerField()
    username = models.CharField(max_length=30)
    name = models.CharField(max_length=100,null=True,blank=True)
    email = models.CharField(max_length=200,null=True,blank=True)
    phone = models.IntegerField(null=True,blank=True)
    alternatePhone = models.CharField(max_length=20,null=True,blank=True,default="Not Provided")
    addressline1=models.CharField(max_length=200)
    addressline2=models.CharField(max_length=150,null=True,blank=True)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=150)
    pincode=models.CharField(max_length=20)
    landmark = models.CharField(max_length=100,null=True,blank=True) 
    date = models.DateField()
    cleared = models.CharField(max_length=10,null=True,blank=True,default="No")
    status = models.CharField(max_length=15,null=True,blank=True,default="Ordered")
    statusjson = models.CharField(max_length=400,null=True,blank=True)
    delivered = models.CharField(max_length=10,default="No",null=True,blank=True)
    payment_status = models.CharField(max_length=20,default="Pending")
    paymentRequestId = models.CharField(max_length=200,null=True,blank=True)
    objects=models.Manager()
    def __str__(self):
        return str(self.order_id)
    def track_order(self):
        return reverse("track-order",kwargs={"pk":self.pk})     
    
class SellerOrder(models.Model):
     username = models.CharField(max_length=50,null=True,blank=True)
     seller_order_id = models.AutoField(primary_key=True)
     seller_id = models.IntegerField()
     product_id = models.IntegerField()
     sku = models.CharField(max_length=150,null=True,blank=True)
     productName = models.CharField(max_length=100,null=True,blank=True)
     price = models.IntegerField(null=True,blank=True)
     totalAmount = models.IntegerField(null=True,blank=True)
     qty = models.IntegerField()
     size = models.CharField(max_length=20,null=True,blank=True)
     color = models.CharField(max_length=30,null=True,blank=True)
     date = models.DateField(null=True,blank=True)
     orderStatus = models.CharField(max_length=15,null=True,blank=True,default="Pending")
     fromOrderId = models.IntegerField(null=True,blank=True)
     addressline1 = models.CharField(max_length=150,null=True,blank=True)
     addressline2 = models.CharField(max_length=150,null=True,blank=True)
     city = models.CharField(max_length=100,null=True,blank=True)
     state = models.CharField(max_length=100,null=True,blank=True)
     pincode = models.CharField(max_length=15,null=True,blank=True)
     objects=models.Manager()
     def __str__(self):
        return str(self.seller_order_id)

class Return(models.Model):
    return_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50,null=True,blank=True)
    seller_order_id = models.IntegerField(null=True,blank=True)
    seller_id = models.IntegerField(null=True,blank=True)
    fromOrderId = models.IntegerField(null=True,blank=True)
    product_id = models.IntegerField(null=True,blank=True)
    date = models.DateField()
    reason = models.TextField(null=True,blank=True)
    quantity = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=20,null=True,blank=True,default="Pending")
    totalAmount = models.IntegerField(null=True,blank=True)
    bankName = models.CharField(max_length=100,null=True,blank=True)
    acno = models.CharField(max_length=100,null=True,blank=True)
    ifsc = models.CharField(max_length=100,null=True,blank=True)
    objects=models.Manager()
    def __str__(self):
        return str(self.return_id)

class Earning(models.Model):
    earn_id = models.AutoField(primary_key=True)
    seller_id = models.IntegerField(null=True,blank=True)
    lastEarning = models.IntegerField(default=0)
    totalEarning = models.IntegerField(default=0)
    date = models.DateField(null=True,blank=True)
    lastPaymentDate = models.DateField(null=True,blank=True)
    objects=models.Manager()
    def __str__(self):
        return str(self.seller_id)


class Feedback(models.Model):
    username = models.CharField(max_length=50,null=True,blank=True)
    name= models.CharField(max_length=50,null=True,blank=True)
    email=models.CharField(max_length=150,null=True,blank=True)
    message = models.TextField(null=True,blank=True)
    objects=models.Manager()
    def __str__(self):
        return self.name









