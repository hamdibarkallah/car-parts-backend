from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, UserProfileView, PartListCreateView, PartDetailView

router = DefaultRouter()

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Part CRUD endpoints
    path('parts/', PartListCreateView.as_view(), name='part-list-create'),
    path('parts/<int:pk>/', PartDetailView.as_view(), name='part-detail'),
] + router.urls
