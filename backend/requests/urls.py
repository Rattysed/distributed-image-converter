from django.urls import path

from .views import TestingView


app_name = "requests"


urlpatterns = [
    path('testing/', TestingView.as_view()),
]
