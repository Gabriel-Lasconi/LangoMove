from django.urls import path

from apps.users.views import CustomLoginView, dashboard_view, logout_view, register_view
from .views.dashboard import dashboard_view, create_class_participation_view
urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("classes/create/", create_class_participation_view, name="create-class-participation"),

]
