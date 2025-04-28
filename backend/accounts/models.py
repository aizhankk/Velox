from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserAccountManager(BaseUserManager):
  def create_user(self, email, name, password=None):
    if not email:
      raise ValueError('Users must have email address')
    
    email = self.normalize_email(email)
    user = self.model(email=email, name=name)
    user.set_password(password)
    user.save()
    return user
  
  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
        raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
        raise ValueError('Superuser must have is_superuser=True.')

    return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
  email = models.EmailField(max_length=255, unique=True)
  name =  models.CharField(max_length=255)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserAccountManager() 

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  def get_full_name(self):
    return self.name
  
  def get_short_name(self):
    return self.name
  
  def __str__(self):
    return self.email
  


from django.db import models
from django.core.exceptions import ValidationError

class Task(models.Model):
    FREQUENCY_CHOICES = [
        ('none',    'None'),
        ('daily',   'Every Day'),
        ('weekly',  'Every Week'),
        ('monthly', 'Every Month'),
        ('yearly',  'Every Year'),
    ]

    title        = models.CharField(max_length=200)
    category     = models.CharField(max_length=100, blank=True)
    date         = models.DateField()
    time_start   = models.TimeField(null=True, blank=True)
    time_end     = models.TimeField(null=True, blank=True)
    reminder     = models.BooleanField(default=False)
    location     = models.CharField(max_length=250, blank=True)
    notes        = models.TextField(blank=True)
    frequency    = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='none')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'time_start']

    def clean(self):
        if self.time_start and self.time_end and self.time_end <= self.time_start:
            raise ValidationError({'time_end': 'Время окончания должно быть позднее времени начала.'})

    def __str__(self):
        if self.time_start and self.time_end:
            return f"{self.title} @ {self.date} {self.time_start}-{self.time_end}"
        if self.time_start:
            return f"{self.title} @ {self.date} {self.time_start}"
        return f"{self.title} @ {self.date}"