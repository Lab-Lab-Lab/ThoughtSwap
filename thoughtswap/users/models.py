import random, string
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models


def generate_unique_code():
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    # Need a check to see if the code already exists
    return code


class User(AbstractUser):
    """
    Default custom user model for ThoughtSwap.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class Course(models.Model):
    """
    Model representing a course.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name="courses")
    code = models.CharField(max_length=6, unique=True, default=generate_unique_code)


class Prompt(models.Model):
    """
    Model representing a prompt.
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()


class Thought(models.Model):
    """
    Model representing a thought.
    """

    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
