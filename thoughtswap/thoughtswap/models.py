from django.db import models
import random

JOIN_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ346789abdgjmnpqrt"
JOIN_CODE_LENGTH = 6


def generate_join_code():
    code = "".join(random.choice(JOIN_CODE_CHARS) for _ in range(JOIN_CODE_LENGTH))
    while Course.objects.filter(join_code=code).exists():
        code = "".join(random.choice(JOIN_CODE_CHARS) for _ in range(JOIN_CODE_LENGTH))
    return code


class Course(models.Model):
    title = models.CharField(max_length=100)
    join_code = models.CharField(
        max_length=JOIN_CODE_LENGTH, default=generate_join_code, unique=True
    )
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# since the coockiecutter-django starter code has groups and permissions to go
# along with users, let's rely on those to identify users who are mostly
# "teachers" vs those that are "students" vs. staff vs. sysadmins
class Enrollment(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    USER_ROLES = (
        ("f", "Facilitator"),
        ("s", "Student"),
    )

    role = models.CharField(
        max_length=1,
        choices=USER_ROLES,
        blank=True,
        default="s",
        help_text="user role in course",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.course}"


class Prompt(models.Model):
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class Session(models.Model):
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="session"
    )

    SESSION_STATE = (
        ("a", "Active"),
        ("c", "Closed"),
        ("d", "Draft"),
    )

    state = models.CharField(
        max_length=1,
        choices=SESSION_STATE,
        default="a",
        help_text="Session state",
    )

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.state}"


# 2 use cases:
# 1. prof wants to use this prompt in class tmr, so make it (the Prompt) today so they can just click it in realtime tmr (which would then instantiate the PromptUse). to be fully motivating we actually have to imagine they have 2 prompts in mind for tmr
# 2. prof wants to use the prompt at the beginning of sem and then again at the end
class PromptUse(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    # our docs show begin and end fields, but we don't remember why
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.prompt}"


class Thought(models.Model):
    prompt_use = models.ForeignKey(PromptUse, on_delete=models.CASCADE)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
