import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

from .models import Course, Enrollment, Session, Prompt, PromptUse, Thought

User = get_user_model()


class ThoughtSwapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_code = self.scope["url_route"]["kwargs"]["course_code"]
        self.room_group_name = f"thoughtswap_{self.course_code}"

        self.user = self.scope["user"]
        self.course = await self.get_course_by_code(self.course_code)
        self.session = await self.get_active_session(self.course)

        if self.course and self.session:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

            await self.accept()

            if self.session.is_swapping:
                await self.send(text_data=json.dumps({
                    "type": "session_phase",
                    "phase": "swapping"
                }))

            active_prompt_use = await self.get_active_prompt_use(self.session)
            if active_prompt_use:
                prompt_content = await self.get_prompt_content(active_prompt_use)
                await self.send(text_data=json.dumps({
                    "type": "new_prompt",
                    "content": prompt_content,
                    "prompt_id": active_prompt_use.id,
                }))
        else:
            await self.close()



    @database_sync_to_async
    def is_facilitator(self):
        return self.course.creator == self.user

    @database_sync_to_async
    def get_prompt_content(self, prompt_use):
        return prompt_use.prompt.content

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")
        

        if msg_type == "disperse_prompt" and await self.is_facilitator():
            content = data.get("content")
            prompt = await self.create_prompt(content)
            prompt_use = await self.create_prompt_use(prompt)
            prompt_content = await self.get_prompt_content(prompt_use)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_prompt",
                    "content": prompt_content,
                    "prompt_id": prompt_use.id,
                }
            )

        elif msg_type == "submit_thought":
            content = data.get("content")
            thought = await self.store_thought(content)
            print("About to send via WebSocket:", {
                "type": "new_thought",
                "content": thought.content,
                "prompt_id": thought.prompt_use.id,
            })
            if thought:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_thought",
                        "content": thought.content,
                        "prompt_id": thought.prompt_use_id,
                    },
                )
        
        elif msg_type == "swap_responses":
            print("Swapping responses!!!!")

            self.session.is_swapping = True
            await database_sync_to_async(self.session.save)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "session_phase",
                    "phase": "swapping"
                }
            )

            await self.swap_responses()

        elif msg_type == "prompt_bank":
            print("Getting prompt bank data\n\n\n")
            prompts = await database_sync_to_async(list)(
                Prompt.objects.filter(author=self.user, in_bank=True).values("id", "content")
            )
            print("Prompts:", prompts)
            await self.send(text_data=json.dumps({
                "type": "prompt_bank_data",
                "prompts": prompts
            }))

        elif msg_type == "send_bank_prompt":
            prompt_id = data.get("prompt_id")
            prompt = await database_sync_to_async(Prompt.objects.get)(id=prompt_id)
            prompt_use = await self.create_prompt_use(prompt)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_prompt",
                    "content": prompt.content,
                    "prompt_id": prompt_use.id,
                }
            )



    async def broadcast_prompt(self, event):
        await self.send(
            text_data=json.dumps({"type": "new_prompt", "content": event["content"]})
        )

    async def new_thought(self, event):
        if await self.is_facilitator():
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "new_thought",
                        "content": event["content"],
                        "prompt_id": event["prompt_id"],
                    }
                )
            )


    @database_sync_to_async
    def get_course_by_code(self, code):
        try:
            return Course.objects.get(join_code=code)
        except Course.DoesNotExist:
            return None

    @database_sync_to_async
    def get_active_session(self, course):
        return course.sessions.filter(state="a").first()

    @database_sync_to_async
    def get_active_prompt_use(self, session):
        return PromptUse.objects.filter(session=session, is_active=True).first()

    # @database_sync_to_async
    # def create_prompt_and_use(self, content):
    #     prompt = Prompt.objects.create(author=self.user, content=content)
    #     PromptUse.objects.filter(session=self.session).update(is_active=False)
    #     prompt_use = PromptUse.objects.create(
    #         prompt=prompt, session=self.session, is_active=True
    #     )
    #     return prompt_use

    @database_sync_to_async
    def create_prompt(self, content):
        return Prompt.objects.create(author=self.user, content=content)

    @database_sync_to_async
    def create_prompt_use(self, prompt):
        PromptUse.objects.filter(session=self.session).update(is_active=False)
        return PromptUse.objects.create(prompt=prompt, session=self.session, is_active=True)


    @database_sync_to_async
    def get_thoughts(self, prompt_use):
        return list(Thought.objects.filter(prompt_use=prompt_use))

    @database_sync_to_async
    def get_all_participant_users(self, course):
        print("Getting all participant users")
        enrollments = Enrollment.objects.filter(course_id=course.id, role='s').select_related("user")
        print("Enrollments:", enrollments)
        return [enrollment.user for enrollment in enrollments]

    @database_sync_to_async
    def store_thought(self, content):
        active = (
            PromptUse.objects.filter(session=self.session)
            .order_by("-created_at")
            .first()
        )
        if active:
            thought = Thought.objects.create(
                prompt_use=active,
                author=self.user,
                content=content
            )
            return Thought.objects.select_related("prompt_use").get(id=thought.id)
        return None



    async def swap_responses(self):
        print("Swapping responses inside function")
        user = self.scope["user"]
        course = self.course 
        # pass in session already being used 
        session = await self.get_active_session(course)
        print("Session:", session)
        print("Course:", course.id)

        if not session:
            return

        latest_prompt_use = await self.get_active_prompt_use(session)
        if not latest_prompt_use:
            return

        thoughts = await self.get_thoughts(latest_prompt_use)
        if len(thoughts) < 2:
            return # TODO: maybe return an error message object? maybe like the channels/js version of https://docs.djangoproject.com/en/5.1/ref/contrib/messages/

        student_ids_who_authored = list(set(t.author_id for t in thoughts))
        print("Student IDs:", student_ids_who_authored)
        # All students may include students who are not in the current session (great for testing actually)
        # What happens if someone joins late? I know we want them to get something to discuss but how?
        # - if there were more sresponses than students, they shoud get one that hasnt been seen before 
        # - if there are more students than responses, they should get a random one
        all_students = await self.get_all_participant_users(course)
        print("All students:", all_students)

        if len(student_ids_who_authored) < 2 or len(all_students) < 2:
            print("Not enough students to swap responses.") 
            return

        responses = [t for t in thoughts]
        print("Responses:", responses)
        distribution_pool = responses[:]
        print("Distribution pool:", distribution_pool)


        # make sure its not 2+ responses from the same student
        # duplicate enough thoughts to have 1 available for every enrolled student
        while len(distribution_pool) < len(all_students):
            distribution_pool.append(random.choice(responses))

        random.shuffle(distribution_pool)

        print("Shuffled distribution pool:", distribution_pool)

        student_response_map = {}
        for student in all_students:
            temp_pool = distribution_pool[:]
            print(f"Handling student: {student.id}")
            assigned = random.choice(temp_pool)
            while assigned.author_id == student.id:
                print(f"Assigned response is from the same student: {assigned.content}")
                temp_pool.remove(assigned)
                assigned = random.choice(distribution_pool)
            student_response_map[student.id] = assigned
            distribution_pool.remove(assigned)
        
        print("Student response map:", student_response_map)

        for student_id, response in student_response_map.items():
            print(f"Sending to user_{student_id}: {response.content}")
            await self.channel_layer.group_send(
                f"user_{student_id}",
                {
                    "type": "distribute_thought",
                    "content": response.content
                }
            )

    async def distribute_thought(self, event):
        print("Inside distribute_thought, sending to client:", event["content"])
        await self.send(text_data=json.dumps({
            "type": "received_thought",
            "content": event["content"]
        }))

    async def session_phase(self, event):
        await self.send(text_data=json.dumps({
            "type": "session_phase",
            "phase": event["phase"]
        }))


    async def new_prompt(self, event):
        content = event["content"]
        prompt_id = event["prompt_id"]

        await self.send(text_data=json.dumps({
            "type": "new_prompt",
            "content": content,
            "prompt_id": prompt_id,
        }))





