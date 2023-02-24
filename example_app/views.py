from django.shortcuts import render
from .models import Name
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def name_list(request):
    names = Name.objects.all() 
    response = {'names': names}
    return render(request, 'names_list.html', response)


