from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from .models import User, Product
from django.contrib.auth import login
from django.views.generic.edit import FormView, UpdateView, DeleteView
from .forms import CustomUserCreationForm, ProductForm
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from .models import Product, Order, ProductInOrder


class MainPage(TemplateView):
    template_name = 'main/start.html'


class Register(FormView):
    template_name = 'main/register.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_staff = form.cleaned_data['is_staff']
        user.save()

        login(self.request, user)

        if user.is_staff:
            return redirect('owner')
        else:
            return redirect('buyer')


class Login(LoginView):
    template_name = 'main/login.html'
    form_class = AuthenticationForm
    staff = None

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('owner')
        else:
            return reverse_lazy('buyer')


class Logout(LogoutView):
    next_page = reverse_lazy('main')


class Owner(ListView):
    model = Product
    template_name = 'owner/owner.html'
    context_object_name = 'products'

    # def get_queryset(self):
    #     return Product.objects.filter(user=self.request.user)


class ProductCreate(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'owner/create.html'
    success_url = reverse_lazy('owner')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProductUpdate(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'owner/update.html'
    success_url = reverse_lazy('owner')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProductDelete(DeleteView):
    model = Product
    template_name = 'owner/delete.html'
    success_url = reverse_lazy('owner')


class Buyer(ListView):
    model = Product
    template_name = 'buyer/buyer.html'
    context_object_name = 'products'
    paginate_by = 10


class Detail(DetailView):
    model = Product
    template_name = 'buyer/detail.html'
    context_object_name = 'product'


class DetailOwner(DetailView):
    model = Product
    template_name = 'owner/detail.html'
    context_object_name = 'product'


class AddToCartView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)

        if self.request.user.is_authenticated:
            order, created = Order.objects.get_or_create(customer=self.request.user, status='Pending')
            product_in_order, created = ProductInOrder.objects.get_or_create(product=product, order=order)
            if product_in_order.quantity is None:
                product_in_order.quantity = 0
            product_in_order.quantity += 1
            product_in_order.save()
            order.total_amount = sum(item.product.price * item.quantity for item in order.productinorder_set.all())
            order.save()

            return reverse_lazy('cart')
        else:
            return reverse_lazy('login')


class CartView(ListView):
    model = ProductInOrder
    template_name = 'buyer/cart.html'
    context_object_name = 'products_in_cart'

    def get_queryset(self):
        order = self.request.user.order_set.filter(status='Pending').first()
        if order:
            return order.productinorder_set.all()
        else:
            return ProductInOrder.objects.none()

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        product_in_order_id = request.POST.get('product_in_order_id')

        if action == 'update':
            new_quantity = int(request.POST.get('quantity'))
            product_in_order = get_object_or_404(ProductInOrder, id=product_in_order_id)
            product_in_order.quantity = new_quantity
            product_in_order.save()

        elif action == 'delete':
            product_in_order = get_object_or_404(ProductInOrder, id=product_in_order_id)
            product_in_order.delete()

        return redirect(reverse_lazy('cart'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.request.user.order_set.filter(status='Pending').first()
        if order:
            context['total_amount'] = order.total_amount
        else:
            context['total_amount'] = 0

        return context