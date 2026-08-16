# Product Fixtures Guide

## Overview

This directory contains Django fixtures for loading initial product and category data into your database. The `initial_products.json` fixture includes 24 products across 5 categories.

## What's Included

### Categories (5 total)
1. **Electronics** - Computers, accessories, and gadgets
2. **Books** - Software development and reference books
3. **Home & Garden** - Furniture and home supplies
4. **Sports & Outdoors** - Sports equipment and outdoor gear
5. **Clothing** - Apparel and footwear

### Products (24 total)

#### Electronics (5 products)
- MacBook Pro 14-inch ($1,999.99)
- Dell XPS 13 Laptop ($1,299.99)
- Wireless Bluetooth Headphones ($299.99)
- USB-C Fast Charging Cable ($19.99)
- 4K Webcam Pro ($149.99)
- Mechanical Keyboard RGB ($179.99)
- Wireless Mouse ($49.99)
- iPad Air Refurbished ($449.99)
- Screen Protector Tempered Glass ($12.99)

#### Books (3 products)
- Clean Code ($49.99)
- The Pragmatic Programmer ($54.99)
- Design Patterns ($59.99)

#### Home & Garden (4 products)
- Ergonomic Office Chair ($399.99)
- Standing Desk with Electric Height Adjustment ($599.99)
- LED Desk Lamp with USB Charging ($79.99)
- Indoor Plant Potting Set ($39.99)

#### Sports & Outdoors (7 products)
- Yoga Mat with Carrying Strap ($49.99)
- Adjustable Dumbbells Set ($299.99)
- Waterproof Bluetooth Portable Speaker ($89.99)
- Hiking Backpack 50L ($159.99)
- Stainless Steel Water Bottle 32oz ($34.99)

#### Clothing (3 products)
- Premium Cotton T-Shirt Pack ($49.99)
- Leather Work Boots ($129.99)
- Winter Wool Sweater ($89.99)

## Loading Fixtures

### Method 1: Using Custom Management Command (Recommended)

```bash
# Load the initial products fixture
python manage.py load_product_fixtures

# Or with Docker
docker compose -f docker-compose.local.yml run --rm django python manage.py load_product_fixtures
```

### Method 2: Using Django's Standard loaddata Command

```bash
# Load the specific fixture
python manage.py loaddata products/initial_products

# Or with Docker
docker compose -f docker-compose.local.yml run --rm django python manage.py loaddata products/initial_products
```

### Method 3: Load All Fixtures in Directory

```bash
# Load all fixtures from the products app
python manage.py loaddata products/*
```

## Pre-requisites

Before loading fixtures, ensure:

1. **Database is migrated**:
   ```bash
   python manage.py migrate
   ```

2. **User exists** (for `created_by` and `updated_by` fields):
   - Fixtures use `created_by: 1` (admin/superuser)
   - Create a superuser if needed:
   ```bash
   python manage.py createsuperuser
   ```

## Fixture Details

### Stock Levels
- High stock: 85-300 units (common items)
- Medium stock: 25-60 units (popular items)
- Low stock: 2-15 units (premium items)

### Pricing Strategy
- **Electronics**: $12.99 - $1,999.99
- **Books**: $49.99 - $59.99
- **Home & Garden**: $39.99 - $599.99
- **Sports & Outdoors**: $34.99 - $299.99
- **Clothing**: $49.99 - $129.99

### Profit Margins
- All products have realistic cost and profit margins
- Markup ranges from ~100% to ~1000% depending on category

### Stock Alerts
- Low stock thresholds set appropriately for each category
- Examples:
  - Low-value items (cables): 20-50 threshold
  - High-value items (desks): 2-5 threshold
  - Clothing: 25-30 threshold

## Verifying Fixtures Loaded

### Via Django Admin
1. Visit http://localhost:8000/admin/
2. Go to Products → Categories (should show 5)
3. Go to Products → Products (should show 24)

### Via API
```bash
# List categories
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/categories/

# List products
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/products/
```

### Via Django Shell
```bash
python manage.py shell

# Check categories
from app.products.models import Category
Category.objects.count()  # Should return 5

# Check products
from app.products.models import Product
Product.objects.count()  # Should return 24

# Check stock levels
Product.objects.filter(status='active').count()  # All 24 are active
```

## Resetting Fixtures

To reload fixtures (WARNING: This will replace existing data):

```bash
# Delete all products and categories
python manage.py shell
>>> from app.products.models import Product, Category
>>> Product.objects.all().delete()
>>> Category.objects.all().delete()

# Then reload
python manage.py load_product_fixtures
```

Or use a single command:
```bash
python manage.py flush --no-input && python manage.py migrate && python manage.py load_product_fixtures
```

## Creating Custom Fixtures

To export current data as a fixture:

```bash
python manage.py dumpdata products > app/products/fixtures/my_custom_products.json
```

To load your custom fixture:

```bash
python manage.py load_product_fixtures --fixture my_custom_products
```

## Testing with Fixtures

### Pytest with Auto-use Fixture

Create a conftest.py in your tests:

```python
import pytest

@pytest.fixture(scope='session')
def load_products_fixture(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('load_product_fixtures')
```

### Running Tests with Fixtures

```bash
pytest --fixtures  # Shows available fixtures
pytest app/products/tests/ -v
```

## Troubleshooting

### "No fixture found" error
- Ensure you're running the command from the project root
- Check that `app/products/fixtures/initial_products.json` exists

### "User with id 1 does not exist" error
- Create a superuser first: `python manage.py createsuperuser`
- Edit the fixture to use a different user ID if needed

### Duplicate key error
- Run `python manage.py flush` to clear the database
- Then reload the fixtures

### SKU conflicts
- SKUs must be unique
- Either flush the database or edit SKU values in the fixture

## Fixture Format

The fixture uses Django's JSON format:

```json
{
  "model": "app_label.model_name",
  "pk": 1,
  "fields": {
    "field_name": "value"
  }
}
```

For more details, see:
- [Django Fixtures Documentation](https://docs.djangoproject.com/en/stable/howto/initial-data-via-fixtures/)
- [Providing initial data with fixtures](https://docs.djangoproject.com/en/stable/ref/django-admin/#loaddata)
