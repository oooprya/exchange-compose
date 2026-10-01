from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/api/balances/", views.dashboard_balances_api,
         name="dashboard_balances_api"),
    path("shift/<int:shift_id>/switch_cashdesk/",
         views.switch_cashdesk, name="shift_switch_cashdesk"),
]
