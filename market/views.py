from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from functools import wraps

from .models import Product, Category, UserProfile
from .cart import Cart
from .forms import SignUpForm, UserUpdateForm, UserProfileForm, ProductForm, CategoryForm


def staff_required(view_func):
    """
    Custom decorator ensuring only admin/staff members can access management views.
    Unauthenticated users are redirected to login.
    Non-admin logged-in users receive a permission warning and are redirected to home catalog.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with an Administrator account to access Store Management.")
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission Denied. Only Store Administrators can access the Manage Store page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def home(request):
    """
    Product Catalog Home page with combined multi-parameter filtering & sorting:
    - Search query (q) by product name, description, or category name
    - Category slug filter
    - Min price & Max price filters
    - Sorting options
    """
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    # Price bounds for filter inputs
    price_aggregate = Product.objects.filter(is_active=True).aggregate(
        min_p=Min('price'), max_p=Max('price')
    )
    lowest_price = price_aggregate['min_p'] or 0
    highest_price = price_aggregate['max_p'] or 100

    # Filtering logic
    q = request.GET.get('q', '').strip()
    selected_category_slug = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(category__name__icontains=q) | 
            Q(description__icontains=q)
        )

    selected_category = None
    if selected_category_slug:
        selected_category = Category.objects.filter(slug=selected_category_slug).first()
        if selected_category:
            products = products.filter(category=selected_category)

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_slug': selected_category_slug,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'lowest_price': lowest_price,
        'highest_price': highest_price,
        'total_results': products.count(),
    }
    return render(request, 'home.html', context)


def product_detail(request, slug):
    """
    Product detail page showing stock count, full description, and add-to-cart button.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'detail.html', context)


def cart_detail(request):
    """
    Shopping cart summary page displaying line items, quantity adjustment controls,
    subtotal, and checkout placeholder button.
    """
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


def cart_add(request, product_id):
    """
    Add product to shopping cart with stock validation.
    Supports both regular POST and AJAX requests.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    success, message = cart.add(product=product, quantity=quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_total': len(cart)
        })

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    redirect_url = request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('cart_detail')


def cart_update(request, product_id):
    """
    Update item quantity directly in the cart with stock validation.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    success, message = cart.add(product=product, quantity=quantity, override_quantity=True)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('cart_detail')


def cart_remove(request, product_id):
    """
    Remove item completely from cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"'{product.name}' was removed from your cart.")
    return redirect('cart_detail')


def checkout(request):
    """
    Simulated Checkout page: validates stock, decrements database stock upon order submission,
    clears cart session, and shows confirmation.
    """
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty! Add some fresh groceries first.")
        return redirect('home')

    if request.method == 'POST':
        out_of_stock_items = []
        for item in cart:
            prod = item['product']
            if item['quantity'] > prod.stock_quantity:
                out_of_stock_items.append(f"{prod.name} (Only {prod.stock_quantity} available)")

        if out_of_stock_items:
            messages.error(
                request, 
                "Stock updated! The following items exceed available quantity: " + ", ".join(out_of_stock_items)
            )
            return redirect('cart_detail')

        for item in cart:
            prod = item['product']
            prod.stock_quantity -= item['quantity']
            prod.save()

        cart.clear()
        messages.success(request, "🎉 Thank you for your order! Your groceries are being packed for delivery.")
        return render(request, 'checkout_success.html')

    user_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None

    return render(request, 'checkout.html', {
        'cart': cart,
        'profile': user_profile,
    })


def signup_view(request):
    """
    User Sign Up view using Django authentication.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to FlavorFoundry Market, {user.first_name or user.username}!")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    """
    User Login view.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """
    User Logout view.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    """
    User Profile View & Edit.
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=profile)

    return render(request, 'registration/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
    })


# ==========================================
# STAFF STORE MANAGEMENT DASHBOARD VIEWS
# ==========================================

@staff_required
def manage_products(request):
    """
    Frontend Store Manager Dashboard: Lists all products with stock counts, status,
    and action links (Edit, Delete, Add Stock).
    """
    products = Product.objects.all().select_related('category').order_by('-created_at')
    categories = Category.objects.all()

    q = request.GET.get('q', '').strip()
    cat_id = request.GET.get('category', '').strip()

    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(category__name__icontains=q)
        )
    if cat_id:
        products = products.filter(category_id=cat_id)

    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'low_stock_count': products.filter(stock_quantity__lte=5).count(),
        'out_of_stock_count': products.filter(stock_quantity=0).count(),
        'q': q,
        'selected_cat': cat_id,
        'category_form': CategoryForm(),
    }
    return render(request, 'manage_products.html', context)


@staff_required
def add_product(request):
    """
    View for store managers to add a new grocery product to the catalog.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' was added successfully to the catalog!")
            return redirect('manage_products')
        else:
            messages.error(request, "Please correct the errors in the product form below.")
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {
        'form': form,
        'title': 'Add New Grocery Product',
        'button_text': 'Create Product',
    })


@staff_required
def edit_product(request, pk):
    """
    View for store managers to update product details and stock quantity.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' was updated successfully!")
            return redirect('manage_products')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {
        'form': form,
        'product': product,
        'title': f"Edit Product: {product.name}",
        'button_text': 'Update Product',
    })


@staff_required
def delete_product(request, pk):
    """
    View for store managers to remove a product from the catalog.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' was deleted from the store catalog.")
        return redirect('manage_products')

    return render(request, 'product_confirm_delete.html', {'product': product})


@staff_required
def add_category(request):
    """
    View to add a new category on the fly.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created successfully!")
        else:
            messages.error(request, "Failed to create category. Please check form input.")
    return redirect('manage_products')