from django.db import models
from enum import Enum


# Create your models here.

class UserRole(Enum):
    Admin = "admin"
    User = "user"

class User(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100, null=False,required=True)
    email = models.EmailField(unique=True, max_length=100, null=False)
    password = models.CharField(max_length=100, null=False,required=True)
    role = models.CharField(max_length=100,choices=[(role.value, role.name) for role in UserRole], null=False,required=True)



    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username



class Book(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100, null=False,required=True)
    author = models.CharField(max_length=100, null=False,required=True)
    description = models.CharField(max_length=350, null=False,required=True)
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

    def save(self, *args, **kwargs):
        if self.book.published_by == self.user:
            raise ValueError("You cannot review your own book")
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'
  
    