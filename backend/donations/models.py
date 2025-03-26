from django.db import models
from django.conf import settings

class Donation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')  # Changed related_name
    
    CATEGORY_CHOICES = [
        ('clothing', 'Clothing'),
        ('toys', 'Toys & Games'),
        ('books', 'Books & Education'),
        ('medical', 'Medical Supplies'),
        ('food', 'Non-perishable Food'),
        ('other', 'Other'),
    ]
    
    item_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,default="clothing")
    other_category = models.CharField(max_length=100, blank=True, null=True)
    item_name = models.CharField(max_length=255,blank=True)
    item_description = models.TextField(blank=True)
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('likenew', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    item_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES,default="new")
    item_quantity = models.PositiveIntegerField(default=100)
    
    address_line1 = models.CharField(max_length=255,default="")
    city = models.CharField(max_length=100,default="")
    state = models.CharField(max_length=100,default="")
    zip_code = models.CharField(max_length=20,default="")
    
    pickup_availability = models.CharField(max_length=255,default="yes")  # Store as a comma-separated string
    pickup_notes = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)  
    
    uploaded_files = models.JSONField(default=list, blank=True)  # Store file names as JSON
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.email} - {self.item_name} ({self.item_category})"
