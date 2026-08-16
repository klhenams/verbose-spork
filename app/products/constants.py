from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    DISCONTINUED = "discontinued", _("Discontinued")
