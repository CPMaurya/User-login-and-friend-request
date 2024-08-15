from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest
from rest_framework.authtoken.models import Token


class SignUpView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            token = Token.objects.get_or_create(user=user)
            response = {
                "user_id": user.pk,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "access_token": user.auth_token.key,
                "groups": [g.name for g in user.groups.all()]
            }
            return Response(response, status.HTTP_200_OK)
        
        user = User.objects.create_user(username=email, email=email, password=password, first_name=email.split("@")[0])
        token = Token.objects.get_or_create(user=user)
        response = {
            "user_id": user.pk,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "access_token": user.auth_token.key,
            "groups": [g.name for g in user.groups.all()]
            # "access_token": token
        }
        return Response(response, status.HTTP_200_OK)
    

class SearchPagination(PageNumberPagination):
    page_size = 10


class UserSearchView(generics.ListAPIView):
    # permission_classes = []
    queryset = User.objects.all()
    pagination_class = SearchPagination
    serializer_class = []
    
    def get_queryset(self):
        search_query = self.request.query_params.get('search', '').lower()
        if '@' in search_query:  # Searching by email
            return User.objects.filter(email__iexact=search_query)
        return User.objects.filter(username__icontains=search_query)
    
    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        
        response = []
        for user in users:
            response.append({
                "email": user.email,
                "name": user.get_full_name(),
                "username": user.username
            })
        return Response(response, status=status.HTTP_200_OK)
    
    
class SendFriendRequestView(generics.ListCreateAPIView):
    serializer_class = []
    
    def create(self, request, *args, **kwargs):
        data = self.request.data
        receiver_email = data['receiver_email']
        
        request_user = self.request.user
        receiver_user = User.objects.get(email=receiver_email)
        if FriendRequest.objects.filter(sender=request_user, receiver=receiver_user).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        FriendRequest.objects.create(sender=request_user, receiver=receiver_user, status='pending')
        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)

    
class FriendsListView(generics.ListAPIView):
    serializer_class = []
    
    def get_queryset(self):
        # sent_requests__status='accepted'
        queryset = User.objects.filter(sent_requests__sender=self.request.user)
        return queryset
    
    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        
        response = []
        for user in users:
            friend_list = []
            friends = user.sent_requests.all()
            for friend in friends:
                friend_list.append({
                    "email": friend.receiver.email,
                    "username": friend.receiver.username,
                    "name": friend.receiver.get_full_name(),
                    "status": friend.status,
                    "time": friend.timestamp
                    
                })
            response.append({
                "email": user.email,
                "name": user.get_full_name(),
                "username": user.username,
                "friend_list": friend_list
            })
        return Response(response, status=status.HTTP_200_OK)
