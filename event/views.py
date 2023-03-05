from django.shortcuts import render

# Create your views here.

def create_event(request):
  return render(request, 'create_event.html', {})