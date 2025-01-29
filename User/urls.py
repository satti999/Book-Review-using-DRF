from django.urls import path, include
from . import views
from rest_framework import routers




router = routers.DefaultRouter()

#router.register('signup', AuthSignUpAPIView, basename='signup')

router.register('signup', views.UserSignupViewSet, basename='signup')
router.register('login', views.UserLoginViewSet, basename='login')
router.register('verifyotp', views.VerifyOTPViewSet, basename='verifyotp')


urlpatterns = router.urls