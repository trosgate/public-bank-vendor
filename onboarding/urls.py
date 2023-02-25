from django.urls import path, re_path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('add_contact', views.add_contact, name='add_contact'), 
    path("mylinks", views.mylinks, name="mylinks"),
    path("restore-application", views.restore_application, name="restore_application"),
    path('compose/<int:website_pk>', views.composer_view, name='message_compose'), 
    path('invitation/<int:tender_pk>/<slug:tender_slug>', views.invitation_detail, name='tender_detail'), 
    path("apply-now/<str:invite_reference>/<slug:tender_slug>", views.application_view, name="application"),
    path("panelist/<str:applicant_name>", views.panelist_view, name="panelist_view"),
    path("ext-scores/<str:reference>/<str:vendor_name>", views.external_scoresheet, name="scoresheet"),
    path("internal-scoresheet/<str:reference>/<str:vendor_name>", views.internal_scoresheet, name="internal_scoresheet"),
    path("master/<str:reference>/<str:vendor_name>", views.master_scoresheet, name="master_scoresheet"),
    path("pool/<str:reference>/<str:vendor_name>", views.pool_review, name="pool_review"),
]

htmx_urlpatterns = [
    path('tender_group', views.tender_group, name='tender_group'), 
    path('search_group', views.search_group, name='search_group'), 
    path('create_contact', views.create_contact, name='create_contact'), 
    path('remove_contact', views.remove_contact, name='remove_contact'), 
    path('message/<int:website_pk>', views.invitemessage_form, name='invitemessage_form'), 
    path('instruction/<int:website_pk>', views.instruction_form, name='instruction_form'), 
    path('composed/<int:website_pk>', views.composed_messages, name='composed_messages'), 
    path('tender_list_nav', views.tender_list_nav, name='tender_list_nav'), 
    path('invitation_list_nav', views.invitation_list_nav, name='invitation_list_nav'), 
    path('ungraded-application', views.ungraded_application_list_nav, name='ungraded_application_list_nav'), 
    path('reviewed-application', views.reviewed_application_list_nav, name='reviewed_application_list_nav'), 
    path('graded-application', views.graded_application_list_nav, name='graded_application_list_nav'), 
    path('bulk-application', views.bulk_application_list_nav, name='bulk_application_list_nav'), 
    path('verify/<int:invite_pk>', views.invitation_link, name='invitation_link'), 
    path('parameter_list_nav', views.parameter_list_nav, name='parameter_list_nav'), 
    path('paramform/<str:reference>', views.param_form, name='param_forms'), 
    path('modifyform/<str:reference>', views.modify_param_form, name='modify_param_form'), 
    path('reminder/<int:application_pk>', views.panel_reminder, name='panel_reminder'), 
    path('param/<str:reference>', views.parameter_detail, name='parameter_detail'), 
    path('create_tender/', views.create_tender, name='create_tender'), 
    path('verify_products', views.verify_products, name="verify_products"),
    path('application_review', views.application_review, name='application_review'), 
    path('meeting/<int:reference>', views.meeting_link, name="meeting_link"),
    path('unlock-panelist/<str:invite_reference>', views.unlock_panelist, name="unlock_panelist"),
    path('internal-panelist/<int:application_pk>', views.panelist, name="add_internal_panelist"),
    path("complete/<str:invite_reference>", views.submit_application, name="submit_application"),
    path("unlock/<str:invite_reference>", views.unlock_application, name="unlock_application"),
    path("gradenow/<str:reference>", views.panel_grading, name="external_grading"),
    
    path("appraisal/<int:application_pk>", views.approval_single, name="approval_single"),
    path("approval/<int:application_pk>/<str:vendor_name>", views.approval, name="approval"),
    path("select_or_unselect_approval", views.select_or_unselect_approval, name="select_or_unselect_approval"),
    path("hide-show", views.hide_application, name="hide_application"),
    path("remove_approval", views.remove_approval, name="remove_approval"),
    path("bulk_approval", views.bulk_approval, name="bulk_approval"),

]

urlpatterns += htmx_urlpatterns
