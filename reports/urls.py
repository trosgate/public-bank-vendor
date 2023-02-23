from django.urls import path, re_path
from . import views

app_name = 'reports'

urlpatterns = [
    path('monitor', views.monitor, name='monitor'), 
    path('reports', views.excel_or_csv, name='excel_or_csv'), 
    path('excelcsv', views.fetch_excel_or_csv, name='fetch_excel_or_csv'), 
    path('allexcelcsv', views.fetch_allbranches, name='fetch_allbranches'), 
    path('customexcelcsv', views.custom_excel_or_csv, name='custom_excel_or_csv'), 
    path('fetchcustomexcelcsv', views.custom_fetch_excel_or_csv, name='custom_fetch_excel_or_csv'), 
    path('allbranchesexcelcsv', views.branches_excel_or_csv, name='branches_excel_or_csv'), 
    path('ticket-by-vendor', views.ticket_by_vendor, name='ticket_by_vendor'), 
    path('ticket-by-status', views.ticket_by_status, name='ticket_by_status'), 
    path('ticket-by-comparison', views.ticket_by_vendor_comparison, name='ticket_by_vendor_comparison'), 
    path('ticket-by-hours-worked', views.ticket_by_hours_worked, name='ticket_by_hours_worked'), 
    path('ticket-by-response', views.ticket_by_response, name='ticket_by_response'), 

]

htmx_urlpatterns = [
    # path('ticket-list/', views.ticket_list, name='ticket_list'), 

]

urlpatterns += htmx_urlpatterns
