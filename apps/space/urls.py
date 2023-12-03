from django.urls import path

from apps.space.views import ListOfSpaces, CreateSpace, EditSpace, DeleteSpace, AddMemberToSpace

urlpatterns = [
    path("create_space/", CreateSpace.as_view(), name="create_space"),
    path("my_spaces/", ListOfSpaces.as_view(), name="spaces_list"),
    path("my_spaces/<int:pk>/", EditSpace.as_view(), name="edit_space"),
    path("delete_space/<int:pk>/", DeleteSpace.as_view(), name="delete_space"),
    path("my_spaces/<int:pk>/add_member/", AddMemberToSpace.as_view(), name="add_member")
]
