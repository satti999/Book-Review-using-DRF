from django.shortcuts import render
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import User,Profile
from Book.models import Book
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated

from .serilizer import UserSignupSerializer, UserLoginSerializer,AuthSignUpSerializer,VerifyAccountSerializer,ProfileSerializer
from .utils import generate_jwt_token, generate_otp,send_email
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.

class UserSignupViewSet(viewsets.ViewSet):

    def create(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            if User.objects.filter(email=email, is_verified=True).exists():
                return Response({'error': 'User already exists' }, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 8:
                return Response({'error': 'Password must be at least 8 characters long' }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email, is_verified=False).exists():
                otp=generate_otp()
                cache.set('otp', otp, timeout=300)
                recipient=email
                email_body="Your OTP is "+str(otp)
                subject="Email Verification"
                email_sent=send_email(recipient,subject,email_body)
                if not email_sent:
                        return Response({'error': 'Email not sent' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'Otp': 'Otp sent' }, status=status.HTTP_200_OK)
            serializer=UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                hashed_password = make_password(password)
                signup_data = {
                    "email": serializer.data['email'],
                    "role": serializer.data["role"],
                    "username": serializer.data["username"],
                    "password": hashed_password
                }
                otp=generate_otp()
                cache.set('otp', otp, timeout=300)
                recipient=email
                email_body="Your OTP is "+str(otp)
                subject="Email Verification"
                email_sent=send_email(recipient,subject,email_body)
                if not email_sent:
                        return Response({'error': 'Email not sent' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                serializer = AuthSignUpSerializer(data=signup_data)
                if serializer.is_valid():
                    serializer.save() 
                    Profile.objects.create(user=serializer.instance)                   
                    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)   
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            data = request.data
            serializer=VerifyAccountSerializer(data=data)
            if serializer.is_valid():
                email=serializer.data['email']
                otp=int(serializer.data['otp'])
                cache_otp = cache.get('otp')
                print("type of cache otp",type(cache_otp))
                print("cache otp",cache_otp)
                user = User.objects.filter(email=email)
                if not  user.exists():
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                if not cache_otp==otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
                user=user.first()
                user.is_verified = True
                user.save()
                
                return Response({'message': 'User verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginViewSet(viewsets.ViewSet):
  def create(self, request):
    try:
        serilizer = UserLoginSerializer(data=request.data)
        if serilizer.is_valid():
                email = serilizer.validated_data['email']
                password = serilizer.validated_data['password']
                role = serilizer.validated_data['role']
                user_role = ['admin', 'user']
                if role in user_role and 'password' in request.data.keys():
                    user = User.objects.filter(email=email).first()
                    if user is not None:
                        if check_password(password, user.password):
                           token = generate_jwt_token(email)
                           return Response({"details": "You are successfully logged in",'token': token}, status=status.HTTP_200_OK)
                        else:
                            return Response({"details": "Invalid Password", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"details": "User not found", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({"details": "Invalid Provider or Combination provided", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class ProfileViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 

    
    def create(self, request):
        try:
            user=request.user
            data = request.data
            serializer=ProfileSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({'message': 'Profile created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def update(self,request):
        try:
           user=request.user
           data= request.data
           serializer=ProfileSerializer(data=data)
           if serializer.is_valid():
               serializer.save(user=user)
               return Response({'message':"Your profile is updated sucessfully",'data':serializer.data})
           else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def retrive(self,request):
        try:
            user=request.user
            user_profile=Profile.objects.filter(user=user).first()
            return Response({'message':'Your profile','profile':{
                'username':user_profile.user.username,
                'first_name':user_profile.first_name,
                'last_name': user_profile.last_name,
                'date_of_birth':user_profile.date_of_birth,
                'profile_pic':user_profile.profile_image.url if user_profile.profile_image else None
            }})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        
    @action(methods=['get'], detail=False, url_name='book_likes')
    def user_likes(self,request):
        try:
            user=request.user
            user_profile=Profile.objects.get(user=user)
            books_ids=user_profile.liked_books
            book_titles = list(Book.objects.filter(id__in=books_ids).values_list('title', flat=True))
            if len(book_titles)==0:
                return Response({'message': 'you did not like any book', 'data':{}}, status=status.HTTP_200_OK)
            total_likes=len(book_titles)
            return Response({'meassage':"your liked books",'Total_likes':total_likes,'Liked_books':book_titles})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    

