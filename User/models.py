from django.db import models
from enum import Enum




# Create your models here.

class UserRole(Enum):
    Admin = "admin"
    User = "user"



class User(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100, null=False,)
    email = models.EmailField(unique=True, max_length=100, null=False)
    password = models.CharField(max_length=100, null=False,)
    role = models.CharField(max_length=100,choices=[(role.value, role.name) for role in UserRole], null=False,)
    is_verified = models.BooleanField(default=False)



    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.email
    
    @property
    def is_authenticated(self):
        return True
    
def upload_to(instance, filename):
    return 'Profile_images/{filename}'.format(filename=filename)
class Profile(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    first_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100,default="")
    date_of_birth = models.DateField(null=True, blank=True)
    liked_books = models.JSONField(default=list)
    profile_image = models.ImageField(upload_to=upload_to, null=True, blank=True)



    