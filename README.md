# ThoughtSwap

## Project Overview

Thought Swap is a discussion facilitation app where a facilitator sends prompts to participants, who submit anonymous responses that are later redistributed for small-group discussion.

**Github repository:** https://github.com/Lab-Lab-Lab/ThoughtSwap

**Key technologies:**
- Django (backend)
- Django Channels (WebSocket communication)
- HTML, JavaScript (frontend templates)

**Core features:**
- Prompt creation, management, and reuse
- Anonymous response submission
- Response “swap” feature for small-group discussion
- Facilitator dashboard with course and session controls

## What Has Been Accomplished

- Set up Django backend and database models
  - Course, Enrollment, Prompt, Session, PromptUse, Thought
- Integrated WebSocket support (channels) for real-time updates to both the facilitator and participant
- Facilitators can switch their course from three states: Active, Draft, and Inactive
- Facilitators can create prompts ahead of time
- Facilitators can send prompts to participants to respond to
- Facilitators can disperse responses using the “swap” feature
- Participants can join a new course via a room code
- Participants can view the current prompt
- Participants can respond to the current prompt
- Participants can receive a thought to discuss

## Key Decisions Made (with Explanations)

- **What is PromptUse**  
  The `PromptUse` model acts as a connection between a prompt and a session. It allows the same prompt to be reused across multiple sessions while keeping track of responses specific to each session. This design improves flexibility by avoiding duplicate prompt entries and enables better tracking of when and where prompts were used.

- **Why there are different HTML templates**  
  I separated the HTML templates into `facilitator_session.html`, `participant_session.html`, and `teacher_dashboard.html` to clearly divide the interfaces by user role. Each role has very different needs:

- **Intended functionality of restrictions around swapping**  
  When swapping responses, the system should ensure that:
  - Each participant receives a response from someone else (not their own)
  - There must be at least two active student who have responded
  - If there are more students than responses, responses are randomly duplicated


## Known Issues or Bugs

- Swapping thoughts needs to be more robust
- Late joiners need to be fully addressed
- Safety and robustness of user contributions has not been fully tested

## Next Steps

- Front-end styling + UX
- Facilitator's ability to create a new course
- Facilitator's ability to create a new session
- “Demo mode,” where the facilitator and/or participants need not create a lasting account
- Functionality for late joiners
- When swapping: if one author is more prolific for a certain prompt, before assigning all their thoughts to others, first ensure that each author's thoughts are assigned (and specifically to authors (users who have submitted for this prompt))
- Somehow allow for the participants indicate their thoughts about the distributed thought
- Start having semantic analysis
- Find some way to track how the discussion went (Form for after the discussion?)
- Participant view for the facilitator
- Offer rich text editor in prompt composition and thought composition

## Important Files / Code to Know

- `facilitator_session.html`
  This is the main interface for facilitators. It allows them to:
  - Write and send prompts
  - Swap anonymous participant responses
  - Access the prompt bank
  - View active and past prompts
  It also includes WebSocket logic to handle live updates from the server.

- `participant_session.html`
  This is the participant view during a session. Participants can:
  - See the current prompt
  - Submit their responses
  - Receive a swapped response to discuss
  It connects to the WebSocket server to listen for prompt updates and swapped thoughts.

- `teacher_dashboard.html`
  This is the dashboard where teachers manage their courses and sessions.
  - Shows all enrolled courses
  - Lets the teacher switch session states (Active, Inactive, Draft)
  - Displays and manages the prompt bank, including adding new prompts

- `models.py`
  Contains all the Django data models, including:
  - Course, Enrollment, Prompt, Session, PromptUse, Thought

- `views.py`
  Contains the Django views that:
  - Handle requests and render the pages
  - Manage course state changes
  - Provide data to the templates

- `consumers.py`
  Contains the Django Channels consumers that:
  - Handle WebSocket connections
  - Receive and send real-time events like new prompts, new thoughts, swaps, and prompt bank data


# ThoughtSwap as an instance of Cookiecutter Django

A project,

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy thoughtswap

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. If you choose to use [Mailpit](https://github.com/axllent/mailpit) when generating the project a local SMTP server with a web interface will be available.

1.  [Download the latest Mailpit release](https://github.com/axllent/mailpit/releases) for your OS.

2.  Copy the binary file to the project root.

3.  Make it executable:

        $ chmod +x mailpit

4.  Spin up another terminal window and start it there:

        ./mailpit

5.  Check out <http://127.0.0.1:8025/> to see how it goes.

Now you have your own mail server running locally, ready to receive whatever you send it.

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.
