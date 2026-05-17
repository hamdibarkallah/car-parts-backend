from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from marketplace.models import Order, OrderItem, Supplier
from marketplace.serializers import OrderSerializer, OrderListSerializer


class SupplierOrderListView(APIView):
    """
    List orders for the current supplier
    GET: List all orders that contain items from this supplier
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="List all orders that contain items from the current supplier",
        operation_summary="List Supplier Orders",
        tags=['Supplier Orders'],
        responses={
            200: OrderListSerializer(many=True),
            403: "Forbidden - Supplier access required",
        }
    )
    def get(self, request):
        if not hasattr(request.user, 'supplier_profile'):
            return Response({'error': 'Only suppliers can view their orders'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = request.user.supplier_profile
        
        # Get orders that contain items from this supplier
        orders = Order.objects.filter(
            items__supplier=supplier
        ).distinct().order_by('-created_at')
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class SupplierOrderDetailView(APIView):
    """
    Get details of a specific order for supplier
    GET: Retrieve order details for supplier validation
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get detailed information about a specific order for supplier",
        operation_summary="Get Supplier Order Details",
        tags=['Supplier Orders'],
        responses={
            200: OrderSerializer,
            403: "Forbidden - Supplier access required",
            404: "Not Found - Order not found",
        }
    )
    def get(self, request, pk):
        if not hasattr(request.user, 'supplier_profile'):
            return Response({'error': 'Only suppliers can view orders'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = request.user.supplier_profile
        
        try:
            order = Order.objects.prefetch_related('items__part', 'items__supplier').get(
                id=pk, items__supplier=supplier
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class SupplierOrderValidationView(APIView):
    """
    Validate or reject an order for supplier
    POST: Approve or reject order with optional notes
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Approve or reject an order with optional notes",
        operation_summary="Validate/Reject Order",
        tags=['Supplier Orders'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['approve', 'reject'],
                    description='Action to perform on the order'
                ),
                'notes': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional notes from supplier'
                )
            },
            required=['action']
        ),
        responses={
            200: OrderSerializer,
            400: "Bad Request - Invalid action or order already processed",
            403: "Forbidden - Supplier access required",
            404: "Not Found - Order not found",
        }
    )
    def post(self, request, pk):
        if not hasattr(request.user, 'supplier_profile'):
            return Response({'error': 'Only suppliers can validate orders'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = request.user.supplier_profile
        
        try:
            order = Order.objects.prefetch_related('items__supplier').get(
                id=pk, items__supplier=supplier
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if order can be validated
        if order.status not in ['SUPPLIER_PENDING']:
            return Response(
                {'error': f'Order cannot be validated. Current status: {order.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = request.data.get('action')
        notes = request.data.get('notes', '')
        
        if action not in ['approve', 'reject']:
            return Response({'error': 'Invalid action. Must be "approve" or "reject"'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status and notes
        if action == 'approve':
            order.status = 'APPROVED'
            order.supplier_notes = notes
            order.updated_at = timezone.now()
            order.save()
            
            # Restore stock for this supplier's items (they were decreased when order was created)
            for item in order.items.filter(supplier=supplier):
                item.part.quantity += item.quantity
                item.part.save()
            
            message = 'Order approved successfully'
            
        elif action == 'reject':
            order.status = 'REJECTED'
            order.supplier_notes = notes
            order.updated_at = timezone.now()
            order.save()
            
            # Restore stock for all items (order is cancelled)
            for item in order.items.all():
                item.part.quantity += item.quantity
                item.part.save()
            
            message = 'Order rejected successfully'
        
        serializer = OrderSerializer(order)
        return Response({
            'message': message,
            'order': serializer.data
        }, status=status.HTTP_200_OK)


class SupplierOrderStatsView(APIView):
    """
    Get order statistics for the current supplier
    GET: Get counts of orders by status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get order statistics for the current supplier",
        operation_summary="Get Supplier Order Stats",
        tags=['Supplier Orders'],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'pending_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'approved_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'rejected_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completed_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            ),
            403: "Forbidden - Supplier access required",
        }
    )
    def get(self, request):
        if not hasattr(request.user, 'supplier_profile'):
            return Response({'error': 'Only suppliers can view order statistics'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = request.user.supplier_profile
        
        # Get all orders for this supplier
        orders = Order.objects.filter(items__supplier=supplier).distinct()
        
        stats = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='SUPPLIER_PENDING').count(),
            'approved_orders': orders.filter(status='APPROVED').count(),
            'rejected_orders': orders.filter(status='REJECTED').count(),
            'completed_orders': orders.filter(status__in=['PAID', 'SHIPPED', 'DELIVERED']).count(),
        }
        
        return Response(stats)
