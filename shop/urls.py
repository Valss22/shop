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
router.register(r'product/cart/delete', CartObjView)
router.register(r'cart', CartViewSet)
router.register(r'discount', DiscountProductViewSet)
# router.register(r'feedback/form', FeedbackFormView)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  # path to djoser end points
                  path('auth/', include('djoser.urls')),
                  path('auth/', include('djoser.urls.jwt')),
                  # path to google token
                  path('user/googlelogin/', GoogleView.as_view()),
                  path('user/refresh/', RefreshTokenView.as_view()),
                  path('user/logout/', LogoutView.as_view()),
                  path('product/cart/deleteBook/<int:pk>/', CartDelObjView.as_view()),
                  path('product/comment/rate/<int:pk>/', FeedbackRateCommentView.as_view()),
                  # path('product/comment/dislike/<int:pk>/', FeedbackDislikeView.as_view()),
                  path('feedback/form/<int:pk>/', FeedbackFormView.as_view()),
                  # path('cart/', CartViewSet.as_view()),
                  path('product/cart/deleteCart/<int:pk>/', CartDeleteView.as_view()),

                  # path to our account's app endpoints
                  # path('api/accounts/', include('accounts.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += router.urls

# from django.conf import settings
# from django.urls import include, path
#
# if settings.DEBUG:
#     import debug_toolbar
#
#     urlpatterns = [
#
#                       path('__debug__/', include(debug_toolbar.urls)),
#                   ] + urlpatterns
