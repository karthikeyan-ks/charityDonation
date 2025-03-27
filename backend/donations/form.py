from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'donor',
            'item_category',
            'other_category',
            'item_name',
            'item_description',
            'item_condition',
            'item_quantity',
            'address_line1',
            'city',
            'state',
            'zip_code',
            'pickup_availability',
            'pickup_notes',
            'additional_notes',
            'uploaded_files',
        ]
        widgets = {
            'item_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'pickup_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)
        self.fields['donor'].disabled = True
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
