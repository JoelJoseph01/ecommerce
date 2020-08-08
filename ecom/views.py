from django.shortcuts import render, redirect
from .models import *
from .forms import *
import json
import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as dj_login,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
def home(request):
    return render(request, 'ecom/home.html')

def store(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        except Exception:
            customer = Customer.objects.create(user=request.user)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
        cartItems = order['get_cart_items']
        cartItems = order.get_cart_items


    products = Product.objects.all()
    context = {'products': products,'cartItems':cartItems}
    return render(request, 'ecom/store.html', context)

def cart(request):

        if request.user.is_authenticated:
            try:
                customer = request.user.customer
            except Exception:
                return redirect('empty')
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items


                
        else:
        
            items = []
            order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
            cartItems = order.get_cart_items

        context = {'items':items, 'order':order,'cartItems':cartItems}
        return render(request, 'ecom/cart.html', context)

def empty(request):
    return render(request,'ecom/empty.html')

@login_required
def checkout(request):
    if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
    else:
        
            items = []
            order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
            cartItems = order.get_cart_items
    context = {'items':items, 'order':order,'cartItems':cartItems}
    return render(request, 'ecom/checkout.html', context)


def signupuser(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'GET':
            return render(request, 'ecom/signupuser.html', {'form': SignUp()})
        if request.POST['password1'] == request.POST['password2']:
            try:
                form = SignUp(request.POST)
                email = request.POST['email']
                if User.objects.filter(email=email):
                    return render(request, 'ecom/signupuser.html', {'form': SignUp(), 'error': 'Email is already taken'})
                user = User.objects.create_user(
                    request.POST['username'], email=request.POST['email'], password=request.POST['password1'])
                user.save()
                dj_login(request, user)
                return redirect('store')
            except IntegrityError:
                return render(request, 'ecom/signupuser.html', {'form': SignUp(), 'error': 'That username has already been taken. Please choose a new username'})


def loginuser(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'GET':
            return render(request, 'ecom/loginuser.html', {'form': AuthenticationForm()})
        else:
            user = authenticate(
                request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'ecom/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and password did not match'})
            else:
                dj_login(request, user)
                return redirect('store')

@login_required
def logoutuser(request):
        logout(request)
        return render(request,'ecom/home.html')

@login_required
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

@login_required
def processOrder(request):
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                country=data['shipping']['country'],
            )
        return JsonResponse('Payment Successful',safe=False)
