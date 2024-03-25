from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from usershome.models import CustomUser
from .models import Address, Wallet, WalletTransactions
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm, AddAddressForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.cache import never_cache
from userproduct.models import CartItem, Cart
from user_order_and_payment.models import Order, OrderItems
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from adminproductmanagement.models import Coupons, ProductVariant
from django.db.models import Q
import os
from dotenv import load_dotenv
load_dotenv()

# Create your views here.


@never_cache
@login_required(login_url="signin")
def profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "user": user,
        "cart_items": cart_items,
        "cart": cart,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/profile.html", context)


@never_cache
@login_required(login_url="signin")
def edit_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated")
            return redirect("userprofile:profile", user_id)
    else:
        form = EditProfileForm(instance=user)

    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "cart_items": cart_items,
        "cart": cart,
        "form": form,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/edit_profile.html", context)


@never_cache
@login_required(login_url="signin")
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password Changed Successfully")
            return redirect("signin")
    else:
        form = PasswordChangeForm(request.user)

    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "cart_items": cart_items,
        "cart": cart,
        "form": form,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/change_password.html", context)


@never_cache
@login_required(login_url="signin")
def address(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "cart_items": cart_items,
        "cart": cart,
        "addresses": addresses,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/address.html", context)


@never_cache
@login_required(login_url="signin")
def add_address(request, address_type=None):
    if request.method == "POST":
        form = AddAddressForm(request.POST)
        if form.is_valid():
            pincode = form.cleaned_data.get("pincode")

            if pincode == "000000":
                messages.error(request, "Please enter a valid pincode.")
                return redirect("userprofile:add_address")

            city = form.cleaned_data.get("city")
            if not city.isalpha():
                messages.error(
                    request, "City name should contain only alphabetic characters."
                )
                return redirect("userprofile:add_address")

            # Perform custom validation for district
            district = form.cleaned_data.get("district")
            if not district.isalpha():
                messages.error(
                    request, "District name should contain only alphabetic characters."
                )
                return redirect("userprofile:add_address")

            state = form.cleaned_data.get("state")
            if not state.isalpha():
                messages.error(
                    request, "State name should contain only alphabetic characters."
                )
                return redirect("userprofile:add_address")

            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "New Address Added")
            if not address_type:
                return redirect("userprofile:address")
            else:
                return redirect("user_order_and_payment:order_address")
    else:
        form = AddAddressForm()

    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "cart_items": cart_items,
        "cart": cart,
        "form": form,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/add_address.html", context)


@never_cache
@login_required(login_url="signin")
def edit_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    if request.method == "POST":
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            pincode = form.cleaned_data.get("pincode")

            if pincode == "000000":
                messages.error(request, "Please enter a valid pincode.")
                return redirect("userprofile:edit_address", address.id)

            city = form.cleaned_data.get("city")
            if not city.isalpha():
                messages.error(
                    request, "City name should contain only alphabetic characters."
                )
                return redirect("userprofile:edit_address", address.id)

            # Perform custom validation for district
            district = form.cleaned_data.get("district")
            if not district.isalpha():
                messages.error(
                    request, "District name should contain only alphabetic characters."
                )
                return redirect("userprofile:edit_address", address.id)

            state = form.cleaned_data.get("state")
            if not state.isalpha():
                messages.error(
                    request, "State name should contain only alphabetic characters."
                )
                return redirect("userprofile:edit_address", address.id)

            form.save()
            messages.success(request, "Address Edited")
            return redirect("userprofile:address")
    else:
        form = AddAddressForm(instance=address)

    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
        "cart_items": cart_items,
        "cart": cart,
        "form": form,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/edit_address.html", context)


@never_cache
@login_required(login_url="signin")
def delete_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    address.delete()
    messages.success(request, "Address Deleted")
    return redirect("userprofile:address")


@never_cache
@login_required(login_url="signin")
def orders(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = cart_items.count() if cart_items is not None else 0

    user = request.user
    orders = Order.objects.filter(user=user)
    orderitems = OrderItems.objects.filter(order__in=orders)

    for item in orderitems:
        item.total_price = item.product.price * item.quantity
        if item.subtotal < item.product.price * item.quantity:
            item.discounted = item.product.price * item.quantity - item.subtotal

    paginator = Paginator(orderitems, 3)
    page_number = request.GET.get("page")

    try:
        orderitems = paginator.page(page_number)
    except PageNotAnInteger:
        orderitems = paginator.page(1)
    except EmptyPage:
        orderitems = paginator.page(paginator.num_pages)

    context = {
        "orders": orders,
        "orderitems": orderitems,
        "cart_count": cart_count,
        "cart": cart,
        "cart_items": cart_items,
    }
    return render(request, "userprofile/orders.html", context)


@never_cache
@login_required(login_url="signin")
def cancel_order(request, item_id):
    wallet = Wallet.objects.get(user=request.user)
    item = OrderItems.objects.get(id=item_id)

    product_variant = item.product_variant
    product = ProductVariant.objects.get(pk=product_variant.pk)
    product.quantity += item.quantity
    product.save()

    item.order_status = "Cancelled"
    if item.payment_status == "Paid":
        wallet.balance += item.subtotal
        wallet.save()
        WalletTransactions.save_transaction(
            type="Credit", amount=item.subtotal, wallet=wallet, user=request.user
        )
    item.save()
    messages.success(request, "Your order has been cancelled")
    return redirect("userprofile:orders")


@never_cache
@login_required(login_url="signin")
def delete_account(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST" and request.POST.get("confirm_delete"):
        user.delete()
        messages.success(
            request, "Your account has been deleted. Thank you for shopping with us!"
        )
        return redirect("home")

    return render(request, "userprofile/profile.html", {"user": user})


@never_cache
@login_required(login_url="signin")
def return_order(request, item_id):
    wallet = Wallet.objects.get(user=request.user)
    item = OrderItems.objects.get(id=item_id)
    item.order_status = "Returned"

    product_variant = item.product_variant
    product = ProductVariant.objects.get(pk=product_variant.pk)
    product.quantity += item.quantity
    product.save()

    if item.payment_status == "Paid":
        wallet.balance += item.subtotal
        wallet.save()
    WalletTransactions.save_transaction(
        type="Credit", amount=item.subtotal, wallet=wallet, user=request.user
    )
    item.save()
    messages.success(request, "Your product will be picked by our agent soon!")
    return redirect("userprofile:orders")


@never_cache
@login_required(login_url="signin")
def wallet(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    wallet = Wallet.objects.get(user=request.user)
    transactions = WalletTransactions.objects.filter(wallet=wallet)
    context = {
        "wallet": wallet,
        "transactions": transactions,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }
    return render(request, "userprofile/wallet.html", context)


@never_cache
@login_required(login_url="signin")
def cash_deposit_page(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count, 'paypal_client_id':paypal_client_id}

    return render(request, "userprofile/cash_deposit_page.html", context)


@login_required(login_url="signin")
def deposit(request):
    if request.method == "POST":
        deposit_amount = request.POST.get("deposit_amount")
        payment_method = request.POST.get("payment_method")

        if deposit_amount and payment_method == "PayPal":
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance += int(deposit_amount)
            wallet.save()
            WalletTransactions.save_transaction(
                type="Credit", amount=deposit_amount, wallet=wallet, user=request.user
            )
            messages.success(request, "Amount Deposited Successfully")
            return redirect("userprofile:wallet")
        else:
            messages.error(request, "Invalid payment method")
            return redirect("userprofile:wallet")

    return redirect("userprofile:wallet")


@never_cache
@login_required(login_url="signin")
def cash_withdraw_page(request):

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count}

    return render(request, "userprofile/cash_withdraw_page.html", context)


@login_required(login_url="signin")
def withdraw(request):
    if request.method == "POST":
        withdraw_amount = request.POST.get("withdraw_amount")
        wallet = Wallet.objects.get(user=request.user)
        withdraw_amount = int(withdraw_amount)
        if wallet.balance >= withdraw_amount:
            wallet.balance -= withdraw_amount
            wallet.save()
            WalletTransactions.save_transaction(
                type="Debit", amount=withdraw_amount, wallet=wallet, user=request.user
            )
            messages.success(request, "Amount Withdrawn Successfully")
            return redirect("userprofile:wallet")
        else:
            messages.error(
                request,
                "Kindly ensure that the entered amount does not exceed your current wallet balance.",
            )
            return redirect("userprofile:wallet")

    return redirect("userprofile:wallet")


@never_cache
@login_required(login_url="signin")
def transaction_history(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    transactions = WalletTransactions.objects.filter(user=request.user)

    context = {
        "transactions": transactions,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }

    return render(request, "userprofile/transaction_history.html", context)


@never_cache
@login_required(login_url="signin")
def coupon(request):

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    unused_coupons = Coupons.objects.exclude(
        Q(status="Inactive") | Q(usedcoupons__user=request.user)
    )

    context = {
        "coupons": unused_coupons,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }
    return render(request, "userprofile/coupon.html", context)


@never_cache
@login_required(login_url="signin")
def download_invoice(request, item_id):
    order_item = OrderItems.objects.get(id=item_id)
    product = order_item.product
    return render(
        request,
        "userprofile/download_invoice.html",
        {"product": product, "order_item": order_item},
    )
