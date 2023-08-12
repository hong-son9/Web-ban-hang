from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('forget_pass/', views.forgetpass, name='forget_pass'),
    path('login/', views.login_account, name='login'),
    path('search/', views.search, name='search'),
    path('logout/', views.logout_account, name='logout'),
    path('', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('category/', views.category, name='category'),
    path('detail/', views.detail, name='detail'),
    path('hotline/', views.hotline, name='hotline'),




]
