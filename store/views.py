from django.shortcuts import render, redirect
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.templatetags.static import static
from .forms import EditProfileForm
from decimal import Decimal
from django.http import JsonResponse
from .utils import make_momo_payment
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

from .forms import YourAddressForm
from .models import YourAddress
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, BlogPost, Comment,User, CartItem, Coupon, Partner, Favorite
from django.core.files.storage import FileSystemStorage
from .models import Feedback
from .forms import FeedbackForm
from .utils import analyze_sentiment
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.sentiment = analyze_sentiment(instance.feedback)
            instance.save()
            return redirect('feedback')  # Name of your feedback URL
    else:
        form = FeedbackForm()

    sentiment_filter = request.GET.get('sentiment')
    if sentiment_filter:
        feedbacks = Feedback.objects.filter(sentiment=sentiment_filter)
    else:
        feedbacks = Feedback.objects.all()

    return render(request, 'store/feedback.html', {'form': form, 'feedbacks': feedbacks})
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def blog_list(request):
    blogs = BlogPost.objects.all()
    return render(request, 'store/blog_list.html', {'blogs': blogs})


def register(request):
    if request.method == 'POST':
        username = request.POST['Surname']
        firstname = request.POST['Firstname']
        email = request.POST['email']
        phone = request.POST['telephone']
        password = request.POST['password']
        profile_image = request.FILES.get('profile_image')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already used.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname
        user.phonenumber = phone
        user.profile_image = profile_image
        user.save()

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'store/register.html')

@login_required(login_url='login')
def catalog(request):
    return render(request,'store/catalog.html')
@login_required(login_url='login')
def catalog_view(request, category=None):
    if category:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'store/catalog.html', {'products': products})

@login_required(login_url='login')
def blog_detail(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    comments = blog.comments.all()  # Related name 'comments'

    if request.method == 'POST':
        text = request.POST['text']
        Comment.objects.create(
            blog=blog,
            author=request.user.username,  # Automatically use logged-in user's username
            text=text
        )
        return redirect('blog_detail', pk=blog.pk)

    return render(request, 'store/blog_detail.html', {'blog': blog, 'comments': comments})

@login_required(login_url='login')
def your_address_view(request):
    try:
        address = request.user.address
        form = YourAddressForm(instance=address)
    except YourAddress.DoesNotExist:
        form = YourAddressForm()

    if request.method == 'POST':
        if 'address' in locals():
            form = YourAddressForm(request.POST, instance=address)
        else:
            form = YourAddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('home')  # or wherever you want to redirect after saving

    return render(request, 'store/your_address.html', {'form': form})

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

@login_required(login_url='login')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    products = []
    total = 0
    applied_discount = 0
    coupon_message = ""

    for item in cart_items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        products.append({
            'product': item.product,
            'quantity': item.quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        if 'checkout' in request.POST:
            phone_number = request.POST.get('phone_number')
            try:
                reference_id = make_momo_payment(total, phone_number)
                messages.success(request, f"Payment prompt sent to {phone_number}. Ref: {reference_id}")
                return redirect('cart')
            except Exception as e:
                messages.error(request, f"Payment failed: {e}")
        
        elif 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('promocode', '').strip()
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                    applied_discount = (Decimal(coupon.discount_percentage) / Decimal('100')) * Decimal(total)
                    total -= applied_discount
                    coupon_message = f"Coupon '{coupon.code}' applied: {coupon.discount_percentage}% off!"
                except Coupon.DoesNotExist:
                    coupon_message = "Invalid or expired coupon code."

    context = {
        'products': products,
        'total': round(total, 2),
        'discount': round(applied_discount, 2),
        'coupon_message': coupon_message
    }
    return render(request, 'store/cart.html', context)


def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return redirect('cart')

@csrf_exempt
def momo_callback(request):
    data = json.loads(request.body)
    # You can log it or handle post-payment confirmation
    return JsonResponse({"status": "received"})

def remove_from_cart(request, product_id):
    CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cart')

def download_pdf(request):
    products = Product.objects.all()
    template_path = 'store/catalog_pdf.html'
    context = {'products': products}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="catalog.pdf"'
    
    # Get the template and render it
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF and attach to response
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Check for errors during the PDF creation
    if pisa_status.err:
        return HttpResponse('We had some errors while generating your PDF.', status=500)

    return response

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'store/login.html')  # Render the login page

def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

def catalog_by_category(request, category_name):
    products = Product.objects.filter(category=category_name)
    men_products = Product.objects.filter(category='Men')
    women_products = Product.objects.filter(category='Women')
    kids_products = Product.objects.filter(category='Kids')
    summer_products = Product.objects.filter(category='Summer')
    winter_products = Product.objects.filter(category='Winter')

    return render(request, 'store/catalog_by_category.html', {
        'products': products,
        'category_name': category_name,
        'men_products': men_products,
        'women_products': women_products,
        'kids_products': kids_products,
        'summer_products': summer_products,
        'winter_products': winter_products
    })

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'store/profile.html', {'user': user})

def partners_page(request):
    partners = Partner.objects.all()
    return render(request, 'store/partners.html', {'partners': partners})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')

            if password and password != '':
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in after password change
            else:
                user.save()
                
            return redirect('user_profile')
        else:
            print(form.errors)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'store/edit_profile.html', {'form': form})
def momo_payment_request(request):
    if request.method == 'POST':
        # Simulate capturing total from session/cart (you can adapt this to use your real total)
        total = request.POST.get('amount')  # get amount from hidden input or session
        phone_number = request.POST.get('phone')  # user’s phone number

        # You'd normally generate the request using MTN's API here
        # For now, simulate success
        return JsonResponse({'status': 'success', 'message': 'Payment request sent'})

    return JsonResponse({'status': 'fail', 'message': 'Invalid request'})

def partners_view(request):
    partners = [
        {"name": "Balenciaga", "logo": "balenciaga.png", "description": "Partnered in sustainable fashion innovation."},
        {"name": "Dior", "logo": "dior.png", "description": "Our luxury fashion & beauty partner."},
        {"name": "MTN Rwanda", "logo": "mtn.png", "description": "Mobile payments and digital connectivity partner."},
        {"name": "Versace", "logo": "versace.png", "description": "Co-creating elegant fashion experiences."},
        {"name": "PayPal", "logo": "paypal.png", "description": "Trusted payment processing partner."},
        {"name": "BK Rwanda", "logo": "bk.png", "description": "Banking partner supporting secure transactions."},
    ]
    return render(request, 'store/partners.html', {'partners': partners})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return redirect('home')

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'store/favorites.html', {'favorites': favorites})

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = list(Product.objects.filter(name__icontains=query).values_list('name', flat=True)[:10])
    return JsonResponse({'results': suggestions})

def search_products(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(name__icontains=query)

    context = {
        'products': results,
        'category_name': f"Search Results for '{query}'" if query else "All Products"
    }
    return render(request, 'store/catalog.html', context)

def autocomplete_products(request):
    query = request.GET.get('term', '')
    results = []

    if query:
        products = Product.objects.filter(name__icontains=query)[:5]
        results = [product.name for product in products]

    return JsonResponse(results, safe=False)