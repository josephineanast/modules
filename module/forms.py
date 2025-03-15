from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean_barcode(self):
        """Ensure barcode is unique."""
        barcode = self.cleaned_data['barcode']
        
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            if Product.objects.exclude(pk=instance.pk).filter(barcode=barcode).exists():
                raise forms.ValidationError("A product with this barcode already exists.")
        else:
            if Product.objects.filter(barcode=barcode).exists():
                raise forms.ValidationError("A product with this barcode already exists.")
        return barcode