from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    Image,
    CategoryOffer,
    ProductOffer,
)
from .forms import (
    CategoryForm,
    BrandForm,
    ProductForm,
    ProductVariantForm,
    AddCategoryOfferForm,
    AddProductOfferForm,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.utils import timezone

# Create your views here.


@never_cache
@login_required(login_url="adminshome:adminsignin")
def manage_category(request):
    if request.user.is_superuser:
        categories = Category.objects.filter(is_listed=True)
        return render(
            request,
            "adminproductmanagement/manage_category.html",
            {"categories": categories},
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_category(request):
    if request.user.is_superuser:
        form = CategoryForm()
        if request.method == "POST":
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "New Category Added")
                return redirect("adminproductmanagement:manage_category")
        return render(
            request, "adminproductmanagement/add_category.html", {"form": form}
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_category(request, pk):
    if request.user.is_superuser:
        category = get_object_or_404(Category, pk=pk)
        if request.method == "POST":
            form = CategoryForm(request.POST, request.FILES, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, "Category Edited")
                return redirect("adminproductmanagement:manage_category")
        else:
            form = CategoryForm(instance=category)
            offers = CategoryOffer.objects.filter(category=category, status="Active")
        return render(
            request,
            "adminproductmanagement/edit_category.html",
            {"form": form, "category": category, "offers": offers},
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category Deleted")
    return redirect("adminproductmanagement:manage_category")


@login_required(login_url="adminshome:adminsignin")
def unlist_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.is_listed = False
    category.save()
    messages.success(request, "Category Unlisted")
    return redirect("adminproductmanagement:manage_category")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def unlisted_categories(request):
    if request.user.is_superuser:
        categories = Category.objects.filter(is_listed=False)
        return render(
            request,
            "adminproductmanagement/unlisted_categories.html",
            {"categories": categories},
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def restore_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.is_listed = True
    category.save()
    messages.success(request, "Category Restored")
    return redirect("adminproductmanagement:unlisted_categories")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def manage_brand(request):
    if request.user.is_superuser:
        brands = Brand.objects.filter(is_listed=True)
        return render(
            request, "adminproductmanagement/manage_brand.html", {"brands": brands}
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_brand(request):
    if request.user.is_superuser:
        form = BrandForm()
        if request.method == "POST":
            form = BrandForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "New Brand Added")
                return redirect("adminproductmanagement:manage_brand")
        return render(request, "adminproductmanagement/add_brand.html", {"form": form})
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_brand(request, pk):
    if request.user.is_superuser:
        brand = get_object_or_404(Brand, pk=pk)
        if request.method == "POST":
            form = BrandForm(request.POST, request.FILES, instance=brand)
            if form.is_valid():
                form.save()
                messages.success(request, "Brand Edited")
                return redirect("adminproductmanagement:manage_brand")
        else:
            form = BrandForm(instance=brand)
        return render(
            request,
            "adminproductmanagement/edit_brand.html",
            {"form": form, "brand": brand},
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def delete_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    messages.success(request, "Brand Deleted")
    return redirect("adminproductmanagement:manage_brand")


@login_required(login_url="adminshome:adminsignin")
def unlist_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.is_listed = False
    brand.save()
    messages.success(request, "Brand Unlisted")
    return redirect("adminproductmanagement:manage_brand")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def unlisted_brands(request):
    if request.user.is_superuser:
        brands = Brand.objects.filter(is_listed=False)
        return render(
            request, "adminproductmanagement/unlisted_brands.html", {"brands": brands}
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def restore_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.is_listed = True
    brand.save()
    messages.success(request, "Brand Restored")
    return redirect("adminproductmanagement:unlisted_brands")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def manage_product(request):
    if request.user.is_superuser:
        query = request.GET.get("q")
        products = Product.objects.filter(is_listed=True)

        if query:
            query = query.replace(" ", "")
            products = products.filter(
                Q(name__icontains=query)
                | Q(category__name__icontains=query)
                | Q(brand__name__icontains=query)
                | Q(type__icontains=query)
            )

        context = {"products": products, "query": query}

        return render(request, "adminproductmanagement/manage_product.html", context)
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_product(request):
    if request.user.is_superuser:
        form = ProductForm()
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "New Product Added")
                return redirect("adminproductmanagement:manage_product")
        return render(
            request, "adminproductmanagement/add_product.html", {"form": form}
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_product(request, pk=None):
    if request.user.is_superuser:
        product = get_object_or_404(Product, pk=pk)
        variants = ProductVariant.objects.filter(product=product)
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Product Edited")
                return redirect("adminproductmanagement:manage_product")
        else:
            form = ProductForm(instance=product)
            offers = ProductOffer.objects.filter(product=product, status="Active")
        return render(
            request,
            "adminproductmanagement/edit_product.html",
            {"form": form, "product": product, "variants": variants, "offers": offers},
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product Deleted")
    return redirect("adminproductmanagement:manage_product")


@login_required(login_url="adminshome:adminsignin")
def unlist_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_listed = False
    product.save()
    messages.success(request, "Product Unlisted")
    return redirect("adminproductmanagement:manage_product")


@login_required(login_url="adminshome:adminsignin")
def restore_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_listed = True
    product.save()
    messages.success(request, "Product Restored")
    return redirect("adminproductmanagement:unlisted_products")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def unlisted_products(request):
    if request.user.is_superuser:
        products = Product.objects.filter(is_listed=False)
        query = request.GET.get("q")
        if query:
            query = query.replace(" ", "")
            products = products.filter(name__icontains=query)

        context = {"products": products, "query": query}
        return render(request, "adminproductmanagement/unlisted_products.html", context)
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_variant(request, product_id):
    if request.user.is_superuser:
        form = ProductVariantForm()
        if request.method == "POST":
            form = ProductVariantForm(request.POST, request.FILES)
            if form.is_valid():
                new_variant = form.save(commit=False)
                form.instance.product = Product.objects.get(id=product_id)
                form.save()
                variant_images = request.FILES.getlist("images")
                if variant_images:
                    for img in variant_images:
                        Image.objects.create(productvariant=new_variant, image=img)
                messages.success(request, "New Variant Added")
                return redirect(
                    reverse(
                        "adminproductmanagement:edit_product", kwargs={"pk": product_id}
                    )
                )
        return render(
            request, "adminproductmanagement/add_variant.html", {"form": form}
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_variant(request, pk):
    if request.user.is_superuser:
        variant = get_object_or_404(ProductVariant, pk=pk)
        images = Image.objects.filter(productvariant=variant)
        if request.method == "POST":
            form = ProductVariantForm(request.POST, request.FILES, instance=variant)
            if form.is_valid():
                form.save()
                for image_file in request.FILES.getlist("images"):
                    Image.objects.create(image=image_file, productvariant=variant)
                messages.success(request, "Variant Edited")
                return redirect(
                    reverse(
                        "adminproductmanagement:edit_product",
                        kwargs={"pk": variant.product.pk},
                    )
                )
        else:
            form = ProductVariantForm(instance=variant)
        return render(
            request,
            "adminproductmanagement/edit_variant.html",
            {"form": form, "variant": variant, "images": images},
        )
    else:
        return redirect("adminshome:adminsignin")


@login_required(login_url="adminshome:adminsignin")
def delete_variant(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    variant.delete()
    messages.success(request, "Variant Deleted")
    return redirect(
        reverse(
            "adminproductmanagement:edit_product", kwargs={"pk": variant.product.pk}
        )
    )


@login_required(login_url="adminshome:adminsignin")
def delete_variant_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    variant_pk = image.productvariant.pk
    image.delete()
    messages.success(request, "Variant Image Deleted")
    return redirect("adminproductmanagement:edit_variant", pk=variant_pk)


@login_required(login_url="adminshome:adminsignin")
def delete_product_thumbnail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.thumbnail:
        product.thumbnail.delete()
        messages.success(request, "Product Thumbnail Deleted")
        return redirect("adminproductmanagement:edit_product", pk=pk)
    return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_category_offer(request, category_id):
    if request.user.is_superuser:
        category = get_object_or_404(Category, id=category_id)

        existing_offer = CategoryOffer.objects.filter(category=category).exists()
        if existing_offer:
            messages.warning(request, "An offer already exists for this category.")
            return redirect("adminproductmanagement:edit_category", category_id)

        form = AddCategoryOfferForm()

        if request.method == "POST":
            form = AddCategoryOfferForm(request.POST)

            if form.is_valid():
                form.instance.category = category
                discount_percentage = form.cleaned_data["discount_percentage"]
                form.save()

                products = Product.objects.filter(category=category)

                for product in products:
                    if not product.offer_price:
                        product.offer_price = product.price - (
                            product.price * discount_percentage // 100
                        )
                        product.save()

                messages.success(request, "Offer Added")
                return redirect("adminproductmanagement:edit_category", category_id)

        return render(
            request, "adminproductmanagement/add_category_offer.html", {"form": form}
        )

    else:
        return redirect("adminshome:adminsignin")


def delete_category_offer(request, offer_id):
    if request.user.is_superuser:
        offer = CategoryOffer.objects.get(id=offer_id)
        category = offer.category

        products = Product.objects.filter(category=category)

        for product in products:
            if not ProductOffer.objects.filter(
                product=product, status="Active", valid_to__gte=timezone.now()
            ).exists():
                product.offer_price = None
                product.save()

        offer.delete()

        messages.success(request, "Offer deleted")
        return redirect("adminproductmanagement:edit_category", category.pk)
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_category_offer(request, offer_id):
    if request.user.is_superuser:
        offer = get_object_or_404(CategoryOffer, id=offer_id)
        if request.method == "POST":
            form = AddCategoryOfferForm(request.POST, instance=offer)
            if form.is_valid():
                category = offer.category
                form.instance.category = category
                discount_percentage = form.cleaned_data["discount_percentage"]
                form.save()

                products = Product.objects.filter(category=category)

                for product in products:
                    if ProductOffer.objects.filter(product=product).exists():
                        continue
                    else:
                        product.offer_price = product.price - (
                            product.price * discount_percentage // 100
                        )
                        product.save()

                messages.success(request, "Offer Edited")
                return redirect(
                    "adminproductmanagement:edit_category", offer.category.pk
                )
        else:
            form = AddCategoryOfferForm(instance=offer)
        return render(
            request, "adminproductmanagement/edit_category_offer.html", {"form": form}
        )
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def add_product_offer(request, product_id):
    if request.user.is_superuser:
        product = get_object_or_404(Product, id=product_id)

        existing_offer = ProductOffer.objects.filter(product=product).exists()
        if existing_offer:
            messages.warning(request, "An offer already exists for this product.")
            return redirect("adminproductmanagement:edit_product", product_id)

        form = AddProductOfferForm()

        if request.method == "POST":
            form = AddProductOfferForm(request.POST)

            if form.is_valid():
                product = Product.objects.get(id=product_id)
                form.instance.product = product
                discount_percentage = form.cleaned_data["discount_percentage"]
                form.save()

                product.offer_price = product.price - (
                    product.price * discount_percentage // 100
                )

                product.save()

                messages.success(request, "Offer Added")
                return redirect("adminproductmanagement:edit_product", product_id)

        else:
            return render(
                request, "adminproductmanagement/add_product_offer.html", {"form": form}
            )

    else:
        return redirect("adminshome:adminsignin")


def delete_product_offer(request, offer_id):
    if request.user.is_superuser:
        offer = get_object_or_404(ProductOffer, id=offer_id)
        product = offer.product

        category_offer = CategoryOffer.objects.filter(
            category=product.category, status="Active", valid_to__gte=timezone.now()
        ).first()

        if category_offer:
            product.offer_price = product.price - (
                product.price * category_offer.discount_percentage // 100
            )
            product.save()
        else:
            product.offer_price = None
            product.save()

        offer.delete()
        messages.success(request, "Offer deleted")
        return redirect("adminproductmanagement:edit_product", product.pk)
    else:
        return redirect("adminshome:adminsignin")


@never_cache
@login_required(login_url="adminshome:adminsignin")
def edit_product_offer(request, offer_id):
    if request.user.is_superuser:
        offer = get_object_or_404(ProductOffer, id=offer_id)
        if request.method == "POST":
            form = AddProductOfferForm(request.POST, instance=offer)
            if form.is_valid():
                product = offer.product
                form.instance.product = product
                discount_percentage = form.cleaned_data["discount_percentage"]
                form.save()

                product.offer_price = product.price - (
                    product.price * discount_percentage // 100
                )

                product.save()
                messages.success(request, "Offer Edited")
                return redirect("adminproductmanagement:edit_product", offer.product.pk)
        else:
            form = AddProductOfferForm(instance=offer)
        return render(
            request, "adminproductmanagement/edit_product_offer.html", {"form": form}
        )
    else:
        return redirect("adminshome:adminsignin")
