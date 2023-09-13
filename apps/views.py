from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import random
import string
from django.core.mail import send_mail

# Create your views here.
def register(request):
        #Xử dụng form của Django
        form = CreateUserForm()
        if request.method == 'POST':
                form = CreateUserForm(request.POST)
                if form.is_valid():
                        form.save()
                return redirect('login')
        context = {
                'form': form,
                'user_login': 'hidden',
        }
        return render(request, 'app/register.html', context)
def login_account(request):
        #Xác thực người dùng
        if request.user.is_authenticated:
                return redirect('home')
        #Bắt tài khoản
        if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                        login(request, user)
                        return redirect('home')
                else:
                        messages.info(request, 'Tài khoản hoặc mật khẩu không chính xác!!!')
        context = {
                'user_login': 'hidden'
        }
        return render(request, 'app/login.html', context)
def logout_account(request):
        #Xủ lí thoát
        logout(request)
        return redirect('login')
def home(request):
        if request.user.is_authenticated:
                customer = request.user
                # Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                # Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"

        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                user_not_login = "show"
                user_login = "hidden"
        categories = Category.objects.filter(is_sub=False)
        # Ng dùng chọn
        active_category = request.GET.get('category', '')
        #Lấy all sản phầm
        products = Product.objects.all()
        context = {
                'products': products,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
        }
        return render(request, 'app/home.html', context)
def cart(request):
        #Xác thực user
        if request.user.is_authenticated:
                customer = request.user
                #Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                #Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                user_not_login = "show"
                user_login = "hidden"
        categories = Category.objects.filter(is_sub=False)
        # Ng dùng chọn
        active_category = request.GET.get('category', '')
        context = {
                'items': items,
                'order': order,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
        }
        return render(request, 'app/cart.html', context)
def checkout(request):
        if request.user.is_authenticated:
                customer = request.user
                #Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                #Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
            #Check ô chọn sản phẩm
        #if request.method == 'GET':
        #        selected_product_ids = request.GET.getlist('selectedProducts')
        #        selected_products = OrderItem.objects.filter(product__id__in=selected_product_ids)
                # Tính tổng giá tiền của các sản phẩm được chọn
         #       total_price = sum(item.get_total for item in selected_products)

        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                user_not_login = "show"
                user_login = "hidden"
        categories = Category.objects.filter(is_sub=False)
        # Ng dùng chọn
        active_category = request.GET.get('category', '')
        context = {
                'items': items,
                'order': order,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
        }
        return render(request, 'app/checkout.html', context)
def updateItem(request):
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']
        customer = request.user
        product = Product.objects.get(id=productId)
        # Lấy và tạo order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        if action == 'add':
                orderItem.quantity += 1
        elif action == 'remove':
                orderItem.quantity -= 1

        orderItem.save()
        if orderItem.quantity <= 0:
              orderItem.delete()
        return JsonResponse('added', safe=False)
def search(request):
        if request.method == 'POST':
                searched = request.POST["searched"]
                keys = Product.objects.filter(name__contains=searched)
        if request.user.is_authenticated:
                customer = request.user
                # Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                # Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                user_not_login = "show"
                user_login = "hidden"
                # Lấy all sản phầm
        products = Product.objects.all()
        context = {
                'products': products,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                "searched": searched,
                "keys": keys,
        }

        return render(request, 'app/search.html', context)
def category(request):
        categories = Category.objects.filter(is_sub=False)  # Khai báo biến categories
        active_category_slug = request.GET.get('category', '')
        active_category = None
        products = Product.objects.all()  # Giá trị mặc định
        if active_category_slug:
                try:
                        active_category = Category.objects.get(slug=active_category_slug)
                        products = Product.objects.filter(category=active_category)
                except Category.DoesNotExist:
                        active_category = None
        if request.user.is_authenticated:
                customer = request.user
                #Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                #Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
                # Ng dùng chọn
                active_category = request.GET.get('category', '')
                if active_category:
                        products = Product.objects.filter(category__slug=active_category)
        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                user_not_login = "show"
                user_login = "hidden"

        # Ng dùng chọn
        active_category = request.GET.get('category', '')
        context = {
                'items': items,
                'order': order,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
                'products': products,
                'active_category': active_category,
        }
        return render(request, 'app/category.html', context)
def detail(request):
        if request.user.is_authenticated:
                customer = request.user
                #Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                #Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                #Ân đăng nhập và đăng kí
                user_not_login = "show"
                user_login = "hidden"
        id = request.GET.get('id', '')
        products = Product.objects.filter(id=id)
        categories = Category.objects.filter(is_sub=False)
        # Ng dùng chọn
        active_category = request.GET.get('category', '')
        context = {
                'items': items,
                'order': order,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
                'products': products,
        }
        return render(request, 'app/detail.html', context)
def hotline(request):
        if request.user.is_authenticated:
                customer = request.user
                #Lấy và tạo order
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                #Truy cập all đơn hàng đã đặt
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                user_not_login = "hidden"
                user_login = "show"
                categories = Category.objects.filter(is_sub=False)
        else:
                items = []
                order = {'get_cart_items': 0, 'get_cart_total': 0}
                cartItems = order['get_cart_items']
                #Ân đăng nhập và đăng kí
                user_not_login = "show"
                user_login = "hidden"
        context = {
                'items': items,
                'order': order,
                'cartItems': cartItems,
                'user_not_login': user_not_login,
                'user_login': user_login,
                'categories': categories,
        }
        return render(request, 'app/hotline.html', context)
def forgetpass(request):
        # if request.method == 'POST':
         #       email = request.POST.get('email')
          #      try:
          #              user = User.objects.get(email=email)
          #              new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
          #              user.set_password(new_password)
           #             user.save()
           #             send_mail(
           #                     'Password Reset',
            #                    f'Your new password: {new_password}',
            #                    'from@example.com',
            #                    [email],
            #                    fail_silently=False,
            #           )
            #            messages.success(request, 'Mật khẩu đã được thay đổi, check email để lấy mật khẩu')
          #              return redirect('login')
          #      except User.DoesNotExist:
           #             messages.info(request, 'Không có tài khoản nào với email này')
           #             return redirect('forget_pass')
        context = {
                'user_not_login': 'show',
                'user_login': 'hidden',
        }
        return render(request, 'app/forget-password.html', context)
