from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import Product, BlogPost, Comment, User, CartItem, Coupon, Feedback, Partner, Favorite, YourAddress

admin.site.register(Partner)
admin.site.register(Product)
admin.site.register(BlogPost)
admin.site.register(Comment)
admin.site.register(User,UserAdmin)
admin.site.register(Coupon)
admin.site.register(CartItem)
admin.site.register(Feedback)
admin.site.register(Favorite)
admin.site.register(YourAddress)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstname', 'email', 'phonenumber', 'profile_image')
