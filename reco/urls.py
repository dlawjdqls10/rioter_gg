from django.urls import path
from reco import views


urlpatterns = [
    path('', views.index, name='index'),
    path('recommend', views.recommend, name='recommend'),
]
