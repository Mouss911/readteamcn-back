from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Component(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('BUTTON', 'Button'),
        ('CARD', 'Card'),
        ('INPUT', 'Input'),
        ('MODAL', 'Modal'),
        ('ACCORDION', 'Accordion'),
        ('SIDEBAR', 'Sidebar'),
        ('NAVBAR', 'Navbar'),
        ('DROPDOWN', 'Dropdown'),
        ('CAROUSEL', 'Carousel'),
        ('CHART', 'Chart'),
        ('TABLE', 'Table'),
        ('TOAST', 'Toast'),
        ('TOGGLE', 'Toggle'),
        ('TEXTAREA', 'Textarea'),
        ('SELECT', 'Select'),
        ('ALERT', 'Alert'),
        ('BADGE', 'Badge'),
        ('BREADCRUMB', 'Breadcrumb'),
        ('FORM', 'Form'),
        ('PAGINATION', 'Pagination'),
        ('PROGRESS', 'Progress'),
    ])
    code = models.TextField()  # HTML/CSS/JS du composant
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='components')
    
    # AJOUT ICI : Champ status pour le workflow de validation
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('approved', 'Validé'),
        ('rejected', 'Rejeté'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name