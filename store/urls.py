from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('register/',views.register, name='register'),
    path('catalog/',views.catalog,name='catalog'),
    path('download-catalog/', views.download_pdf, name='download_pdf'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('catalog/<str:category>/', views.catalog_view, name='catalog_by_category'),
    path('catalog/download/pdf/', views.download_pdf, name='catalog_pdf'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('momo-payment/', views.momo_payment_request, name='momo_payment'),
    path('momo-callback/', views.momo_callback, name='momo_callback'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('partners/', views.partners_page, name='partners'),
    path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('your-address/', views.your_address_view, name='your_address'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('search/', views.search_products, name='search_products'),
    path('autocomplete/', views.autocomplete_products, name='autocomplete_products'),
]

@csrf_exempt
def momo_callback(request):
    data = json.loads(request.body)
    # You can log it or handle post-payment confirmation here
    return JsonResponse({"status": "received"})

