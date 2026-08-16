from rest_framework.routers import DefaultRouter

from app.products.api.views import CategoryViewSet
from app.products.api.views import ProductViewSet

app_name = "api_products"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"", ProductViewSet, basename="product")

urlpatterns = router.urls
