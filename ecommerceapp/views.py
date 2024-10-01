from django.shortcuts import render, redirect ,get_object_or_404
from django.http import JsonResponse
from .models import Product, Orders, OrderUpdate # Assuming you have a Product model
from ecommerceapp.models import Contact,Product
from django.contrib import messages
from math import ceil
from paytm import Checksum
# Render the main pages
MERCHANT_KEY = 'your_merchant_key'

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/login')
    
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Orders(
            items_json=items_json, 
            name=name, 
            amount=amount, 
            email=email, 
            address1=address1, 
            address2=address2, 
            city=city, 
            state=state, 
            zip_code=zip_code, 
            phone=phone
        )
        order.save()

        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        param_dict = {
            'MID': 'your_merchant_id',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')

def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
    
    checksum = response_dict.pop('CHECKSUMHASH', None)
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)

    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order successful')
            order_id = response_dict['ORDERID']
            amount_paid = response_dict['TXNAMOUNT']
            
            # Update order status
            Orders.objects.filter(order_id=order_id).update(
                amountpaid=amount_paid, 
                paymentstatus="PAID"
            )
        else:
            print('Order was not successful because: ' + response_dict['RESPMSG'])
    
    return render(request, 'paymentstatus.html', {'response': response_dict})


def home(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    
    # Get distinct categories
    cats = {item['category'] for item in catprods}

    # Loop through each category to gather products
    for cat in cats:
        # Filter products by category
        prod = Product.objects.filter(category=cat)
        n = len(prod)  # Count of products in this category
        nSlides = n // 4 + ceil((n / 4) - (n // 4))  # Number of slides needed
        
        allProds.append([prod, range(1, nSlides + 1), nSlides])

    params = {'allProds': allProds}
    return render(request, "index.html", params)

def contact(request):
    return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def shop(request):
    products = Product.objects.all()  # Fetch all products from the database
    return render(request, "shop.html", {'products': products})

def services(request):
    return render(request, "services.html")

def blog(request):
    return render(request, "blog.html")

def cart(request):
    cart = request.session.get('cart', {})
    total = 0  # Initialize total
    
    # Calculate total price and prepare cart items
    cart_items = []
    for product_id, item in cart.items():
        # Strip the dollar sign and convert price to float
        price = float(item['price'].replace('$', '').replace(',', '').strip())  # Convert price from string to float
        quantity = item['quantity']
        
        # Accumulate total price
        total += price * quantity  # Use total instead of total_price
        
        # Prepare cart item details
        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': price,  # Use the converted price without the typo
            'quantity': quantity,
            'subtotal': price * quantity,  # Calculate subtotal for each item
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

from django.shortcuts import render, redirect
from django.http import HttpResponse

def checkout(request):
    if request.method == 'POST':
        # Extracting form data from POST request
        first_name = request.POST.get('c_fname')
        last_name = request.POST.get('c_lname')
        email = request.POST.get('c_email_address')
        phone = request.POST.get('c_phone')
        address = request.POST.get('c_address')
        country = request.POST.get('c_country')
        state = request.POST.get('c_state_country')
        postal_code = request.POST.get('c_postal_zip')
        order_notes = request.POST.get('c_order_notes', '')

        # For now, we'll just simulate an order creation process.
        # You would add your logic here to save to the database or process a payment.

        # You can also validate inputs here if needed.
        if not first_name or not last_name or not email:
            return HttpResponse("Please fill in all required fields.", status=400)

        # Simulate successful order placement by redirecting to a thank you page
        return redirect('thankyou')

    # If it's a GET request, render the checkout page
    return render(request, 'checkout.html')

def thankyou(request):
    return render(request, 'thankyou.html')


from django.shortcuts import render, redirect
from .models import Product, CartItem

from django.shortcuts import redirect

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    
    # Assuming you have a way to retrieve the product details
    product = get_object_or_404(Product, id=product_id)
    
    if product_id in cart:
        # Update quantity if the item is already in the cart
        cart[product_id]['quantity'] += 1  # or set to the desired quantity
    else:
        # Add new item to cart
        cart[product_id] = {
            'product_name': product.name,
            'price': product.price,
            'quantity': 1,  # initial quantity
            'image_url': product.image.url  # Assuming the product model has an image field
        }

    # Save updated cart back to session
    request.session['cart'] = cart
    return redirect('cart')  # Redirect to the cart view


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Assuming you are storing items in the session or cart
    cart = request.session.get('cart', {})
    if product_id not in cart:
        cart[product_id] = {
            'product_name': product.product_name,  # Correct attribute
            'price': product.price,
            'quantity': 1,
            'image_url': product.image.url  # Assuming you want to store the image URL
        }
    else:
        cart[product_id]['quantity'] += 1

    request.session['cart'] = cart
    return redirect('cart')  # Redirect to cart or wherever you want

from django.shortcuts import render
from django.conf import settings

def cart_view(request):
    # This example assumes you have a cart object set up
    cart_items = request.session.get('cart', {})

    cart_data = []
    total_price = 0

    for product_id, item in cart_items.items():
        # Create a dictionary for rendering
        cart_data.append({
            'product_id': product_id,  # Include product_id here
            'product_name': item['product_name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image_url': item['image_url'],
        })
        total_price += item['price'] * item['quantity']

    context = {
        'cart_items': cart_data,
        'total_price': total_price,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'cart.html', context)


from django.http import JsonResponse

def update_cart(request, product_id):
    if request.method == 'GET':
        quantity = int(request.GET.get('quantity', 1))
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] = quantity  # Update quantity
            # Optionally update price if needed
            # cart[str(product_id)]['price'] = ...  # Recalculate price if necessary

        request.session['cart'] = cart  # Save the updated cart back to session

        # Send back the updated price for the item
        updated_price = cart[str(product_id)]['price']
        return JsonResponse({'price': updated_price})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())  # Sum all item quantities in the cart
    return JsonResponse({'cart_item_count': total_items})

from django.shortcuts import redirect, get_object_or_404
from .models import CartItem, Product

def remove_from_cart(request, product_id):
    # Convert product_id to string to match session cart keys
    product_id_str = str(product_id)

    # Get the cart from the session
    cart = request.session.get('cart', {})
    

    # Remove the item if it exists
    if product_id_str in cart:
        del cart[product_id_str]
        

    # Update the session
    request.session['cart'] = cart  
    

    # Redirect back to the cart
    return redirect('cart')  


def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        Pnumber=request.POST.get("Pnumber")
        message=request.POST.get("message")
        myquery=Contact(name=name,email=email,message=message,phonenumber=Pnumber)
        myquery.save()
        messages.info(request,"We will get back to you soon...")
        return render(request,"contact.html")
    return render(request,"contact.html")

from django.http import HttpResponse

from math import ceil
from django.shortcuts import render
from .models import Product

def shop_view(request):
    allProds = []
    # Get distinct categories
    cats = Product.objects.values_list('category', flat=True).distinct()
    print(f"Categories found: {cats}")  # Debugging output

    # Loop through each category to gather products
    for cat in cats:
        prod_list = Product.objects.filter(category=cat)
        print(f"Products in category '{cat}': {prod_list}")  # Debugging output
        n = len(prod_list)  # Number of products in the category
        nSlides = n // 4 + ceil((n / 4) - (n // 4))  # Calculating slides
        allProds.append([prod_list, range(1, nSlides + 1), nSlides])

    print(f"Final allProds structure: {allProds}")  # Debugging output

    # Pass context to template
    context = {'allProds': allProds}
    return render(request, 'shop.html', context)