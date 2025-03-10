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
        return self.name


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
