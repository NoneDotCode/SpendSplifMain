from django.urls import path

from apps.space.views import ViewSpace, CreateSpace, EditSpace, DeleteSpace

urlpatterns = [
    path("create_space/", CreateSpace.as_view(), name="create_space"),
    path("my_spaces/", ViewSpace.as_view(), name="spaces_list"),
    path("my_spaces/<int:space_pk>/", EditSpace.as_view(), name="edit_space"),
    path("delete_space/<int:space_pk>/", DeleteSpace.as_view(), name="delete_space")
]
