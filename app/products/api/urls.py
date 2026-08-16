from rest_framework.routers import DefaultRouter

from app.products.api.views import CategoryViewSet
from app.products.api.views import ProductViewSet

app_name = "api_products"

router = DefaultRouter()
router.register(r"", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
