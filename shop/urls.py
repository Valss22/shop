from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from store.views import ProductsViewSet, GoogleView, RefreshTokenView, LogoutView

router = SimpleRouter()
router.register(r'product', ProductsViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    # path to djoser end points
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    #path to google token
    path('user/googlelogin/', GoogleView.as_view(), name='token_obtain_pair'),

    path('user/refresh/', RefreshTokenView.as_view()),
    path('user/logout/', LogoutView.as_view())

    #path to our account's app endpoints
    #path('api/accounts/', include('accounts.urls'))
]

urlpatterns += router.urls
