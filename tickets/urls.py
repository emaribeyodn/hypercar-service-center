from django.urls import path
from . import views


urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('get_ticket/<str:service_name>', views.GetTicketView.as_view(), name='get_ticket'),
    path('processing/', views.ProcessingView.as_view(), name='processing'),
    path('next/', views.NextView.as_view(), name='next'),
]