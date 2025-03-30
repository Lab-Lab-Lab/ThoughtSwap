from django.shortcuts import render, redirect, get_object_or_404
from thoughtswap.users.models import User
from .models import Enrollment, Prompt, Course, Session
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import JsonResponse
import json


def prompt_list(request):
    prompts = Prompt.objects.all()
    return render(request, "thoughtswap/prompt_list.html", {"prompts": prompts})


@login_required
def teacher_dashboard(request):
    facilitator = request.user
    courses = Course.objects.filter(creator=facilitator)
    sessions = Session.objects.filter(course__creator=facilitator).select_related(
        "course"
    )

    course_id = request.GET.get("course_id")  # e.g. /dashboard?course_id=3
    selected_course = None
    students = []

    if course_id:
        selected_course = get_object_or_404(Course, id=course_id, creator=facilitator)
        students = User.objects.filter(
            enrollment__course=selected_course, enrollment__role="s"
        )

    context = {
        "courses": courses,
        "students": students,
        "selected_course": selected_course,
        "sessions": sessions,
    }
    return render(request, "thoughtswap/teacher_dashboard.html", context)


def update_session_status(request): 
    print("Received request to update session status\n\n\n\n")
    if request.method == "POST":
        data = json.loads(request.body)
        session_id = data.get("session_id")
        new_status = data.get("status")
        print("Updating session status:", session_id, new_status)

        try:
            session = Session.objects.get(id=session_id)
            session.status = new_status
            session.save()
            return JsonResponse({"message": f"Status updated to {new_status}."})
        except Session.DoesNotExist:
            return JsonResponse({"message": "Session not found."}, status=404)
    return JsonResponse({"message": "Invalid request."}, status=400)


@login_required
def join_course(request):
    error = None

    if request.method == "POST":
        join_code = request.POST.get("join_code")

        try:
            course = Course.objects.get(join_code=join_code)
        except Course.DoesNotExist:
            error = "Invalid join code. Please try again."
            return render(request, "thoughtswap/join_course.html", {"error": error})

        existing = Enrollment.objects.filter(course=course, user=request.user).first()
        if not existing:
            Enrollment.objects.create(
                course=course,
                user=request.user,
                role="s",
                created_at=now(),
                updated_at=now(),
            )
        return redirect("/thoughtswap/dashboard")

    return render(request, "thoughtswap/join_course.html", {"error": error})


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")

    active_sessions = {s.course_id: s.id for s in Session.objects.filter(state="a")}
    print("active_sessions", active_sessions)

    return render(
        request,
        "thoughtswap/dashboard.html",
        {"enrollments": enrollments, "active_sessions": active_sessions},
    )
