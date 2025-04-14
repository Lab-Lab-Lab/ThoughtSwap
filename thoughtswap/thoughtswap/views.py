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


def get_latest_session(courses):
    for course in courses:
        # If you used related_name="sessions" in your Session model:
        course.latest_session = course.sessions.order_by("-id").first()

        # If you did NOT use related_name, uncomment the line below and comment the one above:
        # course.latest_session = course.session_set.order_by('-id').first()


@login_required  # FIXME this would check the enrollment's ROLE to decide if this is visible
def teacher_dashboard(request):
    facilitator = request.user
    courses = Course.objects.filter(creator=facilitator)
    get_latest_session(courses)

    sessions = Session.objects.filter(course__creator=facilitator).select_related(
        "course"
    )

    course_id = request.GET.get("course_id")
    selected_course = None
    students = []

    if course_id:
        selected_course = get_object_or_404(Course, id=course_id, creator=facilitator)
        students = User.objects.filter(
            enrollment__course=selected_course, enrollment__role="s"
        )

    if request.method == "POST":
        print("info", request.POST)
        session_id = request.POST.get("course_session_id")
        session = Session.objects.get(id=session_id)
        session.state = request.POST.get("session_state")
        session.save()

        get_latest_session(courses)

    context = {
        "courses": courses,
        "students": students,
        "selected_course": selected_course,
        "sessions": sessions,
    }

    return render(request, "thoughtswap/teacher_dashboard.html", context)


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

@login_required
def thoughtswap_room(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)
    session = course.sessions.filter(state="a").first()

    if not session:
        return render(request, "thoughtswap/facilitator_session.html", {
            "course": course,
            "error": "No active session."
        })

    if request.user == course.creator:
        prompt_data = []
        for pu in session.promptuse_set.select_related('prompt').prefetch_related('thought_set').order_by('-created_at'):
            prompt_data.append({
                "prompt": pu.prompt.content,
                "prompt_use_id": pu.id,
                "thoughts": [t.content for t in pu.thought_set.all()]
            })


        return render(
            request,
            "thoughtswap/facilitator_session.html",
            {
                "course": course,
                "session": session,
                "session_data": prompt_data,
            },
        )
    else:
        return render(
            request,
            "thoughtswap/participant_session.html",
            {
                "course": course,
                "session": session,
            },
        )


