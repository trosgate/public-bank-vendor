from django.urls import path, re_path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('requisition', views.requisition, name='requisition'), 
    path('create_requisition', views.create_requisition, name='create_requisition'), 
    path('detail/<int:pk>/', views.inventory_detail, name='inventory_detail'), 
    path('preview/<int:pk>/<slug:inventory_slug>', views.inventory_preview, name='inventory_preview'), 

]

htmx_urlpatterns = [
    path('issue_inventory/<int:pk>/', views.issue_inventory, name='issue_inventory'), 

]

urlpatterns += htmx_urlpatterns
