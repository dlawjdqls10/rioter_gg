from django.urls import path
from reco import views


urlpatterns = [
    path('index', views.index, name='index'),
    path('recommend', views.recommend, name='recommend'),
    path('riot.txt', views.riot, name='riot')
]
