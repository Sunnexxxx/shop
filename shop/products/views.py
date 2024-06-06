from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import UpdateView
from cart.models import Cart, CartItem
from .forms import ProductFilterForm, ProductSearchForm, ProductForm, AddToCartForm
from .models import CustomUser
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = ProductFilterForm(self.request.GET)
        self.search_form = ProductSearchForm(self.request.GET)

        if self.filter_form.is_valid():
            if self.filter_form.cleaned_data['category']:
                queryset = queryset.filter(category=self.filter_form.cleaned_data['category'])
            if self.filter_form.cleaned_data['sort_by']:
                sort_by = self.filter_form.cleaned_data['sort_by']
                if sort_by == 'price_asc':
                    queryset = queryset.order_by('price')
                elif sort_by == 'price_desc':
                    queryset = queryset.order_by('-price')

        if self.search_form.is_valid() and self.search_form.cleaned_data['query']:
            query = self.search_form.cleaned_data['query']
            queryset = queryset.filter(Q(name__icontains=query) | Q(category__name__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        context['search_form'] = self.search_form
        context['is_seller'] = self.request.user.is_authenticated and self.request.user.user_type == CustomUser.SELLER
        context['add_to_cart_form'] = AddToCartForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_to_cart' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                product_id = form.cleaned_data['product_id']
                quantity = form.cleaned_data['quantity']
                product = get_object_or_404(Product, id=product_id)
                if product.stock < quantity:
                    return JsonResponse({'success': False, 'error': 'Not enough stock available'}, status=400)
                else:
                    cart, created = Cart.objects.get_or_create(user=request.user)
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

                    if not created:
                        cart_item.quantity += int(quantity)
                    else:
                        cart_item.quantity = int(quantity)

                    cart_item.save()
                    return JsonResponse({'success': True, 'message': 'Item added to cart'})
        return self.get(request, *args, **kwargs)



class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('seller_product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['seller'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_to_cart_form'] = AddToCartForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_to_cart' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                product_id = form.cleaned_data['product_id']
                quantity = form.cleaned_data['quantity']
                product = get_object_or_404(Product, id=product_id)
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

                if quantity > product.stock:
                    return JsonResponse({'success': False, 'error': 'Not enough stock available'}, status=400)

                if not created:
                    cart_item.quantity += int(quantity)
                else:
                    cart_item.quantity = int(quantity)

                cart_item.save()
                return JsonResponse({'success': True}, status=200)
            else:
                print(form.errors)
        return self.get(request, *args, **kwargs)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_update.html'
    success_url = reverse_lazy('seller_product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['seller'] = self.request.user
        return kwargs

    def test_func(self):
        product = self.get_object()
        return product.seller == self.request.user


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('seller_product_list')

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller

    def handle_no_permission(self):
        return redirect('seller_product_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.test_func():
            return self.handle_no_permission()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)