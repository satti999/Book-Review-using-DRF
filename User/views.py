from django.shortcuts import render
import random
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import User,Book,Review
from .authentication import JWTAuthentication 
from .serilizer import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .serilizer import UserSignupSerializer, UserLoginSerializer,PublishBookSerializer,AuthSignUpSerializer,VerifyAccountSerializer
from .utils import generate_jwt_token, generate_email_body,send_email
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.




class UserSignupViewSet(viewsets.ViewSet):

    def create(self, request):
        try:
            print("data 1",request.data)
            email = request.data['email']
            password = request.data['password']
            if User.objects.filter(email=email, is_verified=True).exists():
                return Response({'error': 'User already exists' }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email, is_verified=False).exists():
                otp=random.randint(100000,999999)
                print("otp",otp)
                cache.set('otp', otp, timeout=300)
                recipient=email
                print("recipient",recipient)
                email_body="Your OTP is "+str(otp)
                print("email_body",)
                subject="Email Verification"
                email_sent=send_email(recipient,subject,email_body)
                if not email_sent:
                        return Response({'error': 'Email not sent' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'Otp': 'Otp sent' }, status=status.HTTP_200_OK)

            if len(password) < 8:
                return Response({'error': 'Password must be at least 8 characters long' }, status=status.HTTP_400_BAD_REQUEST)
            serializer=UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                hashed_password = make_password(password)
                signup_data = {
                    "email": serializer.data['email'],
                    "role": serializer.data["role"],
                    "username": serializer.data["username"],
                    "password": hashed_password
                }
                otp=random.randint(100000,999999)
                print("otp",otp)
                cache.set('otp', otp, timeout=300)
                # email_body = generate_email_body(otp)
                    #recipient , subject, body
                recipient=email
                print("recipient",recipient)
                email_body="Your OTP is "+str(otp)
                print("email_body",)
                subject="Email Verification"
                email_sent=send_email(recipient,subject,email_body)
                if not email_sent:
                        return Response({'error': 'Email not sent' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                #logic to handle already saved data.
                serializer = AuthSignUpSerializer(data=signup_data)
                if serializer.is_valid():
                    serializer.save()                    
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
                print("type of otp",type(otp))
                print("user otp",otp)
                cache_otp = cache.get('otp')
                print("type of cache otp",type(cache_otp))
                print("cache otp",cache_otp)
                user = User.objects.filter(email=email)
                if not  user.exists():
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                if not cache_otp==otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            # user[0].is_verified = True
            # user[0].save()
                user=user.first()
                user.is_verified = True
                user.save()
                return Response({'message': 'User verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginViewSet(viewsets.ViewSet):
  
#   @action(detail=False, methods=["post"], url_path="login")
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
                            if  check_password(password, user.password):
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
        




class PublishBookViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 



    def list(self, request):
        try:
            books = Book.objects.all()
            if not books:
                return Response({'message': 'No book found', 'data':{}}, status=status.HTTP_200_OK)
            
            serializer = PublishBookSerializer(books, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

      
    def create(self, request):
        try:
            serializer = PublishBookSerializer(data=request.data)
            if serializer.is_valid():
                # self.perform_create(serializer)
                serializer.save(published_by=self.request.user)
                return Response({'message': 'Book published successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            serializer = PublishBookSerializer(book)
            return Response({'message': 'Book Retrive successfully','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, pk=None):
        try:
            book = Book.objects.filter(published_by=request.user).get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            serializer = PublishBookSerializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save(publish_by=request.user)
                return Response({'message': 'Book updated successfully','data':serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def partial_update(self, request, pk=None):
            try:
                book = Book.objects.filter(published_by=request.user).get(pk=pk)
                if not book:
                    return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
                serializer = PublishBookSerializer(book, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(publish_by=request.user)
                    return Response({'message': 'Book updated successfully','data':serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
          
        

    def destroy(self, request, pk=None):
        try:
            book = Book.objects.filter(published_by=request.user).get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            book.delete()
            return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class ReviewViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 
    
    print("Review class")

    def create(self, request, pk=None):
        print("create method")
        book_id = request.query_params.get('book_id')
        user=request.user
        print("book id",book_id)
        try:
            book = Book.objects.get(pk=book_id)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            if book.published_by==user:
                return Response({'message':'you can not comment on your book'},status=status.HTTP_200_OK)
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user,book=book)
                return Response({'message': 'Review created successfully','data':serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            reviews = Review.objects.filter(book=book)
            if not reviews:
                return Response({'message': 'No review found','data':{}}, status=status.HTTP_200_OK)
            serializer = ReviewSerializer(reviews, many=True)
            return Response({'message': 'Review Retrive successfully','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return 
    
    def update(self, request, pk=None):
        try:
           review= Review.objects.get(pk=pk)
           if not review:
               return Response({'message': 'No comment found','data':{}}, status=status.HTTP_200_OK)
           serializer=ReviewSerializer(data=request.data)
           if serializer.is_valid:
               serializer.save()
               return Response({'message':'Your Review is update'},status=status.HTTP_200_OK)
           else:
               return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def destroy(self, request,pk=None):
        try:
            review= Review.objects.get(pk=pk)
            if not review:
               return Response({'message': 'No comment found','data':{}}, status=status.HTTP_200_OK)
            review.delete()
            return Response({'message': 'Your review is  deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        