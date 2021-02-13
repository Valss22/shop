from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter

from store.views import ProductsViewSet

router = SimpleRouter()
router.register(r'product', ProductsViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += router.urls
