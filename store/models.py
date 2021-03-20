from django.contrib.auth.models import User
from django.db import models


# 1) Category
# 2) Product
# 3) CartProduct
# 4) Cart
# 5) Order
# 6) Feedback


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    picture = models.CharField(max_length=500)

    def __str__(self):
        return f'id({self.id}) {self.user}'


class UserRefreshToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='refresh', null=True)
    refresh = models.TextField(null=True)

    def __str__(self):
        return f'{self.user}'


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'id({self.id}) {self.name}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50, null=True)
    slug = models.SlugField(unique=True, null=True)
    image = models.ImageField(null=True, upload_to='images/')
    description = models.CharField(max_length=1000, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    reviewers = models.ManyToManyField(User, through='UserProductRelation')

    def __str__(self):
        return f'id({self.id}) {self.name}'


class UserProductRelation(models.Model):
    RATE_CHOICES = (
        (1, "Terribly"),
        (2, "Bad"),
        (3, "Fine"),
        (4, "Good"),
        (5, "Amazing"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    in_cart = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True, blank=True)
    is_rated = models.BooleanField(default=False, blank=True)

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


class CartProduct(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', on_delete=models.CASCADE,
                             related_name='UserCartProduct')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.product}'


class Cart(models.Model):
    owner = models.ForeignKey(User, verbose_name='Владелец', on_delete=models.CASCADE,
                              related_name='ownerCart', null=True)
    products = models.ManyToManyField(CartProduct, verbose_name='Товары', blank=True)
