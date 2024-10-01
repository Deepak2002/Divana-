from django.urls import path
from . import views
from authcart import views
from .views import ActivateAccountView

urlpatterns=[
    path('signup/',views.signup,name='signup'),
    path('login/',views.handlelogin,name='login'),
    path('logout/',views.handlelogout,name='logout'),
     path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),

]