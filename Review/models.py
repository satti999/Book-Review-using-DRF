from django.db import models
from Book.models import Book
from User.models import User


# Create your models here.

class Review(models.Model):
    book = models.ForeignKey(Book, related_name='book_reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_reviews', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'