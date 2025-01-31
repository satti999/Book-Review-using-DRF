from django.db import models
from User.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

def upload_to(instance, filename):
    return 'books/coversImages/{filename}'.format(filename=filename)

class Book(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100, null=False)
    author = models.CharField(max_length=100, null=False,)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    likes = models.IntegerField(default=0,help_text='Number of likes for this book.')
    description = models.CharField(max_length=350, null=False,)
    published_by = models.ForeignKey(User, related_name='published_book', on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to=upload_to,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   


