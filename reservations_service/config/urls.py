from django.contrib import admin
from django.urls import path, include
from reservations.views import my_reservations_view, book_view, cancel_frontend_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend Routes
    path('reservations/', my_reservations_view, name='my_reservations'),
    path('reservations/book/<int:session_id>/', book_view, name='book_session'),
    path('reservations/cancel/<int:pk>/', cancel_frontend_view, name='cancel_reservation'),

    # API Routes
    path('api/reservations/', include('reservations.urls')),
]
