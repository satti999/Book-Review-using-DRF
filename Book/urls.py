from django.urls import path, include
from . import views
from  Review.views import ReviewViewSet
from rest_framework import routers

router = routers.DefaultRouter()

router.register('publishbook', views.PublishBookViewSet, basename='publishbook')
router.register('review',ReviewViewSet,basename='review')


urlpatterns = router.urls
