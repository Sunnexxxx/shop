from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Q

from cart.models import CartItem
from users.models import CustomUser
from .models import Category, Product


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")
    SORT_CHOICES = [
        ('price_asc', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low')
    ]
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Sort by")

    def filter_queryset(self, queryset):
        if self.is_valid():
            category_id = self.cleaned_data.get('category')
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            sort_by = self.cleaned_data.get('sort_by')
            if sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
        return queryset


class ProductSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Поиск")


class ProductForm(forms.ModelForm):
    seller = forms.ModelChoiceField(queryset=None, widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category', 'image', 'stock', 'seller']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        seller = kwargs.pop('seller', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        if seller:
            self.fields['seller'].queryset = CustomUser.objects.filter(pk=seller.pk)
            self.fields['seller'].initial = seller





class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1, label='')

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if self.product:
            self.fields['product_id'].initial = self.product.id

    def clean_product_id(self):
        product_id = self.cleaned_data.get('product_id')
        if not Product.objects.filter(id=product_id).exists():
            raise forms.ValidationError("Invalid product id")
        return product_id

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.stock:
            raise forms.ValidationError('Not enough stock available')
        return quantity