from django import forms
from .models import ResourceNeed

class ResourceNeedForm(forms.ModelForm):
    class Meta:
        model = ResourceNeed
        fields = [
            "resource",
            "quantity",
            "description",
            "pickup_available",
            "location",
            "contact_number",
            "donation_days",
            "donation_hours",
            "scheduling_notes",
            "additional_notes",
            "organization",
            "donations",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "location": forms.Textarea(attrs={"rows": 2}),
            "scheduling_notes": forms.Textarea(attrs={"rows": 2}),
            "additional_notes": forms.Textarea(attrs={"rows": 2}),
            "donation_days": forms.CheckboxSelectMultiple(),
            "donations": forms.CheckboxSelectMultiple(),
        }
