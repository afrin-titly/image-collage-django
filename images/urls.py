from django.urls import path
from .views import UserList, ImageCollage

urlpatterns = [
    path('users/', UserList.as_view()),
    path('user-image/', ImageCollage.as_view()),
]