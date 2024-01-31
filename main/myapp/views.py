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







