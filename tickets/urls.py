from django.urls import path, re_path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.create_ticket, name='create_ticket'), 
    path('unassigned', views.unassigned_ticket_list, name='unassigned_list'), 
    path('assigned', views.assigned_ticket_list, name='assigned_list'), 
    path('started', views.started_list, name='started_list'), 
    path('deffered', views.deffered_list, name='deffered_list'), 
    path('reopened', views.reopened_list, name='reopened_list'), 
    path('closed', views.closed_list, name='closed_list'), 
    path('my-tickets', views.my_ticket_list, name='my_ticket_list'), 
    path('remarks', views.recommendations, name='recommendations'), 
    path('preview/<int:ticket_id>/<slug:ticket_slug>', views.ticket_preview, name='ticket_preview') 
]

htmx_urlpatterns = [
    path('ticket-list/', views.ticket_list, name='ticket_list'), 
    path('search-ticket/', views.search_ticket, name='search_ticket'), 
    path('closed-search/', views.search_closed_ticket, name='search_closed_ticket'), 
    path('remarks-search/', views.search_recommendation, name='search_recommendation'), 
    path('remove_message/', views.remove_message, name='remove_message'), 
    path('assign/<int:ticket_id>/', views.assign_ticket, name='assign_ticket'),
    path('detail/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('arrival/<int:ticket_id>/', views.confirm_arrival, name='confirm_arrival'),
    path('close/<int:ticket_id>/', views.close_ticket, name='close_ticket'),
    path('deffer/<int:ticket_id>/', views.deffer_ticket, name='deffer_ticket'),
    path('reopen/<int:ticket_id>/', views.reopen_ticket, name='reopen_ticket'),
    path('remark/<int:ticket_id>/', views.ticket_remark, name='ticket_remark'),
    path('recall/', views.recall_ticket, name='recall_ticket'),

]

urlpatterns += htmx_urlpatterns
