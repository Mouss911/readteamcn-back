from django.db import models
import uuid

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    # Autres champs si nécessaire

    def __str__(self):
        return self.email

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class TokenSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    json = models.JSONField(default=dict)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=[('draft', 'Draft'), ('published', 'Published')])

    def __str__(self):
        return f"{self.name} (v{self.version})"

class Component(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ComponentVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    tokenset = models.ForeignKey(TokenSet, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.component.name} (v{self.version})"

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.email} - {self.action}"

class KpiEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=255, default="default_event")
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.email} - {self.event_type}"

class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('Developer', 'Developer'), ('Coach', 'Coach')])
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_by_user')

    def __str__(self):
        return f"{self.user.email} - {self.role}"

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    payload_json = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.type}"

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=255)
    target_id = models.UUIDField()
    role = models.CharField(max_length=50, choices=[('Coach', 'Coach'), ('Developer', 'Developer')])
    decision = models.CharField(max_length=50, blank=True, null=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected')])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.target_type} Review"