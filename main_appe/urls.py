from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('category_list',views.Category_list,name="category_list"),
    path('brands_list',views.Brands_list,name="brands_list"),
    path('product_list',views.Product_List,name='product_list'),
    path('search_product',views.search_products,name="search_product"),

    path('category_product_list/<id>',views.Category_Product_List,name='category_product_list'),
    path('brand_product_list/<id>',views.Brand_product_list,name="brand_product_list"),
    path('product_details/<slug>/<id>',views.Product_Details_page,name='product_details'),
    path('filter_products',views.filter_data,name='filter_products'),
    path('loadmode_data',views.loadmode_data,name='loadmode_data'),
    path('add_to_cart',views.Add_To_Cart,name='add_to_cart'),
    path('cart_list',views.Cart_List,name='cart_list'),
    path('delete_from_cart',views.Delete_Cart_Item,name='delete_from_cart'),
    path('update_cart_item',views.Update_Cart_Vtem,name="update_cart_item"),

    path('signup',views.signup,name="signup"),
    path('checkout',views.Checkout_Cart,name='checkout'),

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('save_review/<int:p_id>',views.Save_Review,name="save_review"),

#     user side development
    path('my_dashboard',views.My_DashBoard,name="my_dashboard"),
    path('my_orders',views.My_Orders,name='my_orders'),
    path('my_order_items/<int:id>',views.My_Order_Items,name='my_order_items'),

    path('add_whish_list',views.Add_Whish_List,name='add_whish_list'),
    path('my_wish_list',views.My_Wish_list,name='my_wish_list')

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)