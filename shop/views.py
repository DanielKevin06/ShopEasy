from django.http import JsonResponse
from django.shortcuts import render, redirect
from shop.form import CustomUserForm
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json

def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def favviewpage(request):
    if request.user.is_authenticated:
        fav=Wishlist.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav})
    else:
        return redirect("/")
    
def remove_fav(request,fid):
    item=Wishlist.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

def cart_page(request):
    if request.user.is_authenticated:
        wishlist=Wishlist.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"wishlist":wishlist})
    else:
        return redirect("/")
    
def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")
    
    
def fav_page(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_id = data['pid']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Wishlist.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status':'Product is already in Wishlist'}, status=200)
                else:
                    Wishlist.objects.create(user=request.user, product_id=product_id) 
                    return JsonResponse({'status':'Product added to Wishlist'}, status=200) 
        else:
            return JsonResponse({'status':'Login to add to Wishlist'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)

def add_to_cart(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            # print(request.user.id)
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status':'Product is already in Cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status':'Product is added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status':'Product is Out of Stock'}, status=200)   
        else:
            return JsonResponse({'status':'Login to Add to Cart'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
        return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pswd=request.POST.get('password')
            user=authenticate(request,username=name,password=pswd)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect("/login")
        return render(request,"shop/login.html")


def register(request):
    form=CustomUserForm
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration success, You can Login Now...!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def categories(request):
    category=Category.objects.filter(status=0)
    return render(request,"shop/categories.html",{"category":category})

def categoriesview(request,name):
    if(Category.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products, "category_name":name})
    else:
        messages.warning(request,"No such Category found")
        return redirect('categories')
    
def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request, "shop/products/product_details.html",{"products":products})
        else:
            messages.warning(request,"No such Product found")
            return redirect('categories')
        
    else:
        messages.warning(request,"No such Category found")
        return redirect('categories')
    