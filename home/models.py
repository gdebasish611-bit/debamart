from django.db import models
from django.contrib.auth.models import User


# =========================
# CONTACT
# =========================

class Contact(models.Model):

    Name = models.CharField(
        max_length=100
    )

    Email = models.EmailField()

    Phone = models.CharField(
        max_length=15
    )

    Message = models.TextField()

    date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return self.Name


# =========================
# CATEGORY
# =========================

class Category(models.Model):

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


# =========================
# PRODUCT
# =========================

class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    stock = models.IntegerField(
        default=0
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =========================
# CART
# =========================

class Cart(models.Model):

    # USER SECURITY
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(
        default=1
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.product.name} - {self.quantity}"


# =========================
# ORDER
# =========================

class Order(models.Model):

    # LOGGED-IN USER
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # PAYMENT METHOD
    payment_method = models.CharField(
        max_length=30,
        choices=[
            ("Cash on Delivery", "Cash on Delivery"),
            ("UPI", "UPI"),
            ("Debit / Credit Card", "Debit / Credit Card"),
        ],
        default="Cash on Delivery"
    )

    # ORDER STATUS
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Confirmed", "Confirmed"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


# =========================
# ORDER ITEM
# =========================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# =========================
# USER PROFILE
# =========================

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# =========================
# PRODUCT REVIEW
# =========================

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.PositiveIntegerField(
        default=5
    )

    comment = models.TextField()

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# =========================
# OTP VERIFICATION
# =========================

class OTPVerification(models.Model):

    mobile = models.CharField(
        max_length=15
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.mobile} - {self.otp}"


# =========================
# WISHLIST
# =========================

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"