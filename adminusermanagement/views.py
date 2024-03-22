from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from usershome.models import CustomUser
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="adminshome:adminsignin")
def userlist(request):
    if request.user.is_superuser:
        query = request.GET.get("q")
        users = CustomUser.objects.all()

        if query:
            query = query.replace(" ", "")
            users = users.filter(Q(username__icontains=query))

        context = {"users": users, "query": query}

        return render(request, "adminusermanagement/userlist.html", context)
    else:
        return redirect("adminshome:adminsignin")


def block_unblock_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.is_active:
        user.is_active = False
        messages.success(request, "User successfully blocked.")
    else:
        user.is_active = True
        messages.success(request, "User successfully unblocked.")

    user.save()
    return redirect("adminusermanagement:userlist")
