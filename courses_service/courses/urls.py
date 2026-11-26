from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, SessionViewSet
from config.consul_registry import register_with_consul
import threading

# Register with Consul in background
threading.Thread(target=register_with_consul, daemon=True).start()

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'sessions', SessionViewSet, basename='session')

urlpatterns = router.urls
