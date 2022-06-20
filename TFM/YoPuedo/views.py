from django.shortcuts import render
from .forms import registro


def registrarse(request):
    if request.method == 'GET':
        form = registro()
        return render(request, "YoPuedo/registro.html", {'register_form': form})
