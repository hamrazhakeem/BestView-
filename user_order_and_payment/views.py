from typing import Any
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from userprofile.models import Address
from user_order_and_payment.models import OrderAddress, Order, OrderItems
from userproduct.models import Cart, CartItem
from userprofile.models import Wallet, WalletTransactions
from django.contrib import messages
from adminproductmanagement.models import Coupons, ProductVariant, UsedCoupons
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic import TemplateView
import os
from dotenv import load_dotenv
load_dotenv()

# Create your views here.


@never_cache
@login_required(login_url="signin")
def order_address(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except:
        return redirect("home")
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        if item.quantity > item.product_variant.quantity:
            messages.error(
                request,
                f"{ item.product.name } { item.product_variant.color } quantity exceeds available quantity",
            )
            return redirect("userproduct:cart", cart.id)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    addresses = Address.objects.filter(user=user)

    return render(
        request,
        "user_order_and_payment/order_address.html",
        {
            "addresses": addresses,
            "cart": cart,
            "cart_items": cart_items,
            "cart_count": cart_count,
        },
    )


@never_cache
@login_required(login_url="signin")
def payment_method(request):

    applied_coupon_code = request.session.get("applied_coupon_code")

    available_coupons = Coupons.objects.filter(code=applied_coupon_code).exists()

    if not available_coupons:
        if "applied_coupon_code" in request.session:
            del request.session["applied_coupon_code"]
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            original_total = sum(
                item.product.price * item.quantity for item in cart_items
            )
            cart.total = original_total
            cart.save()

            for item in cart_items:
                if not item.product.offer_price:
                    original_subtotal = item.product.price * item.quantity
                    item.subtotal = original_subtotal
                    item.save()
                else:
                    original_subtotal = item.product.offer_price * item.quantity
                    item.subtotal = original_subtotal
                    item.save()

    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except:
        return redirect("home")
    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        if item.quantity > item.product_variant.quantity:
            messages.error(
                request,
                f"{ item.product.name } { item.product_variant.color } quantity exceeds available quantity",
            )
            return redirect("userproduct:cart", cart.id)

    if cart_items is not None:
        cart_count = cart_items.count()
    else:
        cart_count = 0

    if request.method == "POST":
        selected_address_id = request.POST.get("selected_address_id")
        if selected_address_id:
            selected_address = Address.objects.get(pk=selected_address_id)
            request.session["selected_address"] = selected_address.id

            return redirect("user_order_and_payment:payment_method")

    if applied_coupon_code is None:
        paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
        context = {"cart": cart, "cart_items": cart_items, "cart_count": cart_count, "paypal_client_id": paypal_client_id}
    else:
        paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
        context = {
            "cart": cart,
            "cart_items": cart_items,
            "cart_count": cart_count,
            "applied_coupon_code": applied_coupon_code,
            "paypal_client_id": paypal_client_id
        }

    return render(request, "user_order_and_payment/payment_method.html", context)


@never_cache
@login_required(login_url="signin")
def place_order(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except:
        return redirect("home")
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        if item.quantity > item.product_variant.quantity:
            messages.error(
                request,
                f"{ item.product.name } { item.product_variant.color } quantity exceeds available quantity",
            )
            return redirect("userproduct:cart", cart.id)

    payment_method = request.POST.get("payment_method")

    selected_address_id = request.session.get("selected_address")
    selected_address = (
        Address.objects.get(pk=selected_address_id) if selected_address_id else None
    )

    order_address = None
    if selected_address:
        order_address = OrderAddress.objects.create(
            house_or_building_name=selected_address.house_or_building_name,
            street_address=selected_address.street_address,
            city=selected_address.city,
            district=selected_address.district,
            pincode=selected_address.pincode,
            state=selected_address.state,
            phone_no=selected_address.phone_no,
        )

    order = Order.objects.create(
        total=cart.total,
        user=user,
        paymentmethod=payment_method,
        orderaddress=order_address,
    )

    order_items = []

    for cart_item in cart_items:
        if order.paymentmethod == "Cash On Delivery" and order.total > 200:
            messages.error(
                request, "Orders exceeding $200 are not eligible for Cash On Delivery."
            )
            return redirect("user_order_and_payment:payment_method")
        elif order.paymentmethod == "Cash On Delivery":
            payment_status = "Pending"
        elif order.paymentmethod == "Wallet":
            payment_status = "Paid"

            wallet = Wallet.objects.get(user=request.user)

            if wallet.balance >= order.total:
                wallet.balance -= cart_item.subtotal
                wallet.save()

            else:
                messages.error(
                    request,
                    "Please ensure that the total amount of your order does not exceed the balance available in your wallet.",
                )
                return redirect("userproduct:cart", cart.id)
        else:
            payment_status = "Paid"

        order_item = OrderItems.objects.create(
            quantity=cart_item.quantity,
            subtotal=cart_item.subtotal,
            product=cart_item.product,
            product_variant=cart_item.product_variant,
            order=order,
            payment_status=payment_status,
        )
        order_items.append(order_item)

        product_variant = order_item.product_variant
        product = ProductVariant.objects.get(pk=product_variant.pk)
        product.quantity -= order_item.quantity
        product.save()

    if order.paymentmethod == "Wallet":
        wallet = Wallet.objects.get(user=request.user)
        WalletTransactions.save_transaction(
            type="Debit", amount=order.total, wallet=wallet, user=request.user
        )
    cart.delete()

    context = {
        "order_items": order_items,
        "order_address": order_address,
        "order": order,
        "payment_method": payment_method,
    }

    return render(request, "user_order_and_payment/order_confirm.html", context)


class payment_failed(TemplateView):
    template_name = "user_order_and_payment/payment_failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = None
        cart_items = None
        cart_count = 0

        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user).first()
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = cart_items.count()

        context["cart"] = cart
        context["cart_count"] = cart_count
        context["cart_items"] = cart_items
        return context


def apply_coupon(request):
    if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            if item.quantity > item.product_variant.quantity:
                messages.error(
                    request,
                    f"{ item.product.name } { item.product_variant.color } quantity exceeds available quantity",
                )
                return redirect("userproduct:cart", cart.id)
        applied_coupon_code = request.POST.get("entered_coupon")

        try:
            coupon = Coupons.objects.exclude(status="Inactive").get(
                code=applied_coupon_code
            )

            if timezone.now().date() > coupon.valid_to:
                messages.error(request, "Coupon has expired")
                return redirect("user_order_and_payment:payment_method")

        except ObjectDoesNotExist:
            messages.error(request, "Invalid Coupon Entered")
            return redirect("user_order_and_payment:payment_method")

        if cart.total >= coupon.minimum_amount:
            used_coupon = UsedCoupons.objects.filter(user=request.user, code=coupon)

            if used_coupon:
                messages.error(request, "Coupon already redeemed")
                return redirect("user_order_and_payment:payment_method")

            else:
                used_coupon = UsedCoupons.objects.create(code=coupon, user=request.user)
                used_coupon.save()
                total_discount = 0
                for item in cart_items:
                    discount_amount = (
                        item.subtotal * coupon.discount_percentage
                    ) // 100
                    item.subtotal -= discount_amount
                    item.save()
                    total_discount += discount_amount

                cart.total -= total_discount

                cart.save()
                request.session["applied_coupon_code"] = applied_coupon_code
                coupon.save()
                messages.success(request, "Coupon Applied")
                return redirect("user_order_and_payment:payment_method")
        else:
            messages.warning(
                request,
                "Ensure that the total order amount meets or exceeds the minimum required amount specified by the coupon.",
            )

    return redirect("user_order_and_payment:payment_method")


@login_required(login_url="signin")
def remove_coupon(request):
    try:
        if "applied_coupon_code" in request.session:
            applied_coupon_code = request.session["applied_coupon_code"]
            del request.session["applied_coupon_code"]

            coupon = Coupons.objects.get(code=applied_coupon_code)
            coupon.save()

            used_coupon = UsedCoupons.objects.get(code=coupon, user=request.user)
            used_coupon.delete()

            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            original_total = sum(
                (
                    item.product.price * item.quantity
                    if not item.product.offer_price
                    else item.product.offer_price * item.quantity
                )
                for item in cart_items
            )

            cart.total = original_total
            cart.save()

            for item in cart_items:
                if not item.product.offer_price:
                    original_subtotal = item.product.price * item.quantity
                    item.subtotal = original_subtotal
                    item.save()
                else:
                    original_subtotal = item.product.offer_price * item.quantity
                    item.subtotal = original_subtotal
                    item.save()

            messages.success(request, "Coupon Removed")
            return redirect("user_order_and_payment:payment_method")
    except ObjectDoesNotExist:
        messages.error(request, "Coupon does not exist")
        return redirect("user_order_and_payment:payment_method")
