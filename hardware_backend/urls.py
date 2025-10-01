from django.urls import path
from . import views

urlpatterns = [
    # User Authentication & Data APIs
    path('register/', views.register_business_user, name='register_business_user'),
    path('login/', views.login_business_user, name='login_business_user'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('user-data/', views.get_business_user_data, name='get_business_user_data'),
    path('users/<str:user_id>/update-profile/', views.update_user_profile, name='update_user_profile'),
    path('users/<str:user_id>/update-password/', views.update_user_password, name='update_user_password'),

    # Home Page APIs
    path('home/', views.home_page, name='home_page'),
    path('home-with-user/', views.home_page_with_user, name='home_page_with_user'),
    
    # Products APIs
    path('products/', views.products_page, name='products_page'),
    path('products-with-user/', views.products_page_with_user, name='products_page_with_user'),
    path('products/search/', views.search_products, name='search_products'),
    path('products/category/<str:category_id>/', views.products_by_category, name='products_by_category'),
    path('products/brand/<str:brand_id>/', views.products_by_brand, name='products_by_brand'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    
    # Product Types APIs (for frontend)
    path('product-types/', views.admin_get_all_product_types, name='get_all_product_types'),

    # Admin Management APIs
    # Products
    path('admin/products/', views.admin_get_all_products, name='admin_get_all_products'),
    path('admin/products/create/', views.admin_create_product, name='admin_create_product'),
    path('admin/products/<str:product_id>/', views.admin_update_product, name='admin_update_product'),
    path('admin/products/<str:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('admin/products/<str:product_id>/toggle-status/', views.admin_toggle_product_status, name='admin_toggle_product_status'),
    
    # Categories
    path('admin/categories/', views.admin_get_all_categories, name='admin_get_all_categories'),
    path('admin/categories/create/', views.admin_create_category, name='admin_create_category'),
    path('admin/categories/<str:category_id>/', views.admin_update_category, name='admin_update_category'),
    path('admin/categories/<str:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/categories/<str:category_id>/toggle-status/', views.admin_toggle_category_status, name='admin_toggle_category_status'),
    
    # Brands
    path('admin/brands/', views.admin_get_all_brands, name='admin_get_all_brands'),
    path('admin/brands/create/', views.admin_create_brand, name='admin_create_brand'),
    path('admin/brands/<str:brand_id>/', views.admin_update_brand, name='admin_update_brand'),
    path('admin/brands/<str:brand_id>/delete/', views.admin_delete_brand, name='admin_delete_brand'),
    path('admin/brands/<str:brand_id>/toggle-status/', views.admin_toggle_brand_status, name='admin_toggle_brand_status'),
    
    # Product Types
    path('admin/product-types/', views.admin_get_all_product_types, name='admin_get_all_product_types'),
    path('admin/product-types/create/', views.admin_create_product_type, name='admin_create_product_type'),
    path('admin/product-types/<str:product_type_id>/', views.admin_update_product_type, name='admin_update_product_type'),
    path('admin/product-types/<str:product_type_id>/delete/', views.admin_delete_product_type, name='admin_delete_product_type'),
    path('admin/product-types/<str:product_type_id>/toggle-status/', views.admin_toggle_product_type_status, name='admin_toggle_product_type_status'),
    
    # Product Type detail (for frontend)
    path('product-types/<str:product_type_id>/', views.admin_update_product_type, name='get_product_type'),
    
    # Banners
    path('admin/banners/', views.admin_get_all_banners, name='admin_get_all_banners'),
    path('admin/banners/create/', views.admin_create_banner, name='admin_create_banner'),
    path('admin/banners/<str:banner_id>/', views.admin_update_banner, name='admin_update_banner'),
    path('admin/banners/<str:banner_id>/delete/', views.admin_delete_banner, name='admin_delete_banner'),
    path('admin/banners/<str:banner_id>/toggle-status/', views.admin_toggle_banner_status, name='admin_toggle_banner_status'),

    # User Admin APIs
    path('admin/users/', views.admin_get_all_users, name='admin_get_all_users'),
    path('admin/users/<str:user_id>/toggle-verification/', views.admin_toggle_user_verification, name='admin_toggle_user_verification'),
    path('admin/users/<str:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    
    # Order Management APIs
    path('orders/', views.create_order, name='create_order'),
    path('orders/user/<str:user_id>/', views.get_user_orders, name='get_user_orders'),
    path('orders/<str:order_id>/', views.get_order_details, name='get_order_details'),
    path('orders/<str:order_id>/details/', views.get_order_details_new_format, name='get_order_details_new_format'),
    path('orders/<str:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<str:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<str:order_id>/delete/', views.delete_order, name='delete_order'),
    
    # Admin Order Management APIs
    path('admin/orders/', views.admin_get_all_orders, name='admin_get_all_orders'),
    path('admin/orders/status/<str:status>/', views.admin_get_orders_by_status, name='admin_get_orders_by_status'),
    
    # Sales Management APIs
    path('customers/', views.get_customers, name='get_customers'),
    path('customers/search/', views.search_customers, name='search_customers'),
    path('customers/create/', views.create_customer, name='create_customer'),
    
    # Shelf Management APIs
    path('shelves/', views.get_shelves, name='get_shelves'),
    path('shelves/create/', views.create_shelf, name='create_shelf'),
    
    # Products with Locations
    path('products-with-locations/', views.get_products_with_locations, name='get_products_with_locations'),
    
    # Sales APIs
    path('sales/', views.get_sales, name='get_sales'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/salesperson/<str:salesperson_id>/', views.get_sales_by_salesperson, name='get_sales_by_salesperson'),
    path('sales/<str:sale_id>/update-payment/', views.update_sale_payment_status, name='update_sale_payment_status'),
    
    # Inventory Alerts
    path('alerts/low-stock/', views.get_low_stock_products, name='get_low_stock_products'),
    path('alerts/expiring/', views.get_expiring_products, name='get_expiring_products'),
] 