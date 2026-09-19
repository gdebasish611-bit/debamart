from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        "",
        views.index,
        name="home"
    ),


    # =========================
    # CATEGORIES
    # =========================

    path(
        "categories/",
        views.categories,
        name="categories"
    ),


    # =========================
    # PRODUCTS
    # =========================

    path(
        "products/",
        views.products,
        name="products"
    ),


    # =========================
    # PRODUCT DETAIL
    # =========================

    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),


    # =========================
    # ADD REVIEW
    # =========================

    path(
        "product/<int:product_id>/review/",
        views.add_review,
        name="add_review"
    ),


    # =========================
    # ADD TO CART
    # =========================

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),


    # =========================
    # CART PAGE
    # =========================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),


    # =========================
    # INCREASE QUANTITY
    # =========================

    path(
        "cart/increase/<int:cart_id>/",
        views.increase_cart,
        name="increase_cart"
    ),


    # =========================
    # DECREASE QUANTITY
    # =========================

    path(
        "cart/decrease/<int:cart_id>/",
        views.decrease_cart,
        name="decrease_cart"
    ),


    # =========================
    # REMOVE FROM CART
    # =========================

    path(
        "cart/remove/<int:cart_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),


    # =========================
    # CHECKOUT
    # =========================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),


    # =========================
    # PAYMENT
    # =========================

    path(
        "payment/<int:order_id>/",
        views.payment,
        name="payment"
    ),


    # =========================
    # ORDER SUCCESS
    # =========================

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),


    # =========================
    # ABOUT
    # =========================

    path(
        "about/",
        views.about,
        name="about"
    ),


    # =========================
    # CONTACT
    # =========================

    path(
        "contact/",
        views.contact,
        name="contact"
    ),


    # =========================
    # MY ORDERS
    # =========================

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),


    # =========================
    # ORDER DETAILS
    # =========================

    path(
        "order/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),


    # =========================
    # LOGIN
    # =========================

    path(
        "login/",
        views.login_view,
        name="login"
    ),


    # =========================
    # LOGOUT
    # =========================

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =========================
    # SIGNUP
    # =========================

    path(
        "signup/",
        views.signup_view,
        name="signup"
    ),


    # =========================
    # MY PROFILE
    # =========================

    path(
        "profile/",
        views.profile,
        name="profile"
    ),


    # =========================
    # EDIT PROFILE
    # =========================

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),


    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        "dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # =========================
    # OTP LOGIN
    # =========================

    path(
        "otp-login/",
        views.otp_login,
        name="otp_login"
    ),


    # =========================
    # OTP VERIFY
    # =========================

    path(
        "otp-verify/",
        views.otp_verify,
        name="otp_verify"
    ),


    # =========================
    # WISHLIST
    # =========================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),


    # =========================
    # ADD TO WISHLIST
    # =========================

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),


    # =========================
    # REMOVE FROM WISHLIST
    # =========================

    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

]