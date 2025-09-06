from django.shortcuts import render

# Create your views here.

def placeholder_view(request):
    """Placeholder view for development."""
    return render(request, 'users/placeholder.html')
