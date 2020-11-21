from django.conf.urls import url
from django.urls import path
from creds_handler import register
import django.views

from . import views

urlpatterns = [
    url('register/$', register.login, name='login'),
    url('movies/$', views.movies, name='movies'),
    url('collection/$', views.collection, name='collection'),
    url('request-count/$', views.request_count, name='request_count'),
    url('request-count/reset/$', views.reset_request_count, name='reset_request_count'),
    path('collection/<str:collection_id>/', views.update_collections, name='update_collections')
]