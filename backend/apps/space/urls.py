from django.urls import path

from backend.apps.space.views import (ListOfSpaces, CreateSpace, EditSpace, DeleteSpace, AddMemberToSpace,
                                      RemoveMemberFromSpace, MemberPermissionsEdit, ListOfUsersInSpace,
                                      SpaceBackupListView, SpaceBackupSimulatorView)

urlpatterns = [
    path("create_space/", CreateSpace.as_view(), name="create_space"),
    path("my_spaces/", ListOfSpaces.as_view(), name="spaces_list"),
    path("my_spaces/<int:pk>/", EditSpace.as_view(), name="edit_space"),
    path("delete_space/<int:pk>/", DeleteSpace.as_view(), name="delete_space"),
    path("my_spaces/<int:pk>/add_member/", AddMemberToSpace.as_view(), name="add_member"),
    path("my_spaces/<int:pk>/remove_member/", RemoveMemberFromSpace.as_view(), name="remove_member"),
    path('my_spaces/<int:pk>/edit_member/<int:member_id>/', MemberPermissionsEdit.as_view(),
         name='member-permissions-edit'),
    path("my_spaces/<int:space_pk>/members/", ListOfUsersInSpace.as_view(), name="info-about-space-users"),
    path('my_spaces/<int:space_pk>/backups/', SpaceBackupListView.as_view(), name='space-backups-list'),
    path('my_spaces/<int:space_pk>/simulate-backups/', SpaceBackupSimulatorView.as_view(), name='space-backups-simulate'),

]
