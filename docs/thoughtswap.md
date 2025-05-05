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

