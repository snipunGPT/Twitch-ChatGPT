from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
import asyncio
import config
import openai
import credentials

openai.api_key = credentials.MY_API_KEY
  

class NugGPT:
    def __init__(self, app_id, app_secret, user_scope, target_channel):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_scope = user_scope
        self.target_channel = target_channel
        self.twitch = None
        self.chat = None


    async def on_ready(self, ready_event: EventData):
        print('NugGPT')
        await ready_event.chat.join_room(self.target_channel)


    async def on_message(self, msg: ChatMessage):
        print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
        message = msg.text.split()
        if msg.text[0] == '!' and message[0] not in commandList.commands:
            print('found a command to make up!', message[0])
            prompt = message[0]
            with open('personality.txt', 'r+') as personality:
                identity = personality.read()
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Pretend you have the personality of a {identity} and reply to {prompt}."}])
            # Replace the apostrophe'd item below with whatever Twitch channel name (NOT the URL) you want the bot to respond to
            await self.chat.send_message('replace_with_the_twitch_channel_name', completion.choices[0].message.content)

    async def run(self):
        self.twitch = await Twitch(self.app_id, self.app_secret)
        auth = UserAuthenticator(self.twitch, self.user_scope)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, self.user_scope, refresh_token)
        self.chat = await Chat(self.twitch)
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
        self.chat.start()

        try:
            input('press ENTER to stop\n')
        finally:
            self.chat.stop()
            await self.twitch.close()

if __name__ == '__main__':
    APP_ID = config.APP_ID
    APP_SECRET = config.APP_SECRET
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.MODERATOR_MANAGE_BANNED_USERS]
    # Replace the apostrophe'd item below with whatever Twitch channel name (NOT the URL) you want the bot to respond to
    TARGET_CHANNEL = 'replace_with_the_twitch_channel_name'
    # Replace the apostrophe'd item below with your bot's username making sure to include the @ sign
    BOT_NAME = '@replace_with_bot_name'

    nugexe = NugGPT(APP_ID, APP_SECRET, USER_SCOPE, TARGET_CHANNEL, BOT_NAME)
    asyncio.run(nugexe.run())
