from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class IsAdminOrReadOnly(AllowAny):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class CategoryListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "success": True,
            "message": "Categories fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "success": True,
                "message": "Category created successfully.",
                "data": CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Failed to create category.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({
                "success": False,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response({
            "success": True,
            "message": "Category retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({
                "success": False,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "success": True,
                "message": "Category updated successfully.",
                "data": CategorySerializer(category).data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Failed to update category.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({
                "success": False,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({
            "success": True,
            "message": "Category deleted successfully."
        }, status=status.HTTP_200_OK)


class ProductListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Product.objects.select_related('category').all()

        # Query Filters
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        category_param = request.query_params.get('category', '').strip()
        if category_param:
            if category_param.isdigit():
                queryset = queryset.filter(category_id=int(category_param))
            else:
                queryset = queryset.filter(
                    Q(category__slug=category_param) | Q(category__name__iexact=category_param)
                )

        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        in_stock = request.query_params.get('in_stock')
        if in_stock in ['true', '1', 'True']:
            queryset = queryset.filter(stock__gt=0)

        featured = request.query_params.get('featured')
        if featured in ['true', '1', 'True']:
            queryset = queryset.filter(is_featured=True)

        # Sorting
        sort = request.query_params.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort == 'stock_low':
            queryset = queryset.order_by('stock')
        else: # newest
            queryset = queryset.order_by('-created_at')

        serializer = ProductSerializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Products fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "success": True,
                "message": "Product created successfully.",
                "data": ProductSerializer(product).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Failed to create product.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.select_related('category').get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response({
            "success": True,
            "message": "Product retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "success": True,
                "message": "Product updated successfully.",
                "data": ProductSerializer(product).data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Failed to update product.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({
            "success": True,
            "message": "Product deleted successfully."
        }, status=status.HTTP_200_OK)
