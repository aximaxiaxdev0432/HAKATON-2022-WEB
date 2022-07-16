from django.contrib import admin
from django.urls import path
from users.views import AuthView, Cpanel

urlpatterns = [
	path('', AuthView.as_view()),
	path('index/', Cpanel.as_view(), name='cpanel'),
    path('admin/', admin.site.urls),
]
