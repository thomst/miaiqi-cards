from django.shortcuts import render, get_object_or_404
from .models import Postcard

# Create your views here.

def postcard_list(request):
    postcards = Postcard.objects.filter(is_public=True)
    return render(request, 'cards/postcard_list.html', {'postcards': postcards})

def postcard_detail(request, pk):
    postcard = get_object_or_404(Postcard, pk=pk, is_public=True)
    return render(request, 'cards/postcard_detail.html', {'postcard': postcard})
