from django.shortcuts import render, HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.core.mail import EmailMultiAlternatives
import math,random
from django.utils import timezone
import datetime
from django.views import View
import pytz
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.db.models import Q
from website.models import Customer, Product, Seller, Rating, Review, Order, SellerOrder, Return, Feedback, Earning
import json
from instamojo_wrapper import Instamojo

def index(request):
    menproducts = Product.objects.filter(category="Men's Fashion",approved="Yes").order_by(Coalesce('product_id','avgrating').desc())
    womenproducts = Product.objects.filter(category="Women's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())
    products = {
        'menproducts' : menproducts,
        'womenproducts' : womenproducts,
    }

    return render(request,'index.html',products)

def terms(request):
   return render(request,'terms-of-use.html')

def privacy(request):
    return render(request,'privacy-policy.html')

def disclaimer(request):
    return render(request,'disclaimer.html')   

def returnpolicy(request):
    return render(request,'return-policy.html')

def signupuserval(request):
    if request.method == 'POST':
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if len(password) < 8:
            messages.error(
                request, "Password must contain atleast 8 charactors")
            return redirect('/')
        if User.objects.filter(username=username).exists():
            messages.error(
                request, "This username or email is already registered.")
            return redirect('/')
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.first_name = firstname
        user.last_name = lastname
        user.is_active = False
        user.save()
        messages.success(
            request, 'Email sent. Verify your account')
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
        activate_url = 'https://'+domain+link
        send_mail("Welcome to the Trikada","Hello! "+str(firstname)+" You have successfully signed up to our website. Please use the below link to verify your account.\n"+activate_url,settings.EMAIL_HOST_USER,[email])
        return redirect('/')

    else:
        return HttpResponse('404 - Not Found')


def loginuserval(request):
     if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('/')
        else:
            messages.error(request, "Username or password is incorrect.")
            return redirect('/')
     else:
        return HttpResponse('404 - Not Found')

class VerificationView(View):
   def get(self, request, uidb64, token):
    try:
       id = force_str(urlsafe_base64_decode(uidb64))   
       user = User.objects.get(pk=id)
       if not token_generator.check_token(user, token):
           messages.success(request,'Account already verified.')
           return redirect('/')      
       if user.is_active:
           return redirect('/')
       user.is_active = True
       user.save()    
       messages.success(request,"Account verified successfully.")
       return redirect('/')
    except Exception:
        pass
    return redirect('/')

def logoutuser(request):
   if request.user.is_authenticated : 
     logout(request)
     messages.success(request, 'You are logged out successfully')
     return redirect('/')
   else :
      return HttpResponse('Invalid request')

def resetpassworddone(request):
    if request.user.is_anonymous:
       return render(request,'reset_password_sent.html')       
    else:
        return HttpResponse('Invalid request')

def profile(request):
    if request.user.is_anonymous:
        return redirect('/')
    try:
     profile=Customer.objects.get(username=request.user)
     profile={
        'profile':profile
     }
     return render(request,'profile.html',profile)
    except ObjectDoesNotExist:
        return render(request,'profile.html')

def profileupdate(request):
    if request.user.is_anonymous:
        return redirect('/')
    if request.method == "POST" :
       username=request.user
       gender=request.POST.get('gender')
       email=request.POST.get('email')
       phone=request.POST.get('phone')
       addressline1=request.POST.get('addline1')
       addressline2=request.POST.get('addline2')
       city=request.POST.get('city')
       pincode=request.POST.get('pincode')
       state=request.POST.get('state')
       
       Customer.objects.create(username=username,gender=gender,email=email,
       phone=phone,addressline1=addressline1,addressline2=addressline2,
       city=city,pincode=pincode,state=state)  
       messages.success(request,"Details updated successfully")
       return redirect('/profile_details')
    else:
        messages.success(request,"There is an error. Try again.")
        return redirect('/profile_details')

def profilereupdate(request):
    if request.user.is_anonymous:
        return redirect('/')
    if request.method == "POST" :
       username=request.user
       gender=request.POST.get('gender')
       email=request.POST.get('email')
       phone=request.POST.get('phone')
       addressline1=request.POST.get('addline1')
       addressline2=request.POST.get('addline2')
       city=request.POST.get('city')
       pincode=request.POST.get('pincode')
       state=request.POST.get('state')
       
       Customer.objects.filter(username=username).update(gender=gender,email=email,
       phone=phone,addressline1=addressline1,addressline2=addressline2,
       city=city,pincode=pincode,state=state)  
       messages.success(request,"Details updated successfully")
       return redirect('/profile_details')
    else:
        messages.success(request,"There is an error. Try again.")
        return redirect('/profile_details')

def sellerpage(request):
    try :
        seller = Seller.objects.get(username=request.user)
        sellerdetails = {
            'seller' : seller
        }
        return redirect('/seller_dashboard',sellerdetails)
    except ObjectDoesNotExist:
       return render(request,'seller.html')

def sellerregisterpage(request):
    if request.user.is_anonymous:
        messages.error(request,"Please log in or sign up to continue.")
        return redirect('/become_a_seller')
    return render(request,'register.html')

def registerseller(request):
    if request.user.is_anonymous:
        return redirect('/')
    if request.method == "POST" :
        username = request.user
        brandName = request.POST.get('brand')
        sellerName = request.POST.get('sellername')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        businessName = request.POST.get('businessname')
        businessDescription = request.POST.get('description')       
        tan = request.POST.get('tan')
        gstin = request.POST.get('gstin')
        businessLocation = request.POST.get('businessaddress')
        addressLine1 = request.POST.get('addressline1')
        addressLine2 = request.POST.get('addressline2')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        acHolderName = request.POST.get('acholdername')
        bankName = request.POST.get('bankname')
        acNo = request.POST.get('acno')
        ifsc = request.POST.get('ifsccode')
        Seller.objects.create(username=username,brandName=brandName,sellerName=sellerName,
        mobile=mobile,email=email,businessName=businessName,
        businessDescription=businessDescription,tan=tan,gstin=gstin,businessLocation=businessLocation,
        addressline1=addressLine1,addressline2=addressLine2,city=city,pincode=pincode,
        state=state,acHolderName=acHolderName,bankName=bankName,acNo=acNo,ifsc=ifsc)
        messages.success(request,"Details added successfully.")
        return redirect('/')
    return HttpResponse('404 - Not Found')  

def sellerdashboard(request):
   try: 
    seller = Seller.objects.get(username=request.user)
    if seller.approved == "No":
        messages.success(request,"Account Sent for Approval. Please Wait!")
        return redirect('/')
    elif seller.approved == "Yes" :    
      products = Product.objects.filter(seller=seller.seller_id,approved="Yes").order_by(Coalesce('product_id','category').desc())
      earning = Earning.objects.get(seller_id=seller.seller_id)
      sellerdetails = {
        'seller' : seller,
        'products': products,
        'earning' : earning
      }
      return render(request,'sellerdashboard.html',sellerdetails)
   except:
       return redirect('/')
def sellersearch(request):
    if request.method == "GET" :
        query = request.GET.get('search')
        if query:
            seller = Seller.objects.get(username=request.user,approved="Yes")
            products = Product.objects.filter(seller=seller.seller_id,approved="Yes").filter(Q(title__icontains=query)|Q(sku__icontains=query)|Q(keywords__icontains=query)
            |Q(category__icontains=query)|Q(subCategory__icontains=query)|Q(product_id__icontains=query)|
           Q(subSubCategory__icontains=query)|Q(sellingPrice__icontains=query)).order_by(Coalesce('product_id','category').desc())
            earning = Earning.objects.get(seller_id=seller.seller_id)
            sellerdetails = {
                'products' : products,
                'seller' : seller,
                'earning' : earning
            }
            return render(request,'sellerdashboard.html',sellerdetails)
        else :
            return redirect('/seller_dashboard')
    else:
        return HttpResponse('Invalid Request')            


def selleraccount(request):
    seller = Seller.objects.get(username=request.user,approved="Yes")
    sellerdetails = {
       'seller':seller
    }
    return render(request,'selleraccount.html',sellerdetails)

def sellerorders(request):
    if request.user.is_authenticated:
    #    try:
           seller = Seller.objects.get(username=request.user,approved="Yes")
           sellerorders = SellerOrder.objects.filter(seller_id=seller.seller_id).order_by(Coalesce('seller_order_id','date').desc())
           earning = Earning.objects.get(seller_id=seller.seller_id)
           if request.method == "GET" :
              query = request.GET.get('search')
              if query is not None:
                  match = SellerOrder.objects.filter(seller_id=seller.seller_id).filter(Q(orderStatus__icontains=query)|Q(sku__iexact=query)|
                  Q(seller_order_id__iexact=query)|Q(product_id__iexact=query)).order_by(Coalesce('seller_order_id','date').desc())
                  if match :
                      sellerorders = match
                  else:
                      pass
              else:
                  pass
           orderpage = {
               'orders' : sellerorders,
               'seller' : seller,
               'resultno' : len(sellerorders),
               'earning' : earning
           }
           return render(request,'seller-orders.html',orderpage)
    #    except:
        #    return redirect('/')     
    return HttpResponse('Invalid Request')

def orderpacked(request):
    if request.method == "POST":
        seller_order_id = request.POST.get('seller_order_id')
        packed = request.POST.get('packed')
        SellerOrder.objects.filter(seller_order_id=seller_order_id).update(orderStatus=packed)
        messages.success(request,"Order Sent for Shipment")
        return redirect('/orders')
    return HttpResponse('Invalid Request')    

def sellerreturns(request):
   if request.user.is_authenticated:
    try:
     seller = Seller.objects.get(username=request.user,approved="Yes")
     earning = Earning.objects.get(seller_id=seller.seller_id)
     returns = Return.objects.filter(seller_id=seller.seller_id,status="Returned")
    except:
      return redirect('/')
    context = {
     'seller' : seller,
      'earning' : earning,
      'returns' : returns
    }
    return render(request,'seller-returns.html',context) 

def product_upload_page(request):
    if request.user.is_anonymous:
        return redirect('/')
    seller = Seller.objects.get(username=request.user,approved="Yes")
    sellerdetails = {
        'seller':seller,
    }    
    if seller is not None :
      return render(request,'product_upload.html',sellerdetails)
    else :
        return redirect('/')  

def uploadproduct(request):
    if request.method == "POST" :
        seller = request.POST.get('sellerid')
        brand = request.POST.get('brand')
        title = request.POST.get('title')
        sku = request.POST.get('sku')
        sp = request.POST.get('sp')
        mrp = request.POST.get('mrp')
        category = request.POST.get('category')
        subCategory = request.POST.get('sub-category')
        subSubCategory = request.POST.get('sub-sub-category')
        suitableForMen = request.POST.get('suitableformen')
        suitableForWomen = request.POST.get('suitableforwomen')
        suitableForKids = request.POST.get('suitableforkids')
        description = request.POST.get('description')
        featureName1 = request.POST.get('feature1-name')
        featureName2 = request.POST.get('feature2-name')
        featureName3 = request.POST.get('feature3-name')
        featureName4 = request.POST.get('feature4-name')
        featureName5 = request.POST.get('feature5-name')
        featureName6 = request.POST.get('feature6-name')
        feature1 = request.POST.get('feature1')
        feature2 = request.POST.get('feature2')
        feature3 = request.POST.get('feature3')
        feature4 = request.POST.get('feature4')
        feature5 = request.POST.get('feature5')
        feature6 = request.POST.get('feature6')
        size1 = request.POST.get('size[0]')
        size2 = request.POST.get('size[1]')
        size3 = request.POST.get('size[2]')
        size4 = request.POST.get('size[3]')
        size5 = request.POST.get('size[4]')
        size6 = request.POST.get('size[5]')
        size7 = request.POST.get('size[6]')
        size8 = request.POST.get('size[7]')
        size9 = request.POST.get('size[8]')
        size10 = request.POST.get('size[9]')
        color1 = request.POST.get('color[0]')
        color2 = request.POST.get('color[1]')
        color3 = request.POST.get('color[2]')
        color4 = request.POST.get('color[3]')
        color5 = request.POST.get('color[4]')
        color6 = request.POST.get('color[5]')
        color7 = request.POST.get('color[6]')
        color8 = request.POST.get('color[7]')
        color9 = request.POST.get('color[8]')
        color10 = request.POST.get('color[9]')
        image1 = request.FILES['img1']
        image2 = request.FILES['img2']
        image3 = request.FILES['img3']
        image4 = request.FILES['img4']
        image5 = request.FILES['img5']
        length = request.POST.get('length')
        breadth = request.POST.get('breadth')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        warranty = request.POST.get('warranty')
        cod = request.POST.get('cod')
        refund = request.POST.get('refund')
        off = 100*(int(mrp)-int(sp))/int(mrp)        
        stock = request.POST.get('stock')
        keywords = request.POST.get('keywords')
        if int(stock) < 0 :
             messages.error(request,"Stock cannot be less than 0")
             return redirect('/upload_product')
        Product.objects.create(seller=seller,brand=brand,title=title,sku=sku,sellingPrice=sp,
        mrp=mrp,category=category,subCategory=subCategory,subSubCategory=subSubCategory,
        suitableForMen=suitableForMen,suitableForWomen=suitableForWomen,suitableForKids=suitableForKids,description=description,featureName1=featureName1,featureName2=featureName2,
        featureName3=featureName3,featureName4=featureName4,featureName5=featureName5,featureName6=featureName6,
        feature1=feature1,feature2=feature2,feature3=feature3,feature4=feature4,feature5=feature5,feature6=feature6,
        size1=size1,size2=size2,size3=size3,size4=size4,size5=size5,size6=size6,size7=size7,size8=size8,size9=size9,size10=size10,
        color1=color1,color2=color2,color3=color3,color4=color4,color5=color5,color6=color6,color7=color7,color8=color8,color9=color9,color10=color10,image1=image1,image2=image2,image3=image3,image4=image4,image5=image5,length=length,breadth=breadth,
        height=height,weight=weight,warranty=warranty,cod=cod,refund=refund,off=off,stock=stock,keywords=keywords)      
        messages.success(request,"Product Added Successfully")
        return redirect('/seller_dashboard')
        
    return HttpResponse('404 - Not Found')

def productedit(request,pk):
    try :
        seller = Seller.objects.get(username=request.user)
        product = Product.objects.get(product_id=pk,seller=seller.seller_id,approved="Yes")
        productfetch = {
            'product' : product,
            'seller' : seller,
        }
        return render(request,'product-edit.html',productfetch)
    except ObjectDoesNotExist :
        return HttpResponse('Invalid request')    

def editproduct(request):
    if request.method == "POST" :
        product_id = request.POST.get('productid')
        title = request.POST.get('title')
        sp = request.POST.get('sp')
        mrp = request.POST.get('mrp')
        color1 = request.POST.get('color1')
        color2 = request.POST.get('color2')
        color3 = request.POST.get('color3')
        color4 = request.POST.get('color4')
        color5 = request.POST.get('color5')
        color6 = request.POST.get('color6')
        color7 = request.POST.get('color7')
        color8 = request.POST.get('color8')
        color9 = request.POST.get('color9')
        color10 = request.POST.get('color10')
        size1 = request.POST.get('size1')
        size2 = request.POST.get('size2')
        size3 = request.POST.get('size3')
        size4 = request.POST.get('size4')
        size5 = request.POST.get('size5')
        size6 = request.POST.get('size6')
        size7 = request.POST.get('size7')
        size8 = request.POST.get('size8')
        size9 = request.POST.get('size9')
        size10 = request.POST.get('size10')
        stock = request.POST.get('stock')
        Product.objects.filter(product_id=product_id,approved="Yes").update(title=title,sellingPrice=sp,
        mrp=mrp,color1=color1,color2=color2,color3=color3,color4=color4,color5=color5,color6=color6,color7=color7,color8=color8,color9=color9,color10=color10,
        size1=size1,size2=size2,size3=size3,size4=size4,size5=size5,size6=size6,size7=size7,size8=size8,size9=size9,size10=size10,
        stock=stock)
        messages.success(request,"Product Details Updated")
        return redirect('/seller_dashboard')

def deleteproduct(request):
    if request.method == "POST" :
        product_id = request.POST.get('productid')
        Product.objects.filter(product_id=product_id,approved="Yes").delete()
        messages.error(request,"Product Deleted Successfully")
        return redirect('/seller_dashboard')


def addstock(request,pk):
     if request.method == "POST" :
         stock = request.POST.get('stock')
         if int(stock) < 0 :
             messages.error(request,"Stock cannot be less than 0")
             return redirect('/seller_dashboard')
         Product.objects.filter(product_id=pk,approved="Yes").update(stock=stock)
         messages.success(request,"Stock Added Successfully")
         return redirect('/seller_dashboard')
     return HttpResponse('Invalid Request')     
         

def viewproduct(request,pk):
    product = Product.objects.get(product_id=pk,approved="Yes")
    yousave = int(product.mrp)-int(product.sellingPrice)
    try:
        rates = Rating.objects.filter(product_id=pk)
        ratingno = len(rates)
        reviews = Review.objects.filter(product_id=pk).order_by(Coalesce('date','product_id').desc())      
        reviewno = len(reviews)
        ratedbyuser = Rating.objects.get(product_id=pk,username=request.user)
        try:
            boughtProduct = len(SellerOrder.objects.filter(username=request.user,product_id=pk,orderStatus="Delivered"))
        except:
            boughtProduct = 0
        sumofrating = 0
        for i in rates:
            sumofrating += i.rating
        averagerating = sumofrating/len(rates)    
        productfetch = {
        'product' : product,
        'yousave' : yousave,
        'rates' : rates,
        'totalratings' : ratingno,
        'averagerating' : averagerating,
        'reviews' : reviews,
        'totalreviews' : reviewno,
        'ratedbyuser' : ratedbyuser,
        'boughtProduct' : boughtProduct

          }
        return render(request,'view-product.html',productfetch)
    except ObjectDoesNotExist:
         try:
            boughtProduct = len(SellerOrder.objects.filter(username=request.user,product_id=pk,orderStatus="Delivered"))
         except:
            boughtProduct = 0
         reviews = Review.objects.filter(product_id=pk).order_by(Coalesce('date','product_id').desc())       
         reviewno = len(reviews)
         rates = Rating.objects.filter(product_id=pk)
         ratingno = len(rates)
         if len(rates) > 0: 
           sumofratings = 0
           for i in rates:
            sumofratings += i.rating
           averageratings = sumofratings/len(rates)  
         else :
           averageratings = 0    
         productfetch = {
        'product' : product,
        'yousave' : yousave,
        'reviews' : reviews,
        'averagerating' : averageratings,
        'totalreviews' : reviewno,
        'totalratings' : ratingno,
        'boughtProduct' : boughtProduct
                  }
         return render(request,'view-product.html',productfetch)   
     

def ratenreview(request):
    if request.user.is_anonymous :
        return redirect('/')
    if request.method == "POST" :
        product_id = request.POST.get('productid')
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        Rating.objects.create(username=request.user,product_id=product_id,rating=rating,date=timezone.localtime(timezone.now()))
        if review != "" :
         try:
          profile = Customer.objects.get(username=request.user)
          Review.objects.create(username=request.user,product_id=product_id,review=review,rating=rating,gender=profile.gender,name=request.user.first_name+" "+request.user.last_name,date=timezone.localtime(timezone.now()))
         except:
          Review.objects.create(username=request.user,product_id=product_id,review=review,rating=rating,gender="Male",name=request.user.first_name+" "+request.user.last_name,date=timezone.localtime(timezone.now())) 
        rates = Rating.objects.filter(product_id=product_id)
        sumofratings = 0
        for i in rates:
            sumofratings += i.rating
            avgrating = sumofratings/len(rates) 
        avgrating = round(avgrating) 
        Product.objects.filter(product_id=product_id,approved="Yes").update(avgrating=avgrating,totalratings=len(rates))
        messages.success(request,"Thanks for rating this product")
        return redirect('/view_product/'+product_id)

def search(request):
    if request.method == "GET" :
        category = request.GET.get('category')
        query = request.GET.get('search')
        
        if query != "" and query != " ":
           if category == "All" :
            results = Product.objects.filter(approved="Yes").filter(Q(product_id__icontains=query)|Q(sku__icontains=query)|Q(brand__icontains=query)|
            Q(title__icontains=query)| Q(category__icontains=query)|
             Q(subCategory__icontains=query)| Q(subSubCategory__icontains=query)|
             Q(description__icontains=query)| Q(featureName1__icontains=query)|Q(featureName2__icontains=query)|
               Q(featureName3__icontains=query)|Q(featureName4__icontains=query)|
               Q(featureName5__icontains=query)|Q(keywords__icontains=query)).order_by(Coalesce('avgrating','totalratings').desc()) 
           else:
              results = Product.objects.filter(approved="Yes").filter(subCategory=category).filter(Q(product_id__icontains=query)|Q(sku__icontains=query)|Q(brand__icontains=query)|
            Q(title__icontains=query)| Q(category__icontains=query)|
             Q(subCategory__icontains=query)| Q(subSubCategory__icontains=query)|
             Q(description__icontains=query)| Q(featureName1__icontains=query)|Q(featureName2__icontains=query)|
               Q(featureName3__icontains=query)|Q(featureName4__icontains=query)|
               Q(featureName5__icontains=query)|Q(keywords__icontains=query)).order_by(Coalesce('avgrating','totalratings').desc()) 
           searchresults = {
                'results' : results,
                'query' : query,
                'category' : category
                       }   
           return render(request,'search.html',searchresults) 
           
        else:
            return render(request,'search.html')
    else:
        return HttpResponse('Invalid Request')       

def footwearsnapparels(request):
    query = "Footwears and Apparels"
    results = Product.objects.filter(approved="Yes").filter(Q(subCategory="Footwear")|Q(subSubCategory="Bags & Luggage")|Q(subSubCategory="Bags & Wallets")
    |Q(subCategory="Girls - Apparels")|Q(subCategory="Boys - Apparels")).order_by(Coalesce('avgrating','totalratings').desc()) 
      
    searchresults = {
                'results' : results,
                'query' : query,
                       }   
    return render(request,'search.html',searchresults) 

def fashionclothing(request):
    query = "Fashion Clothing"
    results = Product.objects.filter(approved="Yes").filter(Q(subCategory="Men Clothing")|Q(subCategory="Women Clothing")
    |Q(subCategory="Girls - Apparels")|Q(subCategory="Boys - Apparels")).order_by(Coalesce('avgrating','totalratings').desc()) 
      
    searchresults = {
                'results' : results,
                'query' : query,
                       }   
    return render(request,'search.html',searchresults) 

def marketplace(request):
    latesproducts = Product.objects.filter(approved="Yes").order_by(Coalesce('product_id','avgrating').desc())  
    bestproducts = Product.objects.filter(approved="Yes").order_by(Coalesce('avgrating','totalratings').desc())  
    menproducts = Product.objects.filter(category="Men's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())    
    womenproducts = Product.objects.filter(category="Women's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())     
    kidsproducts = Product.objects.filter(category="Kid's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())        
    sportsproducts = Product.objects.filter(approved="Yes").filter(Q(subSubCategory="Sports Shoes")|Q(subSubCategory="T-Shirts")|Q(subSubCategory="Sneakers Shoes")|Q(subSubCategory="T-Shirts and Tank tops")).order_by(Coalesce('avgrating','product_id').desc())
    formalproducts = Product.objects.filter(approved="Yes").filter(Q(subSubCategory="Formal Shoes")|Q(subSubCategory="Formal Shirts")|Q(subSubCategory="Formal Trouser")|Q(subSubCategory="Suitings and Shirtings")).order_by(Coalesce('avgrating','product_id').desc())
    productfetch = {
        'latestproducts' : latesproducts,
        'bestproducts' : bestproducts,
        'menproducts' : menproducts,
        'womenproducts' : womenproducts,
        'kidsproducts' : kidsproducts,
        'sportsproducts' : sportsproducts,
        'formalproducts' : formalproducts,
    }            
    return render(request,'marketplace.html',productfetch)

def sportscollection(request):
    sportshoesmen = Product.objects.filter(subSubCategory="Sports Shoes",category="Men's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())    
    sportshoeswomen = Product.objects.filter(subSubCategory="Sports Shoes",category="Women's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc()) 
    sportsfashion = Product.objects.filter(approved="Yes").filter(Q(subSubCategory="T-Shirts")|Q(subSubCategory="T-Shirts and Tank tops")|Q(subSubCategory="Sneakers Shoes")).order_by(Coalesce('avgrating','product_id').desc())     
    
 
    productfetch = {
       'sportshoesmen' : sportshoesmen,
        'sportshoeswomen' : sportshoeswomen,
        'sportsfashion' : sportsfashion,
    }
    return render(request,'marketplace.html',productfetch)

def formalcollection(request):
  formalshoesmen = Product.objects.filter(subSubCategory="Formal Shoes",category="Men's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())   
  formalsuits = Product.objects.filter(subSubCategory="Suitings and Shirtings",category="Men's Fashion",approved="Yes").order_by(Coalesce('avgrating','product_id').desc())  
  formalfashion = Product.objects.filter(subCategory="Men Clothing",approved="Yes").filter(Q(subSubCategory="Formal Trouser")|Q(subSubCategory="Formal Shirts")).order_by(Coalesce('avgrating','product_id').desc()) 


  productfetch = {
      'formalshoesmen' : formalshoesmen,
      'formalsuits' : formalsuits,
      'formalfashion' : formalfashion,
  } 
  return render(request,'marketplace.html',productfetch)

def womencollection(request):
    womenshoes = Product.objects.filter(category="Women's Fashion",subCategory="Footwear",approved="Yes").order_by(Coalesce('avgrating','product_id').desc()) 
    womenbags = Product.objects.filter(category="Women's Fashion",subCategory="Bags and Wallets",approved="Yes").order_by(Coalesce('avgrating','product_id').desc()) 
    womenfashion =  Product.objects.filter(category="Women's Fashion",subCategory="Women Clothing",approved="Yes").order_by(Coalesce('avgrating','product_id').desc()) 
    
    productfetch = {
        'womenshoes' : womenshoes,
        'womenbags': womenbags,
        'womenfashion' : womenfashion
    }
    return render(request,'marketplace.html',productfetch)

def checkout(request):
    if request.method == 'POST':
        username = request.user
        items = request.POST.get('items')
        totalPrice = request.POST.get('total')   
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        alternatePhone = request.POST.get('alphone')
        addressline1 = request.POST.get('address-line-1')
        addressline2 = request.POST.get('address-line-2')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        date = datetime.date.today()
        payment = request.POST.get('payment')
        domain = get_current_site(request).domain
        if payment != "COD" : 
          api = Instamojo(api_key='bd12aeaa8b5b32642ed0fa5028d0ebda',auth_token=              '2b7fab639aaaafb72a9e96b89f3ed588')
          response = api.payment_request_create(
            amount=totalPrice,
            purpose='Trikada Item',
            send_email=True,
            email=email,
            redirect_url= 'https://'+domain+'/checkout_done'
            )
          url = response['payment_request']['longurl']
          paymentRequestId = response['payment_request']['id']
          Order.objects.create(username=username,name=name,itemsjson=items,totalPrice=totalPrice,
          email=email,phone=phone,alternatePhone=alternatePhone,addressline1=addressline1,
          addressline2=addressline2,landmark=landmark,city=city,pincode=pincode,state=state,date=date,
          statusjson= json.dumps({ "Ordered" : str(date)}),paymentRequestId=paymentRequestId)
          return redirect(url)
        else:
           Order.objects.create(username=username,name=name,itemsjson=items,totalPrice=totalPrice,
           email=email,phone=phone,alternatePhone=alternatePhone,addressline1=addressline1,
           addressline2=addressline2,landmark=landmark,city=city,pincode=pincode,state=state,date=date,
           statusjson= json.dumps({ "Ordered" : str(date)}),payment_status="COD")
           messages.success(request,"Thanks for your order!")
           return redirect('/my_orders')   
    try: 
     customer = Customer.objects.get(username=request.user)
     makingorder = {
         'customer' : customer,
           }
     return render(request,'checkout.html',makingorder)    
    except ObjectDoesNotExist:
        return render(request,'checkout.html') 
def checkoutdone(request):
   try: 
    api = Instamojo(api_key='bd12aeaa8b5b32642ed0fa5028d0ebda',auth_token=              '2b7fab639aaaafb72a9e96b89f3ed588')
    paymentId = request.GET.get('payment_id','')
    paymentRId = request.GET.get('payment_request_id','')
    response = api.payment_request_payment_status(paymentRId, paymentId)
    payment_status =  response['payment_request']['payment']['status'] 
    if payment_status == "Credit":
        Order.objects.filter(paymentRequestId=paymentRId).update(payment_status=payment_status)
        messages.success(request,"Thanks for your order!")
        return redirect('/my_orders')
    else:
       Order.objects.filter(paymentRequestId=paymentRId).update(payment_status=payment_status) 
       messages.error(request,'Payment Failed') 
       return redirect('/my_orders')   
   except:
       return HttpResponse('Invalid Request')    
   
def myorders(request):
    if request.user.is_anonymous:
        return redirect('/')
    if request.method == "POST" :
        order_id = request.POST.get('orderid')
        delivered = request.POST.get('delivered')
        Order.objects.filter(order_id=order_id).update(status=delivered)
        order = Order.objects.get(order_id=order_id)
        statusJSON = json.loads(order.statusjson)
        date = datetime.date.today()
        data = { delivered : str(date)}
        statusJSON.update(data)
        statusJSONupdate = json.dumps(statusJSON)
        Order.objects.filter(order_id=order_id).update(status=delivered,statusjson=statusJSONupdate)
        messages.success(request,"Order Delivered Updated")
        return redirect('/my_orders') 
    orders = Order.objects.filter(username=request.user).order_by(Coalesce('order_id','date').desc()) 
    return render(request,'my-orders.html',{'orders':orders})

def ordertracker(request,pk):
    if request.user.is_anonymous :
              return redirect('/')
    order = Order.objects.get(order_id=pk)
    orderUpdate = Order.objects.get(order_id=pk)
    statusUpdate = json.loads(orderUpdate.statusjson)
    products = json.loads(order.itemsjson)
    myorders = {
        'order' : order,
        'orderUpdate' : orderUpdate,
        'statusUpdate' : statusUpdate,
        'products' : products,
    }          
    return render(request,'order-tracker.html',myorders)    

def orderreturn(request,pk):
    if request.user.is_authenticated:
        productid = pk
        if request.method == "POST" :
            order_id = request.POST.get('orderid')
            product_id = request.POST.get('productid')
            reason = request.POST.get('reason')
            quantity = request.POST.get('qty')
            bankName = request.POST.get('bank-name')
            acno = request.POST.get('acno')
            ifsc = request.POST.get('ifsc')
            try:
             returnExists  = Return.objects.get(fromOrderId=order_id,product_id=product_id,username=request.user)
            except:
                returnExists = None
            if returnExists is not None :
             messages.error(request,"Return Request Already Sent!")
             return redirect('/my_orders')
            try:
              order = Order.objects.get(order_id=order_id,username=request.user)
              if order is not None :
                   sellerOrder = SellerOrder.objects.get(fromOrderId=order_id,product_id=product_id)
                   if sellerOrder is not None :
                       date = timezone.localtime(timezone.now())
                       totalAmount = int(sellerOrder.price)*int(quantity)
                       Return.objects.create(seller_order_id=sellerOrder.seller_order_id,
                       product_id=product_id,date=date,fromOrderId=order_id,reason=reason,username=request.user,quantity=quantity,totalAmount=totalAmount,
                       bankName=bankName,acno=acno,ifsc=ifsc,seller_id=sellerOrder.seller_id)
                       messages.success(request,"Return Request Sent Successfully!")
                       return redirect('/my_orders')
                   else:
                       messages.error(request,"Cannot Find Seller of this Product!")  
                       return redirect('/my_order')   
              else:
                   messages.error(request,"Cannot find any order with this account!")        
                   return redirect('/my_orders') 
            except:
              messages.error(request,"Cannot find any order with this account!")
              return redirect('/my_orders')
        context = {
            'productid' : productid,
            }
        return render(request,'return.html',context)
    else:
        return HttpResponse('Invalid Request')    

def myreturns(request):
    if request.user.is_authenticated:
        try:
         returns = Return.objects.filter(username=request.user).order_by(Coalesce('return_id','date').desc()) 
        except:
          returns = None
        context = {
            'returns' : returns
        }                    
        return render(request,'my-returns.html',context)
    else:
        return HttpResponse('Invalid Request')    

def cancelreturn(request,pk):
    if request.user.is_authenticated:
       try:
          Return.objects.filter(return_id=pk,username=request.user).delete()
          messages.success(request,"Return Request Cancelled!")
          return redirect('/my_returns')
       except:
           messages.error(request,"Request Not Found!")
           return redirect('/my_returns')   
    else:
        return HttpResponse('Invalid Request')

#Admin Control 
def admincontrol(request):
    if request.user.is_superuser:
        unclearedOrders = Order.objects.filter(cleared="No")
        sellers = Seller.objects.all()
        totalSellers = Seller.objects.filter(approved="Yes")
        undeliveredOrders = SellerOrder.objects.filter(orderStatus="Picked")
        returns = Return.objects.filter(status="Pending")
        sellerRequests = Seller.objects.filter(approved="No")
        if request.method == "GET":
            query1 = request.GET.get('search')
            query2 = request.GET.get('search-order')
            if query1 is not None : 
              order = None
              totalItems = None
              packedOrders = SellerOrder.objects.filter(orderStatus="Packed").filter(Q(fromOrderId__icontains=query1)).order_by(Coalesce('seller_order_id','date').desc())
            elif query2 is not None:
                try:
                 order = Order.objects.get(Q(order_id__iexact=query2))
                 totalItems = len(json.loads(order.itemsjson))
                except:
                 order = None
                 totalItems = None
                packedOrders = SellerOrder.objects.filter(orderStatus="Packed").order_by(Coalesce('seller_order_id','date').desc())
            else:
              packedOrders = SellerOrder.objects.filter(orderStatus="Packed").order_by(Coalesce('seller_order_id','date').desc())
              order = None
              totalItems = None
        else:
            order = None
            totalItems = None
            packedOrders = SellerOrder.objects.filter(orderStatus="Packed").order_by(Coalesce('seller_order_id','date').desc())
        
        adminpage ={
            'unclearedOrders' : len(unclearedOrders),
            'packedOrders' : packedOrders,
            'noOfPackedOrders' : len(packedOrders),
            'sellers' : sellers,
            'order' : order,
            'totalItems' : totalItems,
            'undeliveredOrders' : len(undeliveredOrders),
            'returns' : len(returns),
            'totalSellers' : len(totalSellers),
            'sellerRequest' : len(sellerRequests),
           }
        return render(request,'admin-page.html',adminpage)
    else :
        return HttpResponse('Invalid Request')     

def clearorder(request):
    if request.user.is_superuser:
        # try:
            unclearedOrders = Order.objects.filter(cleared="No")
            for i in unclearedOrders:
                orderItems = json.loads(i.itemsjson)
                addressline1 = i.addressline1
                addressline2 = i.addressline2
                userName = i.username
                city = i.city
                state = i.state
                pincode = i.pincode
                for x, y in orderItems.items() :
                   product = Product.objects.get(product_id=x)
                   seller = Seller.objects.get(seller_id=product.seller)
                   productid = x
                   sku = product.sku
                   productName = product.title
                   price = product.sellingPrice
                   qty = y[0]
                   size = y[5]
                   color = y[6]
                   totalAmount = int(price)*int(qty)
                   date = timezone.localtime(timezone.now())
                   fromOrderId = i.order_id
                   SellerOrder.objects.create(username=userName,seller_id=seller.seller_id,product_id=productid,sku=sku,productName=productName,
                   price=price,totalAmount=totalAmount,qty=qty,size=size,color=color,date=date,fromOrderId=fromOrderId,addressline1=addressline1,
                   addressline2=addressline2,city=city,state=state,pincode=pincode)
                Order.objects.filter(order_id=i.order_id).update(cleared="Yes")       
            messages.success(request,"All Orders Sent to the Sellers.")  
            return redirect('/admin_control_panel_trikada')      
        # except :
            # return redirect('/admin_control_panel_trikada')    
    else :
        return HttpResponse('Invalid Request') 

def pickedorder(request):
  if request.user.is_superuser:  
    if request.method == "POST" :
        seller_order_id = request.POST.get('sellerorderid')
        picked = request.POST.get('picked')
        SellerOrder.objects.filter(seller_order_id=seller_order_id).update(orderStatus=picked)
        messages.success(request,"Item Picked Updated")
        return redirect('/admin_control_panel_trikada')
    else:
        return HttpResponse('Invalid Request')    
  else:
      return HttpResponse('Invalid Request')
def adminorderpacked(request):
    if request.user.is_superuser:
        if request.method == "POST" :
            order_id = request.POST.get('orderid')
            status = request.POST.get('orderStatus')
            order = Order.objects.get(order_id=order_id)
            statusJSON = json.loads(order.statusjson)
            date = datetime.date.today()
            data = { status : str(date)}
            statusJSON.update(data)
            statusJSONupdate = json.dumps(statusJSON)
            Order.objects.filter(order_id=order_id).update(status=status,statusjson=statusJSONupdate)
            messages.success(request,'Order Status Updated')
            return redirect('/admin_control_panel_trikada') 

def adminupdatedelivered(request):
    if request.user.is_superuser:
        sellerOrders = SellerOrder.objects.filter(orderStatus="Picked").order_by(Coalesce('seller_order_id','date').desc())
        sellers = Seller.objects.all()
        order = None
        totalItems = None
        if request.method == "POST" :
            seller_order_id = request.POST.get('sellerorderid')
            delivered = request.POST.get('delivered')
            seller = SellerOrder.objects.get(seller_order_id=seller_order_id)
            SellerOrder.objects.filter(seller_order_id=seller_order_id).update(orderStatus=delivered)
            earning = Earning.objects.get(seller_id=seller.seller_id)
            Amount = int(seller.totalAmount) * 80/100
            addingAmount = int(earning.totalEarning) + Amount
            Earning.objects.filter(seller_id=seller.seller_id).update(totalEarning=addingAmount)
            messages.success(request,"Update Sent to the Seller !")
        if request.method == "GET" :
            query1 = request.GET.get('search-undelivered')
            query2 = request.GET.get('search-orders')
            if query1 is not None :
              sellerOrders = SellerOrder.objects.filter(orderStatus="Picked").filter(Q(fromOrderId__iexact=query1)).order_by(Coalesce('seller_order_id','date').desc())
              order = None 
            elif query2 is not None :
              try:
                 order = Order.objects.get(Q(order_id__iexact=query2))
                 totalItems = len(json.loads(order.itemsjson))
              except:
                 order = None
                 totalItems = None  
            else:
               order = None
               totalItems = None
        statuspage = {
          'sellerOrders' : sellerOrders,
          'sellers' : sellers,
          'order' : order,
          'totalItems' : totalItems
         }
        return render(request,'update-delivered.html',statuspage) 
    else:
        return HttpResponse('Invalid Request')   

def adminreturns(request):
  if request.user.is_superuser :  
    if request.method == "POST" :
        return_id = request.POST.get('returnid')  
        status = request.POST.get('status')
        Return.objects.filter(return_id=return_id).update(status=status)
        if status == "Returned" :
            theReturn = Return.objects.get(return_id=return_id)
            sellerOrder = SellerOrder.objects.get(seller_order_id=theReturn.seller_order_id)
            SellerOrder.objects.filter(seller_order_id=theReturn.seller_order_id).update(orderStatus=status)
            earns = Earning.objects.get(seller_id=sellerOrder.seller_id)
            addAmount = int(earns.totalEarning) - int(theReturn.totalAmount)
            addingAmount = addAmount
            Earning.objects.filter(seller_id=sellerOrder.seller_id).update(totalEarning=addingAmount)
        messages.success(request,"Status Updated")
        return redirect('/admin_returns')    
    returns = Return.objects.all().order_by(Coalesce('return_id','date').desc())
    if request.method == "GET" :
        query = request.GET.get('search')
        if query != "":
          try:
           returns = Return.objects.filter(Q(status__icontains=query)|
            Q(return_id__iexact=query)|Q(fromOrderId__iexact=query)).order_by(Coalesce('return_id','date').desc())
          except:
              pass
        else:
             returns = Return.objects.all().order_by(Coalesce('return_id','date').desc())
    context = {
        'returns' : returns,
    }
    return render(request,'admin-returns.html',context)
  else:
      return HttpResponse('Invalid Request')  

def approvesellers(request):
   if request.user.is_superuser:
     if request.method == "POST":
         approved = request.POST.get('approve')
         seller_id = request.POST.get('sellerid')
         seller_id = seller_id
         Seller.objects.filter(seller_id=seller_id).update(approved=approved)
         Earning.objects.create(seller_id=seller_id,date=datetime.date.today())
         messages.success(request,'Account approved!')
         return redirect('/approve_sellers')
     sellers = Seller.objects.filter(approved="No")
     context = {
        'sellers' : sellers
     }
     return render(request,'approve_sellers.html',context)
   else:
       return HttpResponse('Invalid Request') 

def payments(request):
   if request.user.is_superuser:
      payments = Earning.objects.all()
      if request.method == "POST" :
          seller_id = request.POST.get('sellerid')
          paid = request.POST.get('paid')
          if paid == "paid" :
              earns = Earning.objects.get(seller_id=seller_id)
              date = timezone.localtime(timezone.now())
              Earning.objects.filter(seller_id=seller_id).update(totalEarning=0,lastEarning=earns.totalEarning,lastPaymentDate=date)
              messages.success(request,'Seller paid!')
              return redirect('/clear_payments')
      if request.method == "GET":
          query = request.GET.get('search')
          sellers = Seller.objects.filter(Q(seller_id__iexact=query)|
          Q(brandName__iexact=query))
      else:
          sellers = None
      context = {
          'payments' : payments,
          'sellers' : sellers
          }  
      return render(request,'clear-payments.html',context)
   else:
       return HttpResponse('Invalid Request')   

def confirmproduct(request):
    if request.user.is_superuser:
        products = Product.objects.filter(approved="No")   
        if request.method == "POST":
            query = request.POST.get('search')
            if query is not None :
             try:
              products = Product.objects.filter(product_id=query)
             except:
              products = Product.objects.filter(approved="No")
            else:
             product_id = request.POST.get('productid')
             approved = request.POST.get('approved')
             Product.objects.filter(product_id=product_id).update(approved=approved)
             messages.success(request,"Product approved!")
             return redirect('/confirm_product')
            
        productdisplay = {
            'products' : products
        }
        return render(request,'confirm-products.html',productdisplay)
    else:
        return HttpResponse('Invalid Request')   
        
def feedback(request):
    if request.method == "POST" :
        username = request.user
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('msg')
        Feedback.objects.create(username=username,name=name,email=email,message=message)
        messages.success(request,'Thanks for your feedback')
        return redirect('/')
    else:
        return redirect('/')    