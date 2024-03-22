import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from .forms import CustomUserCreationForm, LoginForm, ForgotPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.views.decorators.cache import never_cache
from adminproductmanagement.models import (
    Brand,
    Product,
    Category,
    ProductVariant,
    CategoryOffer,
)
from adminshome.models import Banner
from userproduct.models import Cart, CartItem
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import TemplateView

# Create your views here.


@never_cache
def home(request):
    banners = Banner.objects.all()
    categories = Category.objects.filter(is_listed=True)
    brands = Brand.objects.filter(is_listed=True)
    latest_products = []

    for brand in brands:
        latest_product = (
            Product.objects.filter(
                brand=brand,
                is_listed=True,
                category__is_listed=True,
                brand__is_listed=True,
            )
            .order_by("-id")
            .first()
        )
        if latest_product:
            latest_products.append(latest_product)

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
    else:
        cart = None
        cart_items = None

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "categories": categories,
        "brands": brands,
        "products": latest_products,
        "banners": banners,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }

    return render(request, "usershome/home.html", context)


@never_cache
def signin(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome {user.username}!")
                return redirect("home")
            else:
                messages.error(
                    request, "Invalid Username or Password. Please try again."
                )
        else:
            messages.error(request, "Please try again.")

    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "usershome/signin.html", {"login_form": login_form})


@never_cache
def signup(request):
    if not request.user.is_authenticated:
        form = CustomUserCreationForm()
        if request.method == "POST":
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                request.session["user_data"] = form.cleaned_data
                email = form.cleaned_data["email"]
                if email:
                    try:
                        request.session["email"] = email
                        first_name = form.cleaned_data.get("first_name")
                        otp = str(random.randint(100000, 999999))
                        request.session["otp"] = otp
                        htmly = get_template("usershome/email.html")
                        subject, from_email, to = (
                            "Welcome",
                            "hamrazhakeem100@gmail.com",
                            email,
                        )
                        html_content = htmly.render(
                            {"otp": otp, "first_name": first_name}
                        )
                        msg = EmailMultiAlternatives(
                            subject, html_content, from_email, [to]
                        )
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        messages.success(request, "An OTP has been Sent to Your Email")
                        return redirect("verify_otp")
                    except:
                        messages.error(request, "Otp sending failed.")
                        return redirect("signup")
        return render(request, "usershome/signup.html", {"form": form})
    else:
        return redirect("home")


@never_cache
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")

        if entered_otp == stored_otp:
            user_data = request.session["user_data"]

            if user_data:
                new_user = CustomUser.objects.create_user(
                    email=user_data.get("email"),
                    username=user_data.get("username"),
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                )

                new_user.set_password(user_data.get("password1"))
                new_user.save()
                messages.success(request, "Account Created Successfully")
                return redirect("signin")
            else:
                messages.error(request, "Request failed. Please try again.")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("verify_otp")

    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "usershome/otp.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")


def shop(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    products = Product.objects.filter(
        is_listed=True, category__is_listed=True, brand__is_listed=True
    )

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    search_query = request.GET.get("q")
    search_type = request.GET.get("type")

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(brand__name__icontains=search_query)
            | Q(type__icontains=search_query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")

    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    variants = ProductVariant.objects.all()
    colors = set([variant.color for variant in variants])

    offers = CategoryOffer.objects.filter(
        status="Active", valid_from__lte=timezone.now(), valid_to__gte=timezone.now()
    )

    context = {
        "products": paginated_products,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
        "categories": Category.objects.filter(is_listed=True),
        "brands": Brand.objects.filter(is_listed=True),
        "variants": colors,
        "offers": offers,
    }
    return render(request, "usershome/shop.html", context)


class about_us(TemplateView):
    template_name = "usershome/about_us.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = None
        cart_items = None
        cart_count = 0

        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user).first()
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = cart_items.count()

        context["banner"] = Banner.objects.all().first()
        context["cart"] = cart
        context["cart_count"] = cart_count
        context["cart_items"] = cart_items
        return context


def filter_products(request):
    categories = request.GET.getlist("category[]")
    productvariants = request.GET.getlist("variant[]")
    brands = request.GET.getlist("brand[]")

    products = Product.objects.filter(is_listed=True).distinct()

    if categories:
        products = products.filter(category__id__in=categories).distinct()

    if productvariants:
        products = products.filter(productvariant__color__in=productvariants).distinct()

    if brands:
        products = products.filter(brand__id__in=brands).distinct()

    offers = CategoryOffer.objects.filter(
        status="Active", valid_from__lte=timezone.now(), valid_to__gte=timezone.now()
    )

    data = render_to_string(
        "usershome/filtered_products.html", {"products": products, "offers": offers}
    )

    return JsonResponse({"data": data})


@never_cache
def forgot_password(request):
    if request.method == "POST":
        entered_email = request.POST.get("email")
        email = CustomUser.objects.filter(email=entered_email).exists()
        if email:
            try:
                user = CustomUser.objects.get(email=entered_email)
                first_name = user.first_name
                request.session["email"] = entered_email
                otp = str(random.randint(100000, 999999))
                request.session["otp"] = otp
                htmly = get_template("usershome/forgot_password_email.html")
                subject, from_email, to = (
                    "Reset Password",
                    "hamrazhakeem100@gmail.com",
                    entered_email,
                )
                html_content = htmly.render({"otp": otp, "first_name": first_name})
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                messages.success(request, "An OTP has been Sent to Your Email")
                return redirect("forgot_password_verify_otp")
            except Exception as e:
                messages.error(request, "OTP Sending Failed")
                return redirect("forgot_password")
        else:
            messages.error(request, "Please enter a valid Email")
    return render(request, "usershome/forgot_password.html")


@never_cache
def forgot_password_verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")

        if entered_otp == stored_otp:
            messages.success(request, "OTP Verified")
            return redirect("forgot_change_password")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("forgot_password_verify_otp")

    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "usershome/forgot_password_verify_otp.html")


@never_cache
def forgot_change_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            entered_email = request.session.get("email")
            if entered_email:
                try:
                    user = CustomUser.objects.get(email=entered_email)
                    password1 = form.cleaned_data["password"]
                    user.set_password(password1)
                    user.save()
                    messages.success(request, "Password Reset Successful")
                    return redirect("signin")
                except CustomUser.DoesNotExist:
                    messages.error(request, "User not found")
            else:
                messages.error(request, "Email not found in session")
        else:
            messages.error(request, "Form is not valid")
    else:
        form = ForgotPasswordForm()
    return render(request, "usershome/forgot_change_password.html", {"form": form})


def del_info(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}
    return render(request, "usershome/del_info.html", context)


def privacy_policy(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}
    return render(request, "usershome/privacy_policy.html", context)


def terms_and_conditions(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}
    return render(request, "usershome/terms_and_conditions.html", context)


def customer_service(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}
    return render(request, "usershome/customer_service.html", context)


def contact_us(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    else:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}
    return render(request, "usershome/contact_us.html", context)
