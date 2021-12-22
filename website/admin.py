from django.contrib import admin
from website.models import Customer, Product, Seller, Rating, Review, Order, SellerOrder, Return, Feedback, Earning

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Seller)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(SellerOrder)
admin.site.register(Return)
admin.site.register(Earning)
admin.site.register(Feedback)