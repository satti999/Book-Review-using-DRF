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
    



class Book(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100, null=False)
    author = models.CharField(max_length=100, null=False,)
    description = models.CharField(max_length=350, null=False,)
    published_by = models.ForeignKey(User, related_name='books', on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='books/covers/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   


class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'
  
    