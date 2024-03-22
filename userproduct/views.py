from django.shortcuts import render, redirect, get_object_or_404
from adminproductmanagement.models import Image, Product, ProductVariant
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import CartItem, Cart, Wishlist
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def product_details(request, pk):
    product = Product.objects.get(pk=pk)
    productvariants = ProductVariant.objects.filter(product=product)

    all_variant_images = []

    for variant in productvariants:
        variant_images = Image.objects.filter(productvariant=variant)
        all_variant_images.extend(variant_images)

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
        "product": product,
        "productvariants": productvariants,
        "all_variant_images": all_variant_images,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }
    return render(request, "userproduct/product_details.html", context)


@never_cache
@login_required(login_url="signin")
def add_to_cart(request):
    if request.method == "POST":
        variant_id = request.POST.get("variant")
        try:
            product_variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            messages.error(request, "Product variant does not exist.")
            return redirect(
                "userproduct:product_details", pk=product_variant.product.id
            )

        try:
            user_cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            user_cart = Cart.objects.create(user=request.user)

        if not CartItem.objects.filter(cart=user_cart).exists():
            if product_variant.quantity == 0:
                messages.error(request, "Variant is out of stock")
                user_cart.delete()
                return redirect(
                    "userproduct:product_details", pk=product_variant.product.id
                )

            if CartItem.objects.filter(
                cart=user_cart, product_variant=product_variant
            ).exists():
                messages.warning(request, "This variant is already in your cart.")
                user_cart.delete()
                return redirect(
                    "userproduct:product_details", pk=product_variant.product.id
                )

        if product_variant.quantity == 0:
            messages.error(request, "Variant is out of stock")
            return redirect(
                "userproduct:product_details", pk=product_variant.product.id
            )

        if CartItem.objects.filter(
            cart=user_cart, product_variant=product_variant
        ).exists():
            messages.warning(request, "This variant is already in your cart.")
            return redirect(
                "userproduct:product_details", pk=product_variant.product.id
            )

        product = product_variant.product

        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        existing_cart_item = CartItem.objects.filter(
            cart=cart, product_variant=product_variant
        ).first()
        if existing_cart_item:
            existing_cart_item.quantity += 1
            existing_cart_item.save()
            quantity = existing_cart_item.quantity
        else:
            quantity = 1

        subtotal = product.price * quantity

        CartItem.objects.update_or_create(
            cart=cart,
            product=product,
            product_variant=product_variant,
            defaults={"quantity": quantity, "subtotal": subtotal},
        )

        messages.success(request, "Item Added to Cart")

        return redirect("userproduct:product_details", product.pk)


@never_cache
@login_required(login_url="signin")
def cart(request, cart_id):
    if "applied_coupon_code" in request.session:
        del request.session["applied_coupon_code"]
    try:
        cart = Cart.objects.get(id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart)
        original_total = 0
        for item in cart_items:
            if item.product.offer_price is None:
                original_total += item.product.price * item.quantity
                cart.total = original_total
                original_subtotal = item.product.price * item.quantity
                item.subtotal = original_subtotal
                item.save()
            else:
                original_total += item.product.offer_price * item.quantity
                cart.total = original_total
                original_subtotal = item.product.offer_price * item.quantity
                item.subtotal = original_subtotal
                item.save()
        cart.save()

        if cart_items is not None:
            cart_count = cart_items.count()
        else:
            cart_count = 0

        context = {"cart_items": cart_items, "cart": cart, "cart_count": cart_count}
        return render(request, "userproduct/cart.html", context)
    except ObjectDoesNotExist:
        messages.error(request, "Cart not found for this user.")
        return redirect("home")


@login_required(login_url="signin")
def delete_from_cart(request, variant_id):
    user = request.user
    cart = Cart.objects.get(user=user)

    if cart.cartitem_set.count() == 1:
        cart.delete()
        messages.success(request, "Cart Cleared")
        return redirect("shop")
    else:
        product = get_object_or_404(CartItem, cart=cart, product_variant=variant_id)
        product.delete()
        messages.success(request, "Product Removed")
        return redirect("userproduct:cart", cart.id)


@login_required(login_url="signin")
def clear_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    cart.delete()
    messages.success(request, "Cart Cleared")
    return redirect("shop")


@login_required(login_url="signin")
@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity"))

        try:
            cart_item = CartItem.objects.get(id=item_id)

            cart_item.quantity = quantity
            if cart_item.quantity > 0:
                if not cart_item.product.offer_price:
                    cart_item.subtotal = (cart_item.product.price) * quantity
                    cart_item.save()
                else:
                    cart_item.subtotal = (cart_item.product.offer_price) * quantity
                    cart_item.save()

                cart = cart_item.cart
                cart_items = CartItem.objects.filter(cart=cart)
                total = sum(item.subtotal for item in cart_items)
                cart.total = total
                cart.save()

                return JsonResponse(
                    {"subtotal": cart_item.subtotal, "total": cart.total}
                )
        except CartItem.DoesNotExist:
            return JsonResponse({"error": "CartItem does not exist"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@never_cache
@login_required(login_url="signin")
def wishlist(request):
    products = Wishlist.objects.filter(user=request.user)

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_items = None
        cart_count = 0

    context = {
        "products": products,
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }
    return render(request, "userproduct/wishlist.html", context)


def add_to_wishlist(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            prod_id = request.POST.get("product_id")
            product = get_object_or_404(Product, id=prod_id)

            if Wishlist.objects.filter(user=request.user, product=product).exists():
                return JsonResponse({"status": "Product already in wishlist"})
            else:
                Wishlist.objects.create(user=request.user, product=product)
                return JsonResponse({"status": "Product added to wishlist"})
        else:
            return JsonResponse({"status": "Login to continue"}, status=401)
    else:
        return JsonResponse({"status": "Invalid request"}, status=400)


def delete_wishlist_item(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            prod_id = request.POST.get("product_id")
            product = get_object_or_404(Product, id=prod_id)

            if Wishlist.objects.filter(user=request.user, product=product).exists():
                wishlistitem = Wishlist.objects.get(product=prod_id)
                wishlistitem.delete()
                return JsonResponse({"status": "Product removed from wishlist"})

            else:
                Wishlist.objects.create(user=request.user, product=product)
                return JsonResponse({"status": "Product not found in wishlist"})

        else:
            return JsonResponse({"status": "Login to continue"}, status=401)

    return redirect("home")
