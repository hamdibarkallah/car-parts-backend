from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserProfileView,
    PartListCreateView, PartDetailView,
    CartView, CartAddItemView, CartItemUpdateView,
    OrderListCreateView, OrderDetailView,
    BrandListCreateView, ModelListCreateView, ModelYearListCreateView, EngineListCreateView,
    CategoryListCreateView, CategoryDetailView,
    PartImageListCreateView, PartImageDeleteView,
)

router = DefaultRouter()

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Vehicle hierarchy endpoints
    path('brands/', BrandListCreateView.as_view(), name='brand-list-create'),
    path('models/', ModelListCreateView.as_view(), name='model-list-create'),
    path('model-years/', ModelYearListCreateView.as_view(), name='modelyear-list-create'),
    path('engines/', EngineListCreateView.as_view(), name='engine-list-create'),
    
    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Part CRUD endpoints
    path('parts/', PartListCreateView.as_view(), name='part-list-create'),
    path('parts/<int:pk>/', PartDetailView.as_view(), name='part-detail'),
    
    # Part Image endpoints
    path('parts/<int:part_id>/images/', PartImageListCreateView.as_view(), name='part-image-list-create'),
    path('images/<int:pk>/', PartImageDeleteView.as_view(), name='part-image-delete'),
    
    # Cart endpoints
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add-item'),
    path('cart/items/<int:item_id>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    
    # Order endpoints
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
] + router.urls
