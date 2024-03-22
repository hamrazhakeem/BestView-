from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_order_and_payment.models import OrderItems
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from userprofile.models import Wallet, WalletTransactions
from adminproductmanagement.models import ProductVariant

# Create your views here.


@never_cache
@login_required(login_url="adminshome:adminsignin")
def manage_order(request):
    if request.user.is_superuser:
        orderitems = OrderItems.objects.all()
        query = request.GET.get("q")

        if query:
            query = query.replace(" ", "")
            orderitems = orderitems.filter(order__order_id__icontains=query)

        return render(
            request,
            "admin_order_and_payment/manage_order.html",
            {"orderitems": orderitems, "query": query},
        )

    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def manage_order_status(request, item_id):
    if request.user.is_superuser:
        order_item = get_object_or_404(OrderItems, id=item_id)
        return render(
            request,
            "admin_order_and_payment/manage_order_status.html",
            {"order_item": order_item},
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def update_order_status(request, item_id):
    if request.method == "POST":
        order_item = get_object_or_404(OrderItems, id=item_id)
        new_status = request.POST.get("status")
        if new_status in dict(OrderItems.ORDER_STATUS_CHOICES) and new_status not in [
            "Returned"
        ]:
            wallet = Wallet.objects.get(user=order_item.order.user)
            if order_item.payment_status == "Paid" and new_status == "Cancelled":
                wallet.balance += order_item.subtotal
                wallet.save()
                WalletTransactions.save_transaction(
                    type="Credit",
                    amount=order_item.subtotal,
                    wallet=wallet,
                    user=order_item.order.user,
                )
            order_item.order_status = new_status

            if new_status in ["Cancelled"]:
                product_variant = order_item.product_variant
                product = ProductVariant.objects.get(pk=product_variant.pk)
                product.quantity += order_item.quantity
                product.save()

            order_item.save()

            messages.success(request, "Order Status Updated")
            return redirect("admin_order_and_payment:manage_order")
        else:
            return HttpResponseForbidden(
                "Forbidden: You are not allowed to update the order status to 'Returned'."
            )

    return redirect("admin_order_and_payment:manage_order_status", item_id=item_id)
