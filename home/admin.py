from django.contrib import admin
from django.utils.html import format_html

from home.models import (
    Contact,
    Category,
    Product,
    Cart,
    Order,
    OrderItem,
    Review,
    Wishlist,
)


# =========================
# CONTACT ADMIN
# =========================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        'Name',
        'Email',
        'Phone',
        'Message',
        'date',
    )


# =========================
# CATEGORY ADMIN
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
    )


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product_image',
        'name',
        'category',
        'price',
        'stock',
        'stock_status',
        'date',
    )

    list_filter = (
        'category',
        'date',
    )

    search_fields = (
        'name',
        'description',
        'category__name',
    )

    def product_image(self, obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )

        return "No Image"

    product_image.short_description = "Image"

    def stock_status(self, obj):

        if obj.stock == 0:

            return "❌ Out of Stock"

        elif obj.stock <= 10:

            return "⚠️ Low Stock"

        else:

            return "✅ Available"

    stock_status.short_description = "Stock Status"


# =========================
# CART ADMIN
# =========================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product',
        'quantity',
        'date',
    )


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'name',
        'phone',
        'city',
        'pincode',
        'total',
        'payment_method',
        'status',
        'date',
    )

    list_filter = (
        'status',
        'payment_method',
        'date',
    )

    search_fields = (
        'name',
        'phone',
        'city',
        'pincode',
        'user__username',
    )


# =========================
# ORDER ITEM ADMIN
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )

    list_filter = (
        'order',
        'product',
    )


# =========================
# REVIEW ADMIN
# =========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product',
        'user',
        'rating',
        'comment',
        'date',
    )

    list_filter = (
        'rating',
        'date',
    )

    search_fields = (
        'product__name',
        'user__username',
        'comment',
    )


# =========================
# WISHLIST ADMIN
# =========================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'product',
        'date',
    )

    list_filter = (
        'date',
        'product',
    )

    search_fields = (
        'user__username',
        'product__name',
    )