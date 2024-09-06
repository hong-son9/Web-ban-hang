from django.contrib import admin
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register, name='register'),
    path('change_account', views.change_account, name="change_account"),
    path('register_api/', views.register_api, name='register_api'),
    path('forget_pass/', views.forgetpass, name='forget_pass'),
    path('login/', views.login_account, name='login'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('logout/', views.logout_account, name='logout'),
    path('', views.home, name='home'),
    path('home_api/', views.home_api, name="home_api"),
    path('cart/', views.cart, name='cart'),
    path('cart_api/', views.cart_api, name='cart_api'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('category/', views.category, name='category'),
    path('detail/', views.detail, name='detail'),
    path('hotline/', views.hotline, name='hotline'),

    path('pay', views.index, name='index'),
    path('payment', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query', views.query, name='query'),
    path('refund', views.refund, name='refund'),
    path('total', views.get_cart_total, name='total'),
]
