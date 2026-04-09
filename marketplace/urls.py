from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserProfileView,
    PartListCreateView, PartDetailView,
    CartView, CartAddItemView, CartItemUpdateView,
    OrderListCreateView, OrderDetailView,
)

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
    
    # Cart endpoints
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add-item'),
    path('cart/items/<int:item_id>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    
    # Order endpoints
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
] + router.urls
