from django.urls import path
from backend.apps.community.views import PostCRUD, PostListView, PostDetailView, LikePost

urlpatterns = [
    path("post/<int:pk>/", PostCRUD.as_view(), name="post CRUD"),
    path("post/<str:country>/", PostListView.as_view(), name="List of posts"),
    path("post/<int:pk>/details/", PostDetailView.as_view(), name="Post details"),
    path("post/<int:pk>/like/", LikePost.as_view(), name="like post"),
]