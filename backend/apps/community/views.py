from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from backend.apps.community.permissions import IsEmployee
from backend.apps.community.serializers import PostCreateingSerializer, PostListSerializer, PostDetailSerializer
from backend.apps.community.models import Post

class PostCRUD(APIView):
    permission_classes = (IsEmployee,IsAuthenticated)

   
    def post(self, request, *args, **kwargs) -> Response:
        """creates new post """
        
        try:
            serializer = PostCreateingSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Post successfully created!"}, status=status.HTTP_201_CREATED)
            
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:    
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk:int, *args, **kwargs) -> Response:
        try:

            post = Post.objects.get(pk=pk)
            serializer = PostCreateingSerializer(post, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Post has been successfully updated"}, status=status.HTTP_200_OK)
            
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk:int, *args, **kwargs) -> Response:
        try:

            post = Post.objects.get(pk=pk)
            serializer = PostCreateingSerializer(post, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Post has been successfully updated"}, status=status.HTTP_200_OK)
            
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk:int, *args, **kwargs) -> Response:
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response({"message":"Post has been successfully deleted!"}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist as e:
            return Response({"error": f"Post with id {pk} does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostListSerializer
    
    def get(self, request, country:str, *args, **kwargs):
        """returns list of all the post of specific country in a concise form"""
        
        try:
            queryset = Post.objects.filter(country=country)
            serializer = PostListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PostDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
            post.views_counter += 1
            post.save()

            serializer = PostDetailSerializer(post) 
            return Response({"post": serializer.data}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": f"Post with id {pk} does not exist!"}, status=status.HTTP_404_NOT_FOUND)
    

class LikePost(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, pk:int, *args, **kwargs):
        try:

            post = Post.objects.get(pk=pk)
            if request.user in post.likes.all():
                return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
            post.likes.add(request.user)
            
            return Response({"message": f"You have been successfully liked the post with id: {pk}!"}, status=status.HTTP_200_OK)
        
        except Post.DoesNotExist:
            return Response({"error": f"Post with id {pk} does not exist!"}, status=status.HTTP_404_NOT_FOUND)