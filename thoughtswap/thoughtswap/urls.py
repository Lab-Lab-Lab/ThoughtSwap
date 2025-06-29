from django.urls import path
from . import views

urlpatterns = [
    path("prompts/", views.prompt_list, name="prompt_list"),
    path("teacher_dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("join/", views.join_course, name="join_course"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("<str:join_code>/", views.thoughtswap_room, name="active_room"),
]
