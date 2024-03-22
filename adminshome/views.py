from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Banner
from .forms import BannerForm, AddCouponFrom
from adminproductmanagement.models import Coupons
from user_order_and_payment.models import Order, OrderItems
from .render_pdf import render_to_pdf
from django.db.models import Sum
from datetime import datetime, timedelta

# Create your views here.


@never_cache
def adminsignin(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("adminshome:dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome {username}")
                return redirect("adminshome:dashboard")
            else:
                messages.error(request, "You are not an admin")
                return redirect("adminshome:adminsignin")
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect("adminshome:adminsignin")
    return render(request, "adminshome/adminsignin.html")


@login_required(login_url="adminshome:adminsignin")
def dashboard(request):
    if request.user.is_superuser:

        orders = Order.objects.all()
        paypal_orders = Order.objects.filter(paymentmethod="PayPal")
        cod_orders = Order.objects.filter(paymentmethod="Cash On Delivery")
        wallet_orders = Order.objects.filter(paymentmethod="Wallet")
        items = OrderItems.objects.filter(payment_status="Paid")
        top_items = (
            OrderItems.objects.filter(payment_status="Paid")
            .values("product__name", "product__price")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )
        top_category = (
            OrderItems.objects.filter(payment_status="Paid")
            .values("product__category__name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")
            .first()
        )
        top_brands = (
            OrderItems.objects.filter(payment_status="Paid")
            .values("product__brand__name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:3]
        )

        discounted = 0
        grand_total = 0

        for item in items:
            item.total_price = item.product.price * item.quantity
            grand_total += item.subtotal
            if item.subtotal < item.product.price * item.quantity:
                item.discounted = item.product.price * item.quantity - item.subtotal
                discounted += item.product.price * item.quantity - item.subtotal

        paypal_order_items = OrderItems.objects.filter(
            order__in=paypal_orders, payment_status="Paid"
        )
        paypal_total_amount = sum(item.subtotal for item in paypal_order_items)

        cod_order_items = OrderItems.objects.filter(
            order__in=cod_orders, payment_status="Paid"
        )
        cod_total_amount = sum(item.subtotal for item in cod_order_items)

        wallet_order_items = OrderItems.objects.filter(
            order__in=wallet_orders, payment_status="Paid"
        )
        wallet_total_amount = sum(item.subtotal for item in wallet_order_items)

        order_items = OrderItems.objects.filter(order__in=orders, payment_status="Paid")
        total_amount = sum(item.subtotal for item in order_items)

        total_order = 0
        for order in order_items:
            total_order += 1

        context = {
            "paypal_total_amount": paypal_total_amount,
            "cod_total_amount": cod_total_amount,
            "wallet_total_amount": wallet_total_amount,
            "total_amount": total_amount,
            "total_order": total_order,
            "items": items,
            "discounted": discounted,
            "grand_total": grand_total,
            "top_items": top_items,
            "top_category": top_category,
            "top_brands": top_brands,
        }

        return render(request, "adminshome/dashboard.html", context)
    else:
        return redirect("adminshome:adminsignin")


def download_pdf(request):
    filter_type = request.GET.get("filter")
    start_date = request.GET.get("start_date") or None
    end_date = request.GET.get("end_date") or None

    if start_date == None and end_date == None:
        now = datetime.now()
        if filter_type == "yearly":
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31, 23, 59, 59, 999999)
        elif filter_type == "monthly":
            start_date = datetime(now.year, now.month, 1)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
        elif filter_type == "weekly":
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif filter_type == "daily":
            start_date = datetime(now.year, now.month, now.day)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)

    items = OrderItems.objects.filter(payment_status="Paid")
    if start_date is not None and end_date is not None:
        items = items.filter(
            order__orderdate__gte=start_date, order__orderdate__lte=end_date
        )

    grand_total = 0

    for item in items:
        item.total_price = item.product.price * item.quantity
        grand_total += item.subtotal
        if item.subtotal < item.product.price * item.quantity:
            item.discounted = item.product.price * item.quantity - item.subtotal

    results = []

    for item in items:
        result_item = {
            "product_name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total_price": item.total_price,
            "subtotal": item.subtotal,
            "discounted_price": (
                item.discounted if hasattr(item, "discounted") else None
            ),
        }
        results.append(result_item)

    context = {
        "pagesize": "A4",
        "mylist": results,
        "grand_total": grand_total,
    }
    pdf = render_to_pdf("adminshome/sales_report_pdf.html", context)

    if pdf:
        response = HttpResponse(pdf, content_type="application/pdf")
        filename = "sales_report.pdf"
        content = f"attachment; filename={filename}"
        download = request.GET.get("download")
        if download:
            content = f"attachment; filename={filename}"
        response["Content-Disposition"] = content
        return response

    return HttpResponse("Failed to generate PDF", status=400)


def get_revenue_data(request):
    filter_type = request.GET.get("filter")
    start_date = request.GET.get("start_date") or None
    end_date = request.GET.get("end_date") or None

    if start_date is None and end_date is None:
        if filter_type == "yearly":
            start_date = datetime.now().replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "custom" and start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "monthly":
            start_date = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                day=30, hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "weekly":
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif filter_type == "daily":
            start_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

    orders = (
        OrderItems.objects.filter(
            payment_status="Paid",
            order__orderdate__gte=start_date,
            order__orderdate__lte=end_date,
        )
        .order_by("-order__orderdate")
        .values("order__orderdate")
        .annotate(revenue=Sum("subtotal"))
    )

    data = {"labels": [], "revenue": []}
    for order in orders:
        data["labels"].append(order["order__orderdate"])
        data["revenue"].append(order["revenue"])

    return JsonResponse(data)


def get_data(request):
    filter_type = request.GET.get("filter")
    start_date = request.GET.get("start_date") or None
    end_date = request.GET.get("end_date") or None

    if start_date is None and end_date is None:
        if filter_type == "yearly":
            start_date = datetime.now().replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "custom" and start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "monthly":
            start_date = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                day=30, hour=23, minute=59, second=59, microsecond=999999
            )
        elif filter_type == "weekly":
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif filter_type == "daily":
            start_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_date = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

    orders = OrderItems.objects.filter(
        payment_status="Paid",
        order__orderdate__gte=start_date,
        order__orderdate__lte=end_date,
    ).values("product__name", "product__price", "quantity", "subtotal")

    data = []
    grand_total = 0
    total_revenue = 0
    total_sales = 0
    total_promotions = 0

    for order in orders:
        total_price = order["product__price"] * order["quantity"]
        grand_total += order["subtotal"]
        total_revenue += order["subtotal"]
        total_sales += 1

        if order["subtotal"] < order["product__price"] * order["quantity"]:
            promotion_amount = total_price - order["subtotal"]
            order["discounted"] = (
                order["product__price"] * order["quantity"] - order["subtotal"]
            )
            total_promotions += promotion_amount

        data.append(
            {
                "name": order["product__name"],
                "price": order["product__price"],
                "quantity": order["quantity"],
                "total_price": total_price,
                "discounted": order.get("discounted", 0),
                "subtotal": order["subtotal"],
            }
        )

    paypal_orders = Order.objects.filter(paymentmethod="PayPal")
    cod_orders = Order.objects.filter(paymentmethod="Cash On Delivery")
    wallet_orders = Order.objects.filter(paymentmethod="Wallet")

    paypal_order_items = OrderItems.objects.filter(
        order__in=paypal_orders,
        payment_status="Paid",
        order__orderdate__gte=start_date,
        order__orderdate__lte=end_date,
    )
    cod_order_items = OrderItems.objects.filter(
        order__in=cod_orders,
        payment_status="Paid",
        order__orderdate__gte=start_date,
        order__orderdate__lte=end_date,
    )
    wallet_order_items = OrderItems.objects.filter(
        order__in=wallet_orders,
        payment_status="Paid",
        order__orderdate__gte=start_date,
        order__orderdate__lte=end_date,
    )

    paypal_total_amount = 0
    cod_total_amount = 0
    wallet_total_amount = 0

    for order in paypal_order_items:
        paypal_total_amount += order.subtotal

    for order in cod_order_items:
        cod_total_amount += order.subtotal

    for order in wallet_order_items:
        wallet_total_amount += order.subtotal

    return JsonResponse(
        {
            "data": data,
            "grand_total": grand_total,
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "total_promotions": total_promotions,
            "paypal_amount": paypal_total_amount,
            "cod_amount": cod_total_amount,
            "wallet_amount": wallet_total_amount,
        },
        safe=False,
    )


def adminsignout(request):
    logout(request)
    messages.success(request, "Admin logged out successfully")
    return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def manage_banner(request):
    if request.user.is_superuser:
        banners = Banner.objects.all()
        return render(request, "adminshome/manage_banner.html", {"banners": banners})
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def add_banner(request):
    if request.user.is_superuser:
        form = BannerForm()
        if request.method == "POST":
            form = BannerForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "New Banner Added")
                return redirect("adminshome:manage_banner")
        return render(request, "adminshome/add_banner.html", {"form": form})
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def edit_banner(request, pk):
    if request.user.is_superuser:
        banner = get_object_or_404(Banner, pk=pk)
        if request.method == "POST":
            form = BannerForm(request.POST, request.FILES, instance=banner)
            if form.is_valid():
                form.save()
                messages.success(request, "Banner Edited")
                return redirect("adminshome:manage_banner")
        else:
            form = BannerForm(instance=banner)
        return render(
            request, "adminshome/edit_banner.html", {"form": form, "banner": banner}
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def delete_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    messages.success(request, "Banner Deleted")
    return redirect("adminshome:manage_banner")


@login_required(login_url="adminshome:adminsignin")
def manage_coupon(request):
    if request.user.is_superuser:
        coupons = Coupons.objects.exclude(status="Inactive")
        context = {"coupons": coupons}
        return render(request, "adminshome/manage_coupon.html", context)
    else:
        return redirect("adminshome:adminsignin")


def unlist_coupon(request, coupon_id):
    coupon = Coupons.objects.get(id=coupon_id)
    coupon.status = "Inactive"
    coupon.save()
    messages.success(request, "Coupon Unlisted")
    return redirect("adminshome:manage_coupon")


def unlisted_coupons(request):
    if request.user.is_superuser:
        coupons = Coupons.objects.filter(status="Inactive")
        context = {"coupons": coupons}
        return render(request, "adminshome/unlisted_coupons.html", context)
    else:
        return redirect("adminshome:adminsignin")


def list_coupon(request, coupon_id):
    coupon = Coupons.objects.get(id=coupon_id)
    coupon.status = "Active"
    coupon.save()
    messages.success(request, "Coupon Listed")
    return redirect("adminshome:unlisted_coupons")


def add_coupon(request):
    if request.user.is_superuser:
        form = AddCouponFrom()
        if request.method == "POST":
            form = AddCouponFrom(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "New Coupon Added")
                return redirect("adminshome:manage_coupon")
        context = {"form": form}
        return render(request, "adminshome/add_coupon.html", context)
    else:
        return redirect("adminshome:adminsignin")
