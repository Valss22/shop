from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from store.validators import *


class UserRefreshToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='refresh', null=True)
    refresh = models.TextField(null=True)

    def __str__(self):
        return f'{self.user}'


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')

    def __str__(self):
        return f'id({self.id}) {self.name}'


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=255, null=True)
    username = models.CharField(max_length=50, null=True)
    date = models.DateField(default=datetime.now())

    def __str__(self):
        return f'{self.username}({self.id})'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50, null=True)
    image = models.TextField(null=True, max_length=500)
    description = models.TextField(null=True, max_length=500)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    reviewers = models.ManyToManyField(User, through='UserProductRelation')
    comments = models.ManyToManyField(Feedback, null=True, blank=True)
    sale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                               validators=[validate_percent_field])
    discountPrice = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'id({self.id}) {self.name}'


class FeedbackRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Feedback, on_delete=models.CASCADE, null=True)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} {self.comment}'


class CartProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    copy_count = models.IntegerField(default=0)
    copyPrice = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    copyDiscountPrice = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.user} {self.product}'


class UserProductRelation(models.Model):
    RATE_CHOICES = (
        (1, "Terribly"),
        (2, "Bad"),
        (3, "Fine"),
        (4, "Good"),
        (5, "Amazing"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True, blank=True)
    is_rated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        from store.services import set_rating

        creating = not self.pk
        old_rating = self.rate

        super().save(*args, **kwargs)

        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.product)

    def __str__(self):
        return f' {self.user.username}: {self.product.name}, RATE {self.rate}'


class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct)

    def __str__(self):
        return f'{self.owner}({self.owner_id})'


class UserPhotoProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    picture = models.TextField(max_length=500, null=True)

    # orderData = models.ManyToManyField(UserOrderData)

    def __str__(self):
        return f'id({self.id}) {self.user}'


class CopyProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    copyCount = models.IntegerField(null=True)
    copyPrice = models.DecimalField(max_digits=5, decimal_places=2, null=True)


class OrderProduct(models.Model):
    STATUS_CHOICES = (
        (1, 'Order processing'),
        (2, 'Order is formed'),
        (3, 'Order for delivery'),
        (4, 'Order was sent to the post office')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(CopyProduct)
    totalCount = models.IntegerField(null=True)
    totalPrice = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    date = models.DateField(default=datetime.now())
    status = models.IntegerField(choices=STATUS_CHOICES, null=True)

    def __str__(self):
        return f'{self.user} ({self.id})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True)
    postalCode = models.CharField(max_length=6, null=True)
    orderItems = models.ManyToManyField(OrderProduct)

    def __str__(self):
        return f'{self.user} {self.email}({self.id})'