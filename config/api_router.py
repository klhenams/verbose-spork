from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from app.products.api.views import CategoryViewSet
from app.products.api.views import ProductViewSet
from app.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("products/products", ProductViewSet, basename="product")
router.register("products/categories", CategoryViewSet, basename="category")


app_name = "api"
urlpatterns = router.urls
