from django.shortcuts import render,redirect
from .models import Category,Brand,Product,ProductAttributes,Banner,cartorder,cartorderitems,ProductReview,WishList
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string

from django.contrib.auth.forms import UserCreationForm
from  .forms import signup_form,ProductReviewForm
from django.contrib.auth import authenticate,login
from  django.contrib.auth.decorators import login_required

from django.db.models import Avg,Min,Max,Count

#paypal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.
def home(request):
    data = Product.objects.filter(is_featured=True).order_by('-id')
    banner = Banner.objects.all().order_by('-id')
    return render(request,'index.html',{"data":data,"banner":banner})

def Category_list(request):
    data = Category.objects.all().order_by('-id')
    return render(request,'category_list.html',{"data":data})

def Brands_list(request):
    data = Brand.objects.all().order_by('-id')
    return render(request,'brands_list.html',{"data":data})

def Product_List(request):
    total_products = Product.objects.count()
    data = Product.objects.all().order_by('-id')[:3]
    # category=Product.objects.distinct().values('category__title','category__id')
    # brand = Product.objects.distinct().values('brand__title',"brand__id")
    # colors=ProductAttributes.objects.distinct().values('color__title','color__id',"color__color_code")
    # sizes = ProductAttributes.objects.distinct().values('size__title','size__id')
    return render(request,'product_list.html',{
        "data":data,
        'total_products':total_products,
        # 'category':category,
        # 'brand':brand,
        # 'colors':colors,
        # 'sizes':sizes
    })
def Category_Product_List(request,id):
    category = Category.objects.get(id=id)
    data = Product.objects.filter(category=category).order_by('-id')
    # category = Product.objects.distinct().values('category__title', 'category__id')
    # brand = Product.objects.distinct().values('brand__title', "brand__id")
    # colors = ProductAttributes.objects.distinct().values('color__title', 'color__id', "color__color_code")
    # sizes = ProductAttributes.objects.distinct().values('size__title', 'size__id')
    return render(request,'category_product_list.html',{
        'data':data,
        # 'category': category,
        # 'brand': brand,
        # 'colors': colors,
        # 'sizes': sizes
    })

def Brand_product_list(request,id):
    brand = Brand.objects.get(id=id)
    data = Product.objects.filter(brand=brand)
    # category = Product.objects.distinct().values('category__title', 'category__id')
    # brand = Product.objects.distinct().values('brand__title', "brand__id")
    # colors = ProductAttributes.objects.distinct().values('color__title', 'color__id', "color__color_code")
    # sizes = ProductAttributes.objects.distinct().values('size__title', 'size__id')
    return render(request,"brand_product_list.html",{
        'data':data,
        # 'category': category,
        # 'brand': brand,
        # 'colors': colors,
        # 'sizes': sizes
    })

# product details page
def Product_Details_page(request,slug,id):
    product = Product.objects.get(id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    colors=ProductAttributes.objects.filter(product=product).values('color__id','color__title','color__color_code').distinct()
    sizes=ProductAttributes.objects.filter(product=product).values('size__id','size__title','price','color__id').distinct()
    print(sizes)
    print(colors)
    form=ProductReviewForm()

    canAdd=True
    review_check=ProductReview.objects.filter(user=request.user,product=product).count()
    if request.user.is_authenticated:
        if review_check > 0:
            canAdd = False
    # send the product review to template
    review=ProductReview.objects.filter(product=product)

    # fetch average rating based on total rating
    avg_rating=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    return render(request,'product_details_page.html',{
        "data":product,
        "related_product":related_products,
        "colors":colors,
        "sizes":sizes,
        'form':form,
        'canAdd':canAdd,
        'reviews':review,
        'avg_rating':avg_rating
    })

# search function for home page
def search_products(request):
    qs=request.GET['q']
    data = Product.objects.filter(title__icontains=qs).order_by('-id')
    return render(request,'search_product.html',{'data':data})

# filter data by products
def filter_data(request):
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    minprice = request.GET['minprice']
    maxprice = request.GET['maxprice']
    allProducts=Product.objects.all().order_by('-id').distinct()
    allProducts = allProducts.filter(productattributes__price__gte=minprice)
    allProducts = allProducts.filter(productattributes__price__lte=maxprice)
    if len(colors) > 0:
        allProducts =allProducts.filter(productattributes__color_id__in=colors).distinct()
        print(allProducts)
    if len(categories) > 0:
        allProducts = allProducts.filter(category__id__in=categories).distinct()
    if len(brands) > 0:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()
    if len(sizes) > 0:
        allProducts = allProducts.filter(productattributes__size_id__in=sizes).distinct()
    t = render_to_string('ajax/product_list.html', {'data': allProducts})
    return JsonResponse({'data':t})


def loadmode_data(request):
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    total = int(request.GET['total'])
    data = Product.objects.all().order_by('-id')[offset:total:limit]
    t=render_to_string('ajax/product_list.html',{"data":data})
    return JsonResponse({"data":t})

def Add_To_Cart(request):
    # del request.session['cartdata']
    cart_p={}
    cart_p[str(request.GET['id'])]={
        'title':request.GET['title'],
        'qty':request.GET['qty'],
        'price':request.GET['price'],
        'image':request.GET['image']
    }
    print(cart_p)
    # del request.session['cartdata']
    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data=request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_p[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cartdata']=cart_data
        else:
            cart_data=request.session['cartdata']
            cart_data.update(cart_p)
            request.session['cartdata']=cart_data
    else:
        request.session['cartdata']=cart_p
    return JsonResponse(
        {"data":request.session['cartdata'],
         "totalitems":len(request.session['cartdata'])})

def Cart_List(request):
    total_amount=0
    for p_id,item in request.session['cartdata'].items():
        total_amount += int(item['qty']) * float(item['price'])
    return render(request, 'cart_list.html',
                      {"cart_data": request.session['cartdata'],
                       "totalitems": len(request.session['cartdata']),
                       'total_amount': total_amount
                       })
def Delete_Cart_Item(request):
    p_id = str(request.GET['id'])
    print(p_id)
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data=request.session['cartdata']
            del request.session['cartdata'][p_id]
            request.session['cartdata']=cart_data
    total_amount = 0
    for p_id, item in request.session['cartdata'].items():
        total_amount += int(item['qty']) * float(item['price'])
    t = render_to_string('ajax/cart_list.html', {"cart_data": request.session['cartdata'],
                       "totalitems": len(request.session['cartdata']),
                       'total_amount': total_amount
                       })
    return JsonResponse({"data": t,"totalitems": len(request.session['cartdata'])})

def Update_Cart_Vtem(request):
    p_id = str(request.GET['id'])
    p_qty=request.GET['qty']
    print(p_id,p_qty)
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = p_qty
            print("cart data",cart_data)
            request.session['cartdata'] = cart_data
    total_amount = 0
    for p_id,item in request.session['cartdata'].items():
        total_amount += int(item['qty']) * float(item['price'])
    t = render_to_string('ajax/cart_list.html', {"cart_data": request.session['cartdata'],
                                                 "totalitems": len(request.session['cartdata']),
                                                 'total_amount': total_amount
                                                 })
    return JsonResponse({"data": t, "totalitems": len(request.session['cartdata'])})

def signup(request):
    if request.method == "POST":
        form=signup_form(request.POST)
        if form.is_valid():
            user = form.save()
            # username = form.cleaned_data.get('username')
            # pwd = form.cleaned_data.get('password11')
            # user = authenticate(username=username, password=pwd)
            login(request, user)
            return redirect('home')
    form = signup_form()
    return render(request,'registration/signup.html',{"form":form})

# @login_required
# def Checkout_Cart(request):
#     # paypall  payment with static
#     order_id="123"
#     host=request.get_host()
#     paypal_dict={
#         'business':settings.PAYPAL_RECEIVER_EMAIL,
#         'amount':'0',
#         'item_name':"item Name",
#         'invoice':'INC-123',
#         'currency_code':'usd',
#         'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
#         'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
#     }
#     form=PayPalPaymentsForm(initial=paypal_dict)
#     total_amount = 0
#     for p_id, item in request.session['cartdata'].items():
#         total_amount += int(item['qty']) * float(item['price'])
#     return render(request,'checkout.html', {"cart_data": request.session['cartdata'],
#                                                  "totalitems": len(request.session['cartdata']),
#                                                  'total_amount': total_amount,
#                                                 'form':form
#                                                  })

@login_required
def Checkout_Cart(request):
    total_amount = 0
    totalAmount = 0
    if 'cartdata' in request.session:
        for p_id, item in request.session['cartdata'].items():
            totalAmount += int(item['qty']) * float(item['price'])
        # create order
        order = cartorder.objects.create(
            user=request.user,
            total_amount=totalAmount
        )
        # end order
        for p_id, item in request.session['cartdata'].items():
            total_amount += int(item['qty']) * float(item['price'])
            # order items
            items =cartorderitems.objects.create(
                order=order,
                invoice_num='INV_'+str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty'])*float(item['price'])
            )
        # end order items
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total_amount,
            'item_name': "orderNo" + str(order.id),
            'invoice': 'Invoice_no' + str(order.id),
            'currency_code': 'usd',
            'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
            'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'checkout.html', {"cart_data": request.session['cartdata'],
                                                 "totalitems": len(request.session['cartdata']),
                                                 'total_amount': total_amount,
                                                 'form': form
                                                 })

@csrf_exempt
def payment_done(request):
    returnData=request.POST
    return render(request,'payment_success.html',{"data":returnData})
@csrf_exempt
def payment_cancelled(request):
    return render(request,'payment_fail.html')


def Save_Review(request,p_id):
    product=Product.objects.get(id=p_id)
    user=request.user
    review=ProductReview.objects.create(
        product=product,
        user=user,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating']
    )
    data={
        'user':user.username,
        # 'review_text':review['review_text'],
        # 'review_rating':review['review_rating']
        'review_text' : request.POST['review_text'],
        'review_rating' : request.POST['review_rating']
    }
    avg_rating=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    return JsonResponse({'bool':True,"data":data,'avg_review':avg_rating})

def My_DashBoard(request):
    return render(request,'user/dashboard.html')
def My_Orders(request):
    orders=cartorder.objects.filter(user=request.user).order_by('-id')
    return render(request,'user/orders.html',{'orders':orders})
def My_Order_Items(request,id):
    order=cartorder.objects.get(id=id)
    order_items=cartorderitems.objects.filter(order=order).order_by('-id')
    return render(request,'user/my_order_item.html',{'order_items':order_items})

def Add_Whish_List(request):
    p_id=request.GET['p_id']
    print(p_id)
    product=Product.objects.get(id=p_id)
    data={}
    check_wish_list=WishList.objects.filter(product=product,user=request.user).count()
    if check_wish_list > 0:
        data={
            'bool':False
        }
    else:
        whish_list=WishList.objects.create(
            product=product,
            user=request.user
        )
        data={
            'bool':True
        }
    return JsonResponse(data)
def My_Wish_list(request):
    wish_list=WishList.objects.filter(user=request.user).order_by('-id')
    return render(request,"user/add_whish_list.html",{'wish_list':wish_list})
