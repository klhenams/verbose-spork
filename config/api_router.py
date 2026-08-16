from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from app.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path("products/", include("app.products.api.urls", namespace="api_products")),
]
