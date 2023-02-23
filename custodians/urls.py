from django.urls import path
from . import views

app_name = 'custodians'

urlpatterns = [

    path('<slug:branch_slug>', views.branch_page, name='branch_page'),
    path('profile/<str:short_name>', views.my_profile, name='my_profile'),
    path('<int:request_id>/<slug:request_slug>', views.complaint_detail, name='complaint_detail'),

]
htmx_urlpatterns = [
    path('modify/<str:short_name>', views.modify_profile, name='modify_profile'),
    path('photo/<str:short_name>', views.upload_photo, name='upload_photo'),
    path('reply/<int:request_id>', views.helpdesk_reply, name='helpdesk_reply'),
    path('reroute/<int:request_id>', views.route_to_branch, name='reroute'),

]
urlpatterns += htmx_urlpatterns