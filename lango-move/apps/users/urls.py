from django.urls import path

from .views.auth import (
    activate_account_view,
    login_view,
    logout_view,
    register_view,
    registration_pending_view,
    resend_activation_view,
)
from .views.dashboard import dashboard_view, volunteer_dashboard_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("volunteer-dashboard/", volunteer_dashboard_view, name="volunteer-dashboard"),

    path("activate/<uidb64>/<token>/", activate_account_view, name="activate-account"),
    path("activation-pending/<int:user_id>/", registration_pending_view, name="registration-pending"),
    path("resend-activation/", resend_activation_view, name="resend-activation"),
]