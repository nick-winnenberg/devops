from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("create/", views.owner_create, name="owner_create"),
    path("owner/<int:owner_id>/dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/<int:owner_id>/edit/", views.owner_edit, name="owner_edit"),
    path("owner/<int:owner_id>/delete/", views.owner_delete, name="owner_delete"),
    path("office/<int:owner_id>/create/", views.office_create, name="office_create"),
    path("office/<int:office_id>/dashboard/", views.office_dashboard, name="office_dashboard"),
    path("office/<int:office_id>/edit/", views.office_edit, name="office_edit"),
    path("office/<int:office_id>/create_owner/", views.owner_create_from_office, name="owner_create_from_office"),
    path("office/<int:office_id>/create_employee/", views.employee_create, name="employee_create"),
    path("employee/<int:employee_id>/edit/", views.employee_edit, name="employee_edit"),
    path("delete_employee/<int:employee_id>/", views.employee_delete, name="employee_delete"),
    path("log_call_from_employee/<int:employee_id>/", views.log_call_from_employee, name="log_call_from_employee"),
    path("log_call_from_office/<int:office_id>/", views.log_call_from_office, name="log_call_from_office"),
    path("log_call_from_owner/<int:owner_id>/", views.log_call_from_owner, name="log_call_from_owner"),
    path("report/<int:report_id>/", views.report_dashboard, name="report_dashboard"),
    path("activity/", views.activity_dashboard, name="activity_dashboard"),
]