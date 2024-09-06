from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import random
import string
from django.core.mail import send_mail

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from .serializers import OrderItemSerializer, ProductSerializer
from django.contrib.auth.decorators import login_required

import hashlib
import hmac
import json
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from urllib.parse import quote

from apps.models import PaymentForm
from apps.vnpay import vnpay


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def register_api(request, user_id=None):
    if request.method == 'GET':
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            user_data = {'id': user.id, 'username': user.username, 'password': user.password, 'email': user.email}
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        else:
            users = User.objects.all()
            user_data = [{'id': user.id, 'username': user.username, 'password': user.password, 'email': user.email} for
                         user in users]
            return Response({'users': user_data}, status=status.HTTP_200_OK)

    # Xử lý POST request
    elif request.method == 'POST':
        form = UserCreationForm(request.data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            response_data = {
                'username': username,
                'message': 'Register successful',
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        errors = form.errors.get_json_data()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    # Xử lý PUT request (Sửa thông tin người dùng)
    elif request.method == 'PUT':
        user = get_object_or_404(User, pk=user_id)
        try:
            # Chuyển đổi dữ liệu từ chuỗi JSON sang dict
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        # Sử dụng UserChangeForm để xử lý cập nhật thông tin người dùng
        form = UserChangeForm(data, instance=user)

        if form.is_valid():
            form.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    # Xử lý DELETE request (Xóa người dùng)
    elif request.method == 'DELETE':
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'error': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def register(request):
    order = {'get_cart_items': 0, 'get_cart_total': 0}
    cartItems = order['get_cart_items']
    # Xử dụng form của Django
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            # Chuyển hướng đến trang đăng nhập sau khi đăng ký thành công
            return redirect(reverse('login'))
    context = {
        'form': form,
        'user_login': 'hidden',
        'cartItems': cartItems,
    }
    return render(request, 'app/register.html', context)


def change_account(request):
    if request.user.is_authenticated:
        customer = request.user
        # Lấy và tạo order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Truy cập all đơn hàng đã đặt
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    categories = Category.objects.filter(is_sub=False)

    if request.method == 'POST':
        form = ChangeUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Xử lý sau khi thay đổi thông tin thành công
            return redirect('login')  # Điều chỉnh URL đích của bạn
    else:
        form = ChangeUserProfileForm(instance=request.user)

    context = {'form': form,
               'cartItems': cartItems,
               'user_not_login': user_not_login,
               'user_login': user_login,
               'categories': categories,
               }
    return render(request, 'app/change_account.html', context)


def login_account(request):
    # Xác thực người dùng
    if request.user.is_authenticated:
        return redirect('home')
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_info = None
    # Bắt tài khoản
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Tài khoản hoặc mật khẩu không chính xác!!!')
    categories = Category.objects.filter(is_sub=False)
    context = {
        'user_login': 'hidden',
        'categories': categories,
        'cartItems': cartItems,
    }
    return render(request, 'app/login.html', context)


def logout_account(request):
    # Xủ lí thoát
    logout(request)
    return redirect('login')


def profile(request):
    form = CreateUserForm()
    user_not_login = "hidden"
    user_login = "show"

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        # Add user information to the context
        user_info = {
            'username': customer.username,
            'email': customer.email,
            'password': customer.password,

        }
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_info = None
        user_not_login = "show"
        user_login = "hidden"

    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()

    context = {
        'form': form,
        'products': products,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'user_info': user_info,  # Add user_info to the context
    }

    return render(request, 'app/profile.html', context)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def home_api(request, product_id=None):
    if request.user.is_authenticated:
        customer = request.user
        products = Product.objects.all()
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        if request.method == 'GET':
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


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
    # Lấy all sản phầm
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
    # Xác thực user
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
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
    }
    return render(request, 'app/cart.html', context)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def cart_api(request, item_id=None):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        if request.method == 'GET':
            # Trả về thông tin về sản phẩm trong giỏ hàng
            serializer = OrderItemSerializer(items, many=True)
            total_price = order.get_cart_total  # Sử dụng phương thức để tính tổng tiền giỏ hàng
            return Response({
                'items': serializer.data,
                'total_price_all': total_price
            }, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            # Xử lý thêm sản phẩm vào giỏ hàng
            serializer = OrderItemSerializer(data=request.data)
            if serializer.is_valid():
                product_id = serializer.validated_data['product']
                quantity = serializer.validated_data['quantity']

                # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
                order_item, created = OrderItem.objects.get_or_create(order=order, product_id=product_id)
                # Cập nhật số lượng
                order_item.quantity += quantity
                order_item.save()

                return Response({'message': 'Product added to cart successfully'}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'PUT':
            serializer = OrderItemSerializer(items, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Order item updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                item = order.orderitem_set.get(id=item_id)
            except OrderItem.DoesNotExist:
                return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)
            item.delete()
            return Response({'message': 'Order item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    else:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        # Lấy và tạo order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Truy cập all đơn hàng đã đặt
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    # Check ô chọn sản phẩm
    # if request.method == 'GET':
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
        categories = Category.objects.filter(is_sub=False)
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
        'categories': categories,
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
        # Lấy và tạo order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Truy cập all đơn hàng đã đặt
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
        # Ân đăng nhập và đăng kí
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
        # Lấy và tạo order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Truy cập all đơn hàng đã đặt
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
        categories = Category.objects.filter(is_sub=False)
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        # Ân đăng nhập và đăng kí
        user_not_login = "show"
        user_login = "hidden"
        categories = Category.objects.filter(is_sub=False)

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
    if request.user.is_authenticated:
        pass
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_info = None

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
    #           messages.success(request, 'Mật khẩu đã được thay đổi, check email để lấy mật khẩu')
    #               return redirect('login')
    #      except User.DoesNotExist:
    #             messages.info(request, 'Không có tài khoản nào với email này')
    #             return redirect('forget_pass')
    context = {
        'user_not_login': 'show',
        'user_login': 'hidden',
        'cartItems': cartItems,
    }
    return render(request, 'app/forget-password.html', context)


def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def get_cart_total(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = order.get_cart_total()
        return JsonResponse({'total': total})
    else:
        return JsonResponse({'error': 'User is not authenticated'})


def payment(request):
    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payment/payment.html", {"title": "Thanh toán"})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        payment = Payment_VNPay.objects.create(
            order_id=order_id,
            amount=amount,
            order_desc=order_desc,
            vnp_TransactionNo=vnp_TransactionNo,
            vnp_ResponseCode=vnp_ResponseCode
        )

        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Thành công", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Lỗi", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


n = random.randint(10 ** 11, 10 ** 12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html",
                  {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})


def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html",
                  {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})
