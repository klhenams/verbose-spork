# Products App CRUD Documentation

## Overview

The Products app is a complete CRUD (Create, Read, Update, Delete) implementation with:
- **Pagination**: Configurable page size (default: 20 items per page)
- **Filtering**: Multiple filter options (name, SKU, category, status, price range, low stock)
- **Web Interface**: Django templates for browsing and managing products
- **REST API**: Full API with DRF (Django REST Framework)
- **Admin Interface**: Django admin with custom list filters and actions
- **Comprehensive Tests**: Unit tests for models, views, forms, and API endpoints

## Features

### Product Model
- Name and description
- SKU (unique stock keeping unit)
- Price and cost with automatic profit margin calculation
- Stock quantity with low stock threshold alerts
- Category relationship
- Status tracking (Active, Inactive, Discontinued)
- User tracking (created_by, updated_by)
- Timestamps (created_at, updated_at)

### Category Model
- Name and description
- Product count tracking
- Automatic timestamping

## Installation & Setup

### 1. Create Migrations

```bash
python manage.py makemigrations products
python manage.py migrate products
```

### 2. Create a Superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 3. Access Admin Interface

Visit http://localhost:8000/admin/ and log in with your superuser credentials.

## Web Interface Usage

### Product List
- **URL**: `/products/`
- **Features**:
  - Paginated list (20 items per page)
  - Search by name or SKU
  - Filter by category
  - Filter by status
  - Filter by price range
  - Sort options

### Product Detail
- **URL**: `/products/<id>/`
- **Features**:
  - Full product information
  - Profit margin calculation
  - Stock status indicator
  - User tracking information
  - Quick action buttons

### Create Product
- **URL**: `/products/create/`
- **Features**:
  - Form validation
  - Auto-calculation of profit margin
  - Success messages

### Edit Product
- **URL**: `/products/<id>/edit/`
- **Features**:
  - Update all product fields
  - Automatic updated_by tracking

### Delete Product
- **URL**: `/products/<id>/delete/`
- **Features**:
  - Confirmation dialog
  - Prevents accidental deletion

## REST API Usage

### Base URL
```
/api/products/
```

### Endpoints

#### Products

**List Products**
```
GET /api/products/products/
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `name`: Filter by name (contains search)
- `sku`: Filter by SKU (contains search)
- `category`: Filter by category ID
- `status`: Filter by status (active, inactive, discontinued)
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `is_low_stock`: Filter by low stock (true/false)

Example:
```
GET /api/products/products/?page=1&page_size=20&status=active&min_price=10&max_price=100
```

**Retrieve Product**
```
GET /api/products/products/{id}/
```

**Create Product**
```
POST /api/products/products/
Content-Type: application/json

{
    "name": "Laptop",
    "description": "High-performance laptop",
    "sku": "LAPTOP-001",
    "price": "999.99",
    "cost": "600.00",
    "stock_quantity": 50,
    "low_stock_threshold": 10,
    "category": 1,
    "status": "active"
}
```

**Update Product**
```
PATCH /api/products/products/{id}/
Content-Type: application/json

{
    "name": "Updated Name",
    "price": "1099.99"
}
```

**Delete Product**
```
DELETE /api/products/products/{id}/
```

#### Categories

**List Categories**
```
GET /api/products/categories/
```

Query Parameters:
- `page`: Page number
- `page_size`: Items per page
- `name`: Filter by name

**Retrieve Category**
```
GET /api/products/categories/{id}/
```

**Create Category**
```
POST /api/products/categories/
Content-Type: application/json

{
    "name": "Electronics",
    "description": "Electronic devices"
}
```

**Update Category**
```
PATCH /api/products/categories/{id}/
```

**Delete Category**
```
DELETE /api/products/categories/{id}/
```

## Authentication

All API endpoints require authentication. Use one of these methods:

### Token Authentication
1. Obtain token:
```
POST /api/auth-token/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

2. Use token in requests:
```
Authorization: Token <your-token>
```

### Session Authentication
Use the standard Django login at `/accounts/login/`

## Testing

### Run All Tests
```bash
pytest app/products/tests/
```

### Run Specific Test
```bash
pytest app/products/tests/test_models.py::TestProduct::test_is_low_stock
```

### Run Tests with Coverage
```bash
pytest --cov=app.products app/products/tests/
```

### Run Tests in Verbose Mode
```bash
pytest -v app/products/tests/
```

## Admin Features

### Product Admin
- List view with filters:
  - By status
  - By category
  - By creation date
  - By low stock status
- Search by name, SKU, or description
- Profit margin display
- Low stock indicator
- Batch editing support

### Category Admin
- Product count display
- Search support
- Readonly timestamps

## API Response Examples

### List Products Response
```json
{
    "count": 150,
    "next": "http://api.example.com/products/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Laptop",
            "sku": "LAPTOP-001",
            "price": "999.99",
            "stock_quantity": 50,
            "category_name": "Electronics",
            "status": "active",
            "is_low_stock": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Product Detail Response
```json
{
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "sku": "LAPTOP-001",
    "price": "999.99",
    "cost": "600.00",
    "profit_margin": "66.67",
    "stock_quantity": 50,
    "low_stock_threshold": 10,
    "is_low_stock": false,
    "category": 1,
    "category_name": "Electronics",
    "status": "active",
    "created_by": 1,
    "created_by_name": "Admin User",
    "updated_by": 1,
    "updated_by_name": "Admin User",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

## Troubleshooting

### Products Not Showing
1. Ensure you're logged in
2. Check product status is set to "active"
3. Verify page number is valid

### API Returns 401 Unauthorized
1. Ensure you're authenticated
2. Check your token is valid
3. Verify token is passed in Authorization header

### Low Stock Not Working
1. Check `stock_quantity` is below `low_stock_threshold`
2. Run migrations if just created

## File Structure

```
app/products/
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
├── api/
│   ├── __init__.py
│   ├── serializers.py      # API serializers
│   ├── views.py            # API viewsets
│   └── urls.py             # API routes
├── tests/
│   ├── __init__.py         # Factories
│   ├── test_models.py      # Model tests
│   ├── test_forms.py       # Form tests
│   ├── test_views.py       # View tests
│   └── test_api.py         # API tests
├── __init__.py
├── admin.py                # Django admin config
├── apps.py                 # App config
├── conftest.py             # Pytest config
├── forms.py                # HTML forms
├── models.py               # Data models
├── urls.py                 # Web routes
├── views.py                # Web views
└── README.md               # This file
```

## Performance Considerations

### Database Indexes
Products are indexed on:
- SKU (unique)
- Status
- Category
- Creation date (for sorting)

### Query Optimization
- Uses `select_related()` for foreign keys
- Uses `prefetch_related()` where appropriate
- API uses lightweight serializers for list views

### Pagination
- Default: 20 items per page
- Maximum: 100 items per page
- Configurable via `page_size` query parameter
