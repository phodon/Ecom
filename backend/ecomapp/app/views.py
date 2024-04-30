from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProfileSerializer
from .models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from app.middlewares import UserMiddleware
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)

# Create your views here.
@api_view(['POST'])
def register(request):
    data = request.data

    required_fields = ['password', 'confirm_password', 'email']
    for field in required_fields:
        if field not in data or not data[field]:
            return Response({'error': f'{field.capitalize()} is required'}, status=status.HTTP_400_BAD_REQUEST)

    if data['confirm_password'] != data['password']:
        return Response({'error': 'Password does not match Confirm_password'}, status=status.HTTP_400_BAD_REQUEST)

    if UserProfile.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserProfileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        logger.info('Register Successfully')
        return Response({'message': 'Register is success', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    return Response({'message': 'Information is invalid', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def loginUser(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(email=email, password=password)
    print(user)

    if not user:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token) 
    refresh = str(refresh) 

    user_data = {
        'email': user.email,
        'is_staff': user.is_staff  
    }

    return Response({'refresh_token': refresh,'access_token': access, 'user_data': user_data})