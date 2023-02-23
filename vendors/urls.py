from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [

    path('team-chat', views.teamchat, name='teamchat'),
    path('team/chatroom', views.teamchatroom, name='teamchatroom'),
    path('profile/<str:short_name>', views.my_profile, name='my_profile'),
    path('member/<str:short_name>', views.vendor_profile, name='vendor_profile'),
    path('team/<slug:vendor_slug>', views.vendor_detail, name='vendor_detail'),
]

htmx_urlpatterns = [
    path('upgrade/', views.vendor_upgrade_downgrade, name='vendor_team_upgrade'),
    path('modify/<str:short_name>', views.modify_profile, name='modify_profile'),
    path('photo/<str:short_name>', views.upload_photo, name='upload_photo'),

]

urlpatterns += htmx_urlpatterns
