from django.urls import path

from .views import RequestView, TestingView


app_name = "requests"


urlpatterns = [
    path('requests/', RequestView.as_view()),
    path('testing/', TestingView.as_view()),
]
