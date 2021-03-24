from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter


from store.views import *

router = SimpleRouter()
router.register(r'product', ProductViewSet)
router.register(r'product/rate', UserProductRateView)
router.register(r'product/cart', UserProductCartView)
router.register(r'cart', CartViewSet)
urlpatterns = [
                  path('admin/', admin.site.urls),
                  # path to djoser end points
                  path('auth/', include('djoser.urls')),
                  path('auth/', include('djoser.urls.jwt')),
                  # path to google token
                  path('user/googlelogin/', GoogleView.as_view()),

                  path('user/refresh/', RefreshTokenView.as_view()),
                  path('user/logout/', LogoutView.as_view()),
                  path('product/cart/delete/<int:pk>/', CartObjView.as_view()),
                  path('product/cart/deleteBook/<int:pk>/', CartDelObjView.as_view())

                  # path to our account's app endpoints
                  # path('api/accounts/', include('accounts.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += router.urls
