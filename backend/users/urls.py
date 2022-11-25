from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'users'


urlpatterns = [
	
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
	
]