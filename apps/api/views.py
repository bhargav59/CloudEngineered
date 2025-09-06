from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class PlaceholderAPIView(APIView):
    """Placeholder API view for development."""
    
    def get(self, request):
        return Response({'message': 'API endpoint placeholder'})
