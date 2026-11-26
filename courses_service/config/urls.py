from django.contrib import admin
from django.urls import path, include
from courses.views import home_view, create_session_view, session_details_view, admin_session_list_view, coach_session_update_view, coach_session_delete_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend Routes
    path('', home_view, name='home'),
    path('courses/create-session/', create_session_view, name='create_session'),
    path('courses/session/<int:session_id>/', session_details_view, name='session_details'),
    path('courses/session/<int:session_id>/edit/', coach_session_update_view, name='session_edit'),
    path('courses/session/<int:session_id>/delete/', coach_session_delete_view, name='session_delete'),
    path('gym-admin/sessions/', admin_session_list_view, name='admin-session-list'),

    # API Routes
    path('api/', include('courses.urls')),
    
    # Also support /api/sessions/ if needed by other services, but router exposes it via first include
    # Just keeping existing structure
]

