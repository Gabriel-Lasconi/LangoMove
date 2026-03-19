from django.urls import path
from apps.schools.views.evaluations import create_class_evaluation_view, my_schools_and_classes_view

urlpatterns = [
    path("evaluations/new/", create_class_evaluation_view, name="create-class-evaluation"),
    path("my-schools/", my_schools_and_classes_view, name="my-schools-and-classes"),
]