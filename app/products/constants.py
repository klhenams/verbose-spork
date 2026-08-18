from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    DISCONTINUED = "discontinued", _("Discontinued")
    PENDING_PRICING = "pending_pricing", _("Pending Pricing")
    FAILED_PUBLISH = "failed_publish", _("Failed Publish")
