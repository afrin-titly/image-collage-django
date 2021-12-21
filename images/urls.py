from django.urls import path
from .views import UserList, ImageCollage

image_list = ImageCollage.as_view({
    'get':'get',
    'post':'post',
})
urlpatterns = [
    path('users/', UserList.as_view()),
    path('user-image/', image_list),
    path('collage/',ImageCollage.as_view({"get":"make_collage"}))
]