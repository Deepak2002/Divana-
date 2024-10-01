from django.urls import path
from ecommerceapp import views
from .views import add_to_cart, cart, update_cart, remove_from_cart

urlpatterns=[
    path('',views.home,name="home"),
    path('index.html',views.home,name="home"),
    path('contact.html',views.contact,name="contact"),
    path('about.html',views.about,name="about"),
    path('shop/', views.shop_view, name="shop"),
    path('services.html',views.services,name="services"),
    path('blog.html',views.blog,name="blog"),
    path('cart.html',views.cart,name="cart"),
     path('checkout/',views.checkout,name="checkout"),
     path('thankyou/',views.thankyou,name="thankyou"),
     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart-item-count/', views.cart_item_count, name='cart_item_count'),
     path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),  
     path('handlerequest/', views.handlerequest, name='handlerequest'),
]