from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User

from django.db.models import Sum, Avg, Count, Q

from django.utils import timezone

from datetime import timedelta

import random

from .models import (
    Contact,
    Category,
    Product,
    Cart,
    Order,
    OrderItem,
    Profile,
    Review,
    OTPVerification,
    Wishlist,
)


# ==================================================
# HOME
# ==================================================

def index(request):

    # DYNAMIC CATEGORIES
    categories = Category.objects.all().order_by("name")

    # FEATURED PRODUCTS
    featured_products = Product.objects.filter(
        stock__gt=0
    ).annotate(
        average_rating=Avg("reviews__rating"),
        review_count=Count("reviews")
    ).order_by(
        "-average_rating",
        "-id"
    )[:8]

    # SPECIAL OFFERS
    offer_products = Product.objects.filter(
        stock__gt=0,
        price__gte=50
    ).order_by(
        "price"
    )[:4]

    return render(
        request,
        "index.html",
        {
            "categories": categories,
            "featured_products": featured_products,
            "offer_products": offer_products,
        }
    )


# ==================================================
# CATEGORIES
# ==================================================

def categories(request):

    categories = Category.objects.all()

    return render(
        request,
        "categories.html",
        {
            "categories": categories
        }
    )


# ==================================================
# PRODUCTS
# SEARCH + CATEGORY + SORT + STOCK FILTER
# ==================================================

def products(request):

    products = Product.objects.annotate(
        average_rating=Avg("reviews__rating"),
        review_count=Count("reviews")
    )

    # ----------------------------------------------
    # SEARCH
    # ----------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )

    # ----------------------------------------------
    # CATEGORY FILTER
    # ----------------------------------------------

    category = request.GET.get(
        "category",
        ""
    ).strip()

    if category:

        products = products.filter(
            category__name=category
        )

    # ----------------------------------------------
    # SORT
    # ----------------------------------------------

    sort = request.GET.get(
        "sort",
        ""
    ).strip()

    if sort == "price_low":

        products = products.order_by(
            "price"
        )

    elif sort == "price_high":

        products = products.order_by(
            "-price"
        )

    elif sort == "name_az":

        products = products.order_by(
            "name"
        )

    elif sort == "name_za":

        products = products.order_by(
            "-name"
        )

    elif sort == "rating":

        products = products.order_by(
            "-average_rating"
        )

    elif sort == "newest":

        products = products.order_by(
            "-date"
        )

    else:

        products = products.order_by(
            "-id"
        )

    # ----------------------------------------------
    # STOCK FILTER
    # ----------------------------------------------

    stock = request.GET.get(
        "stock",
        ""
    ).strip()

    if stock == "available":

        products = products.filter(
            stock__gt=0
        )

    elif stock == "out":

        products = products.filter(
            stock=0
        )

    # ----------------------------------------------
    # CATEGORIES
    # ----------------------------------------------

    categories = Category.objects.all()

    # ----------------------------------------------
    # SEND DATA TO TEMPLATE
    # ----------------------------------------------

    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "search": search,
            "search_query": search,
            "selected_category": category,
            "selected_sort": sort,
            "selected_stock": stock,
        }
    )


# ==================================================
# PRODUCT DETAIL
# ==================================================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related(
        "user"
    ).order_by(
        "-date"
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "reviews": reviews
        }
    )


# ==================================================
# ADD REVIEW
# ==================================================

@login_required(login_url="login")
def add_review(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        rating = request.POST.get(
            "rating"
        )

        comment = request.POST.get(
            "comment",
            ""
        ).strip()

        try:

            rating = int(rating)

        except (TypeError, ValueError):

            rating = 5

        if rating < 1:

            rating = 1

        if rating > 5:

            rating = 5

        if comment:

            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )

    return redirect(
        "product_detail",
        product_id=product.id
    )


# ==================================================
# ADD TO CART
# USER-WISE CART SECURITY
# ==================================================

@login_required(login_url="login")
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # ----------------------------------------------
    # STOCK CHECK
    # ----------------------------------------------

    if product.stock <= 0:

        return redirect(
            "products"
        )

    # ----------------------------------------------
    # CURRENT USER CART ITEM
    # ----------------------------------------------

    cart_item = Cart.objects.filter(
        user=request.user,
        product=product
    ).first()

    # ----------------------------------------------
    # EXISTING ITEM
    # ----------------------------------------------

    if cart_item:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1

            cart_item.save()

    # ----------------------------------------------
    # NEW ITEM
    # ----------------------------------------------

    else:

        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=1
        )

    return redirect(
        "cart"
    )


# ==================================================
# CART
# USER-WISE + STOCK SAFE CART
# ==================================================

@login_required(login_url="login")
def cart(request):

    # ----------------------------------------------
    # ONLY CURRENT USER'S CART
    # ----------------------------------------------

    cart_items = Cart.objects.filter(
        user=request.user
    ).select_related(
        "product",
        "product__category"
    )

    # ----------------------------------------------
    # CHECK STOCK AND FIX CART QUANTITY
    # ----------------------------------------------

    for item in cart_items:

        # Product completely out of stock
        if item.product.stock <= 0:

            item.delete()

        # Cart quantity greater than stock
        elif item.quantity > item.product.stock:

            item.quantity = item.product.stock

            item.save()

    # ----------------------------------------------
    # GET UPDATED USER CART
    # ----------------------------------------------

    cart_items = Cart.objects.filter(
        user=request.user
    ).select_related(
        "product",
        "product__category"
    )

    # ----------------------------------------------
    # CALCULATE CART TOTAL
    # ----------------------------------------------

    cart_total = 0

    for item in cart_items:

        item.total = (
            item.product.price *
            item.quantity
        )

        cart_total += item.total

    # ----------------------------------------------
    # SEND DATA TO CART PAGE
    # ----------------------------------------------

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "cart_total": cart_total,
        }
    )


# ==================================================
# INCREASE CART
# USER-WISE SECURITY
# ==================================================

@login_required(login_url="login")
def increase_cart(request, cart_id):

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    product = cart_item.product

    if cart_item.quantity < product.stock:

        cart_item.quantity += 1

        cart_item.save()

    return redirect(
        "cart"
    )


# ==================================================
# DECREASE CART
# USER-WISE SECURITY
# ==================================================

@login_required(login_url="login")
def decrease_cart(request, cart_id):

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1

        cart_item.save()

    else:

        cart_item.delete()

    return redirect(
        "cart"
    )


# ==================================================
# REMOVE FROM CART
# USER-WISE SECURITY
# ==================================================

@login_required(login_url="login")
def remove_from_cart(request, cart_id):

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    cart_item.delete()

    return redirect(
        "cart"
    )


# ==================================================
# CHECKOUT
# FINAL STOCK VALIDATION
# USER-WISE CART
# ==================================================

@login_required(login_url="login")
def checkout(request):

    # ----------------------------------------------
    # ONLY CURRENT USER'S CART
    # ----------------------------------------------

    cart_items = Cart.objects.filter(
        user=request.user
    ).select_related(
        "product"
    )

    # ----------------------------------------------
    # EMPTY CART CHECK
    # ----------------------------------------------

    if not cart_items.exists():

        return redirect(
            "cart"
        )

    # ----------------------------------------------
    # FINAL STOCK CHECK
    # ----------------------------------------------

    stock_error = None

    for item in cart_items:

        if item.product.stock <= 0:

            stock_error = (
                f"{item.product.name} is currently "
                f"out of stock."
            )

            break

        if item.quantity > item.product.stock:

            stock_error = (
                f"Only {item.product.stock} unit(s) of "
                f"{item.product.name} are available."
            )

            break

    # ----------------------------------------------
    # FIX CART IF STOCK CHANGED
    # ----------------------------------------------

    if stock_error:

        for item in cart_items:

            if item.product.stock <= 0:

                item.delete()

            elif item.quantity > item.product.stock:

                item.quantity = item.product.stock

                item.save()

        # Reload current user's cart
        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related(
            "product"
        )

        # ------------------------------------------
        # CART BECAME EMPTY
        # ------------------------------------------

        if not cart_items.exists():

            return render(
                request,
                "checkout.html",
                {
                    "cart_items": cart_items,
                    "total": 0,
                    "error": stock_error,
                }
            )

    # ----------------------------------------------
    # CALCULATE TOTAL
    # ----------------------------------------------

    total = sum(
        item.product.price *
        item.quantity
        for item in cart_items
    )

    # ----------------------------------------------
    # CHECKOUT FORM SUBMITTED
    # ----------------------------------------------

    if request.method == "POST":

        # ------------------------------------------
        # FINAL STOCK CHECK BEFORE ORDER
        # ------------------------------------------

        for item in cart_items:

            if item.product.stock <= 0:

                return render(
                    request,
                    "checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"{item.product.name} is "
                            f"currently out of stock."
                        ),
                    }
                )

            if item.quantity > item.product.stock:

                return render(
                    request,
                    "checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"Only {item.product.stock} "
                            f"unit(s) of {item.product.name} "
                            f"are available."
                        ),
                    }
                )

        # ------------------------------------------
        # GET CUSTOMER DETAILS
        # ------------------------------------------

        name = request.POST.get(
            "name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        # ------------------------------------------
        # BASIC FORM VALIDATION
        # ------------------------------------------

        if not name or not phone or not address or not city or not pincode:

            return render(
                request,
                "checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                    "error": (
                        "Please fill all delivery details."
                    ),
                }
            )

        # ------------------------------------------
        # CREATE PENDING ORDER
        # ------------------------------------------

        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            total=total,
            status="Pending"
        )

        # ------------------------------------------
        # CREATE ORDER ITEMS
        # ------------------------------------------

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # ------------------------------------------
        # PAYMENT
        # ------------------------------------------

        return redirect(
            "payment",
            order_id=order.id
        )

    # ----------------------------------------------
    # SHOW CHECKOUT PAGE
    # ----------------------------------------------

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "total": total
        }
    )


# ==================================================
# PAYMENT
# USER-WISE CART CLEARING
# ==================================================

@login_required(login_url="login")
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    ).select_related(
        "product"
    )

    # ----------------------------------------------
    # PLACE ORDER
    # ----------------------------------------------

    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method"
        )

        allowed_methods = [
            "Cash on Delivery",
            "UPI",
            "Debit / Credit Card",
        ]

        if payment_method not in allowed_methods:

            return render(
                request,
                "payment.html",
                {
                    "order": order,
                    "items": items,
                    "total": order.total,
                    "error": (
                        "Please select a valid "
                        "payment method."
                    )
                }
            )

        # ------------------------------------------
        # CHECK STOCK AGAIN
        # ------------------------------------------

        for item in items:

            if item.quantity > item.product.stock:

                return render(
                    request,
                    "payment.html",
                    {
                        "order": order,
                        "items": items,
                        "total": order.total,
                        "error": (
                            f"{item.product.name} "
                            f"is out of stock."
                        )
                    }
                )

        # ------------------------------------------
        # REDUCE STOCK
        # ------------------------------------------

        for item in items:

            product = item.product

            product.stock -= item.quantity

            if product.stock < 0:

                product.stock = 0

            product.save()

        # ------------------------------------------
        # SAVE PAYMENT METHOD
        # ------------------------------------------

        order.payment_method = payment_method

        # ------------------------------------------
        # CONFIRM ORDER
        # ------------------------------------------

        order.status = "Confirmed"

        order.save()

        # ------------------------------------------
        # CLEAR ONLY CURRENT USER'S CART
        # ------------------------------------------

        Cart.objects.filter(
            user=request.user
        ).delete()

        # ------------------------------------------
        # ORDER SUCCESS
        # ------------------------------------------

        return redirect(
            "order_success",
            order_id=order.id
        )

    return render(
        request,
        "payment.html",
        {
            "order": order,
            "items": items,
            "total": order.total
        }
    )


# ==================================================
# ORDER SUCCESS
# ==================================================

@login_required(login_url="login")
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "order_success.html",
        {
            "order": order
        }
    )


# ==================================================
# ABOUT
# ==================================================

def about(request):

    return render(
        request,
        "about.html"
    )


# ==================================================
# CONTACT
# ==================================================

def contact(request):

    if request.method == "POST":

        # ------------------------------------------
        # GET CONTACT DETAILS
        # ------------------------------------------

        name = request.POST.get(
            "name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        message = request.POST.get(
            "message",
            ""
        ).strip()

        # ------------------------------------------
        # REQUIRED FIELD CHECK
        # ------------------------------------------

        if not name or not email or not phone or not message:

            return render(
                request,
                "contact.html",
                {
                    "error":
                    "Please fill all contact details."
                }
            )

        # ------------------------------------------
        # EMAIL VALIDATION
        # ------------------------------------------

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        try:
            validate_email(email)
        except ValidationError:

            return render(
                request,
                "contact.html",
                {
                    "error":
                    "Please enter a valid email address."
                }
            )

        # ------------------------------------------
        # PHONE VALIDATION
        # ------------------------------------------

        if not phone.isdigit() or len(phone) != 10:

            return render(
                request,
                "contact.html",
                {
                    "error":
                    "Please enter a valid 10-digit phone number."
                }
            )

        # ------------------------------------------
        # MESSAGE LENGTH CHECK
        # ------------------------------------------

        if len(message) < 5:

            return render(
                request,
                "contact.html",
                {
                    "error":
                    "Message must be at least 5 characters."
                }
            )

        # ------------------------------------------
        # SAVE CONTACT MESSAGE
        # ------------------------------------------

        Contact.objects.create(
            Name=name,
            Email=email,
            Phone=phone,
            Message=message
        )

        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        return redirect(
            "contact"
        )

    return render(
        request,
        "contact.html"
    )


# ==================================================
# LOGIN
# ==================================================

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            "home"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # ------------------------------------------
        # REQUIRED FIELD CHECK
        # ------------------------------------------

        if not username or not password:

            return render(
                request,
                "login.html",
                {
                    "error":
                    "Please enter username and password."
                }
            )

        # ------------------------------------------
        # AUTHENTICATE USER
        # ------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "home"
            )

        return render(
            request,
            "login.html",
            {
                "error":
                "Invalid username or password."
            }
        )

    return render(
        request,
        "login.html"
    )


# ==================================================
# LOGOUT
# ==================================================

def logout_view(request):

    logout(request)

    return redirect(
        "home"
    )


# ==================================================
# SIGNUP
# SECURITY + VALIDATION
# ==================================================

def signup_view(request):

    if request.user.is_authenticated:

        return redirect(
            "home"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # ------------------------------------------
        # REQUIRED FIELD CHECK
        # ------------------------------------------

        if (
            not username
            or not email
            or not password
            or not confirm_password
        ):

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Please fill all fields."
                }
            )

        # ------------------------------------------
        # USERNAME LENGTH CHECK
        # ------------------------------------------

        if len(username) < 3:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Username must be at least 3 characters."
                }
            )

        # ------------------------------------------
        # PASSWORD LENGTH CHECK
        # ------------------------------------------

        if len(password) < 8:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Password must be at least 8 characters."
                }
            )

        # ------------------------------------------
        # PASSWORD MATCH CHECK
        # ------------------------------------------

        if password != confirm_password:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Passwords do not match."
                }
            )

        # ------------------------------------------
        # USERNAME CHECK
        # ------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Username already exists."
                }
            )

        # ------------------------------------------
        # EMAIL FORMAT CHECK
        # ------------------------------------------

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        try:
            validate_email(email)
        except ValidationError:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Please enter a valid email address."
                }
            )

        # ------------------------------------------
        # EMAIL CHECK
        # ------------------------------------------

        if User.objects.filter(
            email__iexact=email
        ).exists():

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Email already exists."
                }
            )

        # ------------------------------------------
        # PASSWORD STRENGTH CHECK
        # ------------------------------------------

        if password.isdigit():

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Password cannot contain only numbers."
                }
            )

        if password.lower() == password:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Password must contain at least one uppercase letter."
                }
            )

        if password.upper() == password:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Password must contain at least one lowercase letter."
                }
            )

        if not any(char.isdigit() for char in password):

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Password must contain at least one number."
                }
            )

        # ------------------------------------------
        # CREATE USER
        # ------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # ------------------------------------------
        # CREATE PROFILE
        # ------------------------------------------

        Profile.objects.get_or_create(
            user=user
        )

        # ------------------------------------------
        # LOGIN
        # ------------------------------------------

        login(
            request,
            user
        )

        return redirect(
            "home"
        )

    return render(
        request,
        "signup.html"
    )


# ==================================================
# MY PROFILE
# ==================================================

@login_required(login_url="login")
def profile(request):

    profile_obj, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "profile.html",
        {
            "user": request.user,
            "profile": profile_obj,
        }
    )


# ==================================================
# EDIT PROFILE
# ==================================================

@login_required(login_url="login")
def edit_profile(request):

    profile_obj, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        # ------------------------------------------
        # USERNAME CHECK
        # ------------------------------------------

        if username:

            if User.objects.filter(
                username=username
            ).exclude(
                id=request.user.id
            ).exists():

                return render(
                    request,
                    "edit_profile.html",
                    {
                        "profile": profile_obj,
                        "user": request.user,
                        "error":
                        "Username already exists."
                    }
                )

            request.user.username = username

        # ------------------------------------------
        # EMAIL
        # ------------------------------------------

        request.user.email = email

        request.user.save()

        # ------------------------------------------
        # PROFILE IMAGE
        # ------------------------------------------

        profile_image = request.FILES.get(
            "profile_image"
        )

        if profile_image:

            profile_obj.profile_image = profile_image

        profile_obj.save()

        # ------------------------------------------
        # GO TO PROFILE
        # ------------------------------------------

        return redirect(
            "profile"
        )

    # ----------------------------------------------
    # SHOW EDIT PROFILE
    # ----------------------------------------------

    return render(
        request,
        "edit_profile.html",
        {
            "profile": profile_obj,
            "user": request.user
        }
    )


# ==================================================
# MY ORDERS
# ==================================================

@login_required(login_url="login")
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items__product"
    ).order_by(
        "-date"
    )

    return render(
        request,
        "my_orders.html",
        {
            "orders": orders
        }
    )


# ==================================================
# ORDER DETAIL
# ==================================================

@login_required(login_url="login")
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    ).select_related(
        "product"
    )

    return render(
        request,
        "order_detail.html",
        {
            "order": order,
            "items": items
        }
    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@staff_member_required
def admin_dashboard(request):

    # TOTAL USERS
    total_users = User.objects.count()

    # TODAY'S REGISTRATIONS
    today = timezone.localdate()

    today_registrations = User.objects.filter(
        date_joined__date=today
    ).count()

    # TOTAL PRODUCTS
    total_products = Product.objects.count()

    # TOTAL CATEGORIES
    total_categories = Category.objects.count()

    # TOTAL ORDERS
    total_orders = Order.objects.count()

    # ORDER STATUS
    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()

    confirmed_orders = Order.objects.filter(
        status="Confirmed"
    ).count()

    shipped_orders = Order.objects.filter(
        status="Shipped"
    ).count()

    delivered_orders = Order.objects.filter(
        status="Delivered"
    ).count()

    cancelled_orders = Order.objects.filter(
        status="Cancelled"
    ).count()

    # TOTAL SALES
    total_sales = Order.objects.filter(
        status__in=[
            "Confirmed",
            "Shipped",
            "Delivered"
        ]
    ).aggregate(
        total=Sum("total")
    )["total"] or 0

    # RECENT ORDERS
    recent_orders = Order.objects.select_related(
        "user"
    ).order_by(
        "-date"
    )[:10]

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": total_users,
            "today_registrations": today_registrations,
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "total_sales": total_sales,
            "recent_orders": recent_orders,
        }
    )


# ==================================================
# OTP LOGIN
# ==================================================

def otp_login(request):

    if request.user.is_authenticated:

        return redirect(
            "home"
        )

    if request.method == "POST":

        mobile = request.POST.get(
            "mobile",
            ""
        ).strip()

        # ------------------------------------------
        # MOBILE CHECK
        # ------------------------------------------

        if not mobile:

            return render(
                request,
                "otp_login.html",
                {
                    "error":
                    "Please enter your mobile number."
                }
            )

        # ------------------------------------------
        # GENERATE 6 DIGIT OTP
        # ------------------------------------------

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        # ------------------------------------------
        # DELETE OLD OTP
        # ------------------------------------------

        OTPVerification.objects.filter(
            mobile=mobile
        ).delete()

        # ------------------------------------------
        # SAVE NEW OTP
        # ------------------------------------------

        OTPVerification.objects.create(
            mobile=mobile,
            otp=otp
        )

        # ------------------------------------------
        # DEMO OTP IN TERMINAL
        # ------------------------------------------

        print("================================")
        print("DEBAMART OTP")
        print("Mobile:", mobile)
        print("OTP:", otp)
        print("================================")

        # ------------------------------------------
        # OTP VERIFY PAGE
        # ------------------------------------------

        return redirect(
            f"/otp-verify/?mobile={mobile}"
        )

    return render(
        request,
        "otp_login.html"
    )


# ==================================================
# OTP VERIFY
# ==================================================

def otp_verify(request):

    if request.user.is_authenticated:

        return redirect(
            "home"
        )

    # ----------------------------------------------
    # GET MOBILE NUMBER
    # ----------------------------------------------

    mobile = request.POST.get(
        "mobile",
        ""
    ).strip()

    if not mobile:

        mobile = request.GET.get(
            "mobile",
            ""
        ).strip()

    # ----------------------------------------------
    # POST
    # ----------------------------------------------

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        # ------------------------------------------
        # FIND OTP
        # ------------------------------------------

        otp_record = OTPVerification.objects.filter(
            mobile=mobile
        ).order_by(
            "-created_at"
        ).first()

        # ------------------------------------------
        # OTP NOT FOUND
        # ------------------------------------------

        if not otp_record:

            return render(
                request,
                "otp_verify.html",
                {
                    "mobile": mobile,
                    "error":
                    "OTP not found. Please request a new OTP."
                }
            )

        # ------------------------------------------
        # OTP EXPIRY
        # ------------------------------------------

        expiry_time = (
            otp_record.created_at +
            timedelta(minutes=5)
        )

        if timezone.now() > expiry_time:

            otp_record.delete()

            return render(
                request,
                "otp_verify.html",
                {
                    "mobile": mobile,
                    "error":
                    "OTP expired. Please request a new OTP."
                }
            )

        # ------------------------------------------
        # CHECK OTP
        # ------------------------------------------

        if entered_otp != otp_record.otp:

            return render(
                request,
                "otp_verify.html",
                {
                    "mobile": mobile,
                    "error":
                    "Invalid OTP. Please try again."
                }
            )

        # ------------------------------------------
        # FIND USER
        # ------------------------------------------

        user = User.objects.filter(
            username=mobile
        ).first()

        # ------------------------------------------
        # CREATE USER
        # ------------------------------------------

        if not user:

            user = User.objects.create_user(
                username=mobile
            )

        # ------------------------------------------
        # CREATE PROFILE
        # ------------------------------------------

        Profile.objects.get_or_create(
            user=user
        )

        # ------------------------------------------
        # LOGIN USER
        # ------------------------------------------

        login(
            request,
            user
        )

        # ------------------------------------------
        # DELETE USED OTP
        # ------------------------------------------

        otp_record.delete()

        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        return redirect(
            "home"
        )

    # ----------------------------------------------
    # SHOW OTP PAGE
    # ----------------------------------------------

    return render(
        request,
        "otp_verify.html",
        {
            "mobile": mobile
        }
    )


# ==================================================
# WISHLIST
# ==================================================

@login_required(login_url="login")
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(
        "wishlist"
    )


# ==================================================
# REMOVE FROM WISHLIST
# ==================================================

@login_required(login_url="login")
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect(
        "wishlist"
    )


# ==================================================
# MY WISHLIST
# ==================================================

@login_required(login_url="login")
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "product",
        "product__category"
    ).order_by(
        "-date"
    )

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )