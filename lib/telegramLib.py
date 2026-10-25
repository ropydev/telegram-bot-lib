import requests
import uuid
import time
import inspect


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.url = f"https://api.telegram.org/bot{token}"

        bot_info = self.getInfo()

        self.id = bot_info["id"]
        self.name = bot_info["first_name"]
        self.username = bot_info["username"]

        self.callbacks = {}
        self.offset = 0

    def _request(self, method, **kwargs):
        response = requests.post(
            f"{self.url}/{method}",
            timeout=35,
            **kwargs
        )

        response.raise_for_status()
        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                result.get("description", "Error de Telegram")
            )

        return result["result"]

    def getInfo(self) -> dict:
        response = requests.get(
            f"{self.url}/getMe",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                data.get("description", "Error de Telegram")
            )

        return data["result"]

    def message(self, chat_id, text, parse_mode="Markdown"):
        return SendMessage(self, chat_id, text, parse_mode)

    def sendPhoto(self, chat_id, photo, caption = ""):
        return SendPhoto(self, chat_id, photo, caption)

    def sendMessage(self, chat_id, text):
        return self._request(
            "sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            }
        )

    def _register_callback(self, function):
        callback_id = uuid.uuid4().hex
        self.callbacks[callback_id] = function
        return callback_id

    def _handle_callback(self, query):
        callback_id = query.get("data")
        function = self.callbacks.get(callback_id)

        message = query.get("message") or {}
        chat = message.get("chat") or {}
        user = query.get("from") or {}

        context = CallbackContext(
            bot=self,
            chat_id=chat.get("id"),
            user_id=user.get("id"),
            username=user.get("username"),
            name=user.get("first_name", "Desconocido"),
            data=callback_id,
            query=query
        )

        try:
            if function is not None:
                function(context)

        except Exception as error:
            print(f"Error ejecutando callback: {error}")

        finally:
            if not context.answered:
                try:
                    context.answer()
                except (
                    requests.RequestException,
                    RuntimeError,
                    KeyError
                ) as error:
                    print(
                        f"Error respondiendo al botón: {error}"
                    )

    def getMessage(self):
        return self._request(
            "getUpdates",
            json={
                "offset": self.offset,
                "timeout": 30,
                "allowed_updates": [
                    "message",
                    "callback_query"
                ]
            }
        )

    def start(self, startMsg="", commands=None):
        commands = dict(commands or [])

        normalized_commands = {}

        for command, function in commands.items():
            command = command.split("@")[0].strip()

            if not command.startswith("/"):
                command = "/" + command

            normalized_commands[command.lower()] = function

        print(startMsg)

        while True:
            try:
                updates = self.getMessage()

                for update in updates:
                    self.offset = update["update_id"] + 1

                    if "callback_query" in update:
                        self._handle_callback(
                            update["callback_query"]
                        )
                        continue

                    msg = update.get("message")

                    if msg is None:
                        continue

                    user = msg.get("from") or {}
                    chat = msg.get("chat") or {}
                    text = msg.get("text", "")

                    name = user.get(
                        "first_name", "Desconocido"
                    )
                    username = user.get("username")
                    user_id = user.get("id")
                    chat_id = chat.get("id")

                    if not text.startswith("/"):
                        continue

                    command_text = text.split()[0]

                    command_name = command_text.split("@")[0]

                    target = (
                        command_text.split("@", 1)[1]
                        if "@" in command_text
                        else None
                    )

                    if (
                        target
                        and target.lower() != self.username.lower()
                    ):
                        continue

                    function = normalized_commands.get(
                        command_name.lower()
                    )

                    if function is None:
                        continue

                    context = CommandContext(
                        bot=self,
                        chat_id=chat_id,
                        user_id=user_id,
                        message=msg,
                        text=text,
                        username=username,
                        name=name,
                        botName=self.name
                    )

                    try:
                        args = text.split()
                        args.pop(0)
                        nargs = len(list(inspect.signature(function).parameters.keys()))-1
                        args = args[:nargs]
                        falt = nargs - len(args)
                        if falt > 0:
                            args.extend([None] * falt)
                        function(context, *args)
                    except Exception as error:
                        print(
                            f"Error ejecutando comando "
                            f"{command_name}: {error}"
                        )

            except KeyboardInterrupt:
                break

            except requests.RequestException as error:
                print(f"Error de conexión: {error}")
                time.sleep(2)

            except RuntimeError as error:
                print(f"Error de Telegram: {error}")
                time.sleep(2)


class Context:
    def __init__(
        self,
        bot,
        chat_id,
        user_id,
        username,
        name
    ):
        self.bot = bot
        self.chat_id = chat_id
        self.user_id = user_id
        self.username = username
        self.name = name

        self.botName = bot.name

    def send(self, text):
        if self.chat_id is None:
            raise ValueError(
                "Este contexto no tiene un chat asociado."
            )

        return self.bot.sendMessage(
            self.chat_id,
            text
        )

class CallbackContext(Context):
    def __init__(
        self,
        bot,
        chat_id,
        user_id,
        username,
        name,
        data,
        query
    ):
        super().__init__(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            username=username,
            name=name
        )

        self.data = data
        self.query = query
        self.answered = False

    def answer(self, text=None, show_alert=False):
        if self.answered:
            return None

        payload = {
            "callback_query_id": self.query["id"],
            "show_alert": show_alert
        }

        if text is not None:
            payload["text"] = text

        result = self.bot._request(
            "answerCallbackQuery",
            json=payload
        )

        self.answered = True
        return result

class CommandContext(Context):
    def __init__(
        self,
        bot,
        chat_id,
        user_id,
        message,
        text: str,
        username,
        name,
        botName
    ):
        super().__init__(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            username=username,
            name=name
        )

        self.message = message
        self.text = text
        self.botName = botName

        parts = text.split()

        self.command = (
            parts[0].split("@")[0]
            if parts else ""
        )

        params = parts
        params.pop(0)
        self.params = params

        self.args = parts[1:]

class Message:
    def __init__(self, bot, chat_id, text):
        self.bot = bot
        self.chat_id = chat_id
        self.text = text
        self.keyboard = []

    def buttons(self, data):
        row = []

        for text, function in data:
            callback_id = self.bot._register_callback(
                function
            )

            row.append({
                "text": text,
                "callback_data": callback_id
            })

        self.keyboard.append(row)
        return self

class SendMessage(Message):
    def __init__(self, bot, chat_id, text, parse_mode: str = "Markdown"):
        self.parse_mode = parse_mode
        self.bot = bot
        self.chat_id = chat_id
        self.text = text
        self.keyboard = []

    def send(self):
        payload = {
            "chat_id": self.chat_id,
            "text": self.text,
            "parse_mode": self.parse_mode
        }

        if self.keyboard:
            payload["reply_markup"] = {
                "inline_keyboard": self.keyboard
            }

        return self.bot._request(
            "sendMessage",
            json=payload
        )

class SendPhoto(Message):
    def __init__(self, bot, chat_id, photo, text):
        self.bot = bot
        self.chat_id = chat_id
        self.text = text
        self.keyboard = []
        self.photo = photo

    def send(self):
        payload = {
            "chat_id": self.chat_id,
            "caption": self.text,
            "photo": self.photo
        }

        if self.keyboard:
            payload["reply_markup"] = {
                "inline_keyboard": self.keyboard
            }

        return self.bot._request(
            "sendPhoto",
            json=payload
        )
