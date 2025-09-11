# Hardware Delivery Backend API

This is the backend API for a hardware delivery application where businesses can purchase industrial products like machines, aluminium, tools, and more.

## Features

- **Business User Management**: Registration, login, and OTP verification
- **Product Catalog**: Categories, brands, product types, and detailed products
- **Home Page**: Categories, brands, and promotional banners
- **Product Search**: Search products by name or description
- **Product Filtering**: Filter by category, brand, or product type

## API Endpoints

### Authentication APIs

#### 1. Register Business User
- **URL**: `POST /v1/hardware/register/`
- **Description**: Register a new business user
- **Request Body**:
```json
{
    "business_type": "manufacturing",
    "business_name": "ABC Manufacturing Ltd",
    "phone_number": "+1234567890",
    "business_location": "123 Industrial Ave, City",
    "tin_number": "TIN123456789",
    "password": "securepassword123"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Registration successful. Please verify your phone number with the OTP sent.",
    "user_id": "uuid-here",
    "phone_number": "+1234567890"
}
```

#### 2. Login Business User
- **URL**: `POST /v1/hardware/login/`
- **Description**: Login with phone number and password
- **Request Body**:
```json
{
    "phone_number": "+1234567890",
    "password": "securepassword123"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "user_id": "uuid-here",
        "business_type": "manufacturing",
        "business_name": "ABC Manufacturing Ltd",
        "phone_number": "+1234567890",
        "business_location": "123 Industrial Ave, City",
        "tin_number": "TIN123456789",
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 3. Verify OTP
- **URL**: `POST /v1/hardware/verify-otp/`
- **Description**: Verify phone number with OTP
- **Request Body**:
```json
{
    "phone_number": "+1234567890",
    "otp": "123456"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Phone number verified successfully",
    "user": {
        "user_id": "uuid-here",
        "business_type": "manufacturing",
        "business_name": "ABC Manufacturing Ltd",
        "phone_number": "+1234567890",
        "business_location": "123 Industrial Ave, City",
        "tin_number": "TIN123456789",
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 4. Resend OTP
- **URL**: `POST /v1/hardware/resend-otp/`
- **Description**: Resend OTP to phone number
- **Request Body**:
```json
{
    "phone_number": "+1234567890"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "OTP sent successfully"
}
```

#### 5. Get User Data
- **URL**: `POST /v1/hardware/user-data/`
- **Description**: Get all data for a specific user. This can be called on the splash screen.
- **Request Body**:
```json
{
    "user_id": "uuid-here"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "User data fetched successfully",
    "user": {
        "user_id": "uuid-here",
        "business_type": "manufacturing",
        "business_name": "ABC Manufacturing Ltd",
        "phone_number": "+1234567890",
        "business_location": "123 Industrial Ave, City",
        "tin_number": "TIN123456789",
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### Home Page APIs

#### 6. Get Home Page Data
- **URL**: `GET /v1/hardware/home/`
- **Description**: Get categories, brands, and banners for home page
- **Response**:
```json
{
    "success": true,
    "data": {
        "categories": [
            {
                "category_id": "uuid-here",
                "name": "Machines",
                "description": "Industrial and construction machines",
                "image": "https://example.com/images/machines.jpg",
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "brands": [
            {
                "brand_id": "uuid-here",
                "name": "Caterpillar",
                "description": "Heavy machinery and construction equipment",
                "logo": "https://example.com/logos/caterpillar.png",
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "banners": [
            {
                "banner_id": "uuid-here",
                "title": "New Excavators Arrival",
                "description": "Latest models from Caterpillar and Komatsu",
                "image": "https://example.com/banners/excavators-banner.jpg",
                "link_url": "/products/category/machines",
                "is_active": true,
                "order": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
}
```

#### 7. Get Personalized Home Page Data
- **URL**: `POST /v1/hardware/home-with-user/`
- **Description**: Get personalized home page data with user context
- **Request Body**:
```json
{
    "user_id": "uuid-here"
}
```
- **Response**:
```json
{
    "success": true,
    "data": {
        "categories": [...],
        "brands": [...],
        "banners": [...],
        "user": {
            "user_id": "uuid-here",
            "business_type": "manufacturing",
            "business_name": "ABC Manufacturing Ltd",
            "phone_number": "+1234567890",
            "business_location": "123 Industrial Ave, City",
            "tin_number": "TIN123456789",
            "is_verified": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
}
```

### Products APIs

#### 8. Get Products Page Data
- **URL**: `GET /v1/hardware/products/`
- **Description**: Get all product types with their products
- **Response**:
```json
{
    "success": true,
    "data": {
        "product_types": [
            {
                "type_id": "uuid-here",
                "name": "Excavators",
                "category_name": "Machines",
                "description": "Excavators for machines",
                "is_active": true,
                "products": [
                    {
                        "product_id": "uuid-here",
                        "name": "CAT 320 Excavator",
                        "description": "Heavy-duty hydraulic excavator for construction and mining",
                        "price": "150000.00",
                        "image": "https://example.com/products/cat320.jpg",
                        "category": "uuid-here",
                        "category_name": "Machines",
                        "brand": "uuid-here",
                        "brand_name": "Caterpillar",
                        "product_type": "uuid-here",
                        "product_type_name": "Excavators",
                        "subtype": "Hydraulic",
                        "size": "20 ton",
                        "color": null,
                        "material": null,
                        "weight": "20000.00",
                        "dimensions": "8.5m x 2.8m x 2.9m",
                        "is_active": true,
                        "is_featured": false,
                        "stock_quantity": 5,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        ]
    }
}
```

#### 9. Get Personalized Products Page Data
- **URL**: `POST /v1/hardware/products-with-user/`
- **Description**: Get personalized products page data with user context and filtering options
- **Request Body**:
```json
{
    "user_id": "uuid-here",
    "category_id": "uuid-here",
    "brand_id": "uuid-here"
}
```
- **Response**:
```json
{
    "success": true,
    "data": {
        "product_types": [
            {
                "type_id": "uuid-here",
                "name": "Excavators",
                "category_name": "Machines",
                "description": "Excavators for machines",
                "is_active": true,
                "products": [...]
            }
        ],
        "user": {
            "user_id": "uuid-here",
            "business_type": "manufacturing",
            "business_name": "ABC Manufacturing Ltd",
            "phone_number": "+1234567890",
            "business_location": "123 Industrial Ave, City",
            "tin_number": "TIN123456789",
            "is_verified": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
}
```

#### 10. Get Products by Category
- **URL**: `GET /v1/hardware/products/category/{category_id}/`
- **Description**: Get products filtered by category
- **Response**: Same as product detail structure

#### 11. Get Products by Brand
- **URL**: `GET /v1/hardware/products/brand/{brand_id}/`
- **Description**: Get products filtered by brand
- **Response**: Same as product detail structure

#### 12. Get Product Detail
- **URL**: `GET /v1/hardware/products/{product_id}/`
- **Description**: Get detailed information about a specific product
- **Response**:
```json
{
    "success": true,
    "data": {
        "product": {
            "product_id": "uuid-here",
            "name": "CAT 320 Excavator",
            "description": "Heavy-duty hydraulic excavator for construction and mining",
            "price": "150000.00",
            "image": "https://example.com/products/cat320.jpg",
            "category": "uuid-here",
            "category_name": "Machines",
            "brand": "uuid-here",
            "brand_name": "Caterpillar",
            "product_type": "uuid-here",
            "product_type_name": "Excavators",
            "subtype": "Hydraulic",
            "size": "20 ton",
            "color": null,
            "material": null,
            "weight": "20000.00",
            "dimensions": "8.5m x 2.8m x 2.9m",
            "is_active": true,
            "is_featured": false,
            "stock_quantity": 5,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
}
```

#### 13. Search Products
- **URL**: `GET /v1/hardware/products/search/?q=excavator`
- **Description**: Search products by name or description
- **Response**:
```json
{
    "success": true,
    "data": {
        "products": [...],
        "query": "excavator",
        "count": 2
    }
}
```

## Data Models

### BusinessUser
- Custom user model for business users
- Fields: business_type, business_name, phone_number, business_location, tin_number, is_verified

### ProductCategory
- Product categories like Machines, Aluminium, Tools, etc.
- Fields: name, description, image, is_active

### Brand
- Product brands like Caterpillar, Komatsu, Alcoa, etc.
- Fields: name, description, logo, is_active

### ProductType
- Product types within categories (e.g., Excavators under Machines)
- Fields: name, category (FK), description, is_active

### Product
- Individual products with detailed specifications
- Fields: name, description, price, image, category, brand, product_type, specifications (size, color, material, weight, dimensions), stock_quantity

### Banner
- Promotional banners for home page
- Fields: title, description, image, link_url, is_active, order

### HardwareOTP
- OTP storage for phone verification
- Fields: phone_number, otp, is_used, created_at

## Setup Instructions

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run Migrations**:
```bash
python manage.py makemigrations hardware_backend
python manage.py migrate
```

3. **Create Superuser**:
```bash
python manage.py createsuperuser
```

4. **Populate Sample Data**:
```bash
python manage.py populate_sample_data
```

5. **Run Development Server**:
```bash
python manage.py runserver
```

## Business Types

Available business types for registration:
- manufacturing
- construction
- retail
- wholesale
- service
- other

## OTP System

- OTPs are 4-digit numeric codes
- OTPs expire after 15 minutes
- OTPs can only be used once
- Currently uses mock SMS service (print to console)
- In production, integrate with SMS service like Twilio or AfricasTalking

## Error Responses

All APIs return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error details"]
    }
}
```

## Security Features

- Password hashing using Django's built-in hashers
- Phone number and TIN number uniqueness validation
- OTP expiration and single-use validation
- User verification requirement for login

## Future Enhancements

- JWT token authentication
- Order management system
- Payment integration
- Real SMS service integration
- Image upload functionality
- Product reviews and ratings
- Inventory management
- Delivery tracking