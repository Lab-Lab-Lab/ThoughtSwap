from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

from .models import Course, Session, Prompt, PromptUse, Thought

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
            await self.accept()

            active_prompt_use = await self.get_active_prompt_use(self.session)
            if active_prompt_use:
                prompt_content = await self.get_prompt_content(active_prompt_use)
                await self.send(text_data=json.dumps({
                    "type": "new_prompt",
                    "content": prompt_content,
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
            prompt_use = await self.create_prompt_and_use(content)
            prompt_content = await self.get_prompt_content(prompt_use)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_prompt",
                    "content": prompt_content,
                }
            )

        elif msg_type == "submit_thought":
            content = data.get("content")
            thought = await self.store_thought(content)
            if thought:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_thought",
                        "content": thought.content,
                    },
                )

    async def broadcast_prompt(self, event):
        await self.send(
            text_data=json.dumps({"type": "new_prompt", "content": event["content"]})
        )


    async def new_thought(self, event):
        if await self.is_facilitator():
            await self.send(
                text_data=json.dumps(
                    {"type": "new_thought", "content": event["content"]}
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

    @database_sync_to_async
    def create_prompt_and_use(self, content):
        prompt = Prompt.objects.create(author=self.user, content=content)
        PromptUse.objects.filter(session=self.session).update(is_active=False)
        prompt_use = PromptUse.objects.create(
            prompt=prompt, session=self.session, is_active=True
        )
        return prompt_use

    @database_sync_to_async
    def store_thought(self, content):
        active = (
            PromptUse.objects.filter(session=self.session)
            .order_by("-created_at")
            .first()
        )
        if active:
            return Thought.objects.create(
                prompt_use=active, author=self.user, content=content
            )
        return None
