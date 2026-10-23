import requests
import uuid
import time


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
            raise RuntimeError(result.get("description", "Error de Telegram"))

        return result["result"]

    def getInfo(self) -> dict:
        response = requests.get(
            f"{self.url}/getMe",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description", "Error de Telegram"))

        return data["result"]

    def message(self, chat_id, text):
        return Message(self, chat_id, text)

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
        self._request(
            "answerCallbackQuery",
            json={"callback_query_id": query["id"]}
        )

        if function is None:
            return

        message = query.get("message") or {}
        chat = message.get("chat") or {}

        context = CallbackContext(
            bot=self,
            chat_id=chat.get("id"),
            user_id=query["from"]["id"],
            data=callback_id,
            query=query
        )

        try:
            function(context)
        except Exception as error:
            print(f"Error ejecutando callback: {error}")

    def start(self):
        print(f"Bot @{self.username} iniciado.")

        while True:
            try:
                updates = self._request(
                    "getUpdates",
                    data={
                        "offset": self.offset,
                        "timeout": 30,
                        "allowed_updates": [
                            "message",
                            "callback_query"
                        ]
                    }
                )

                for update in updates:
                    self.offset = update["update_id"] + 1

                    if "callback_query" in update:
                        self._handle_callback(
                            update["callback_query"]
                        )

            except KeyboardInterrupt:
                print("Bot detenido.")
                break

            except requests.RequestException as error:
                print(f"Error de conexión: {error}")
                time.sleep(2)

            except RuntimeError as error:
                print(f"Error de Telegram: {error}")
                time.sleep(2)


class CallbackContext:
    def __init__(
        self, bot, chat_id, user_id, data, query
    ):
        self.bot = bot
        self.chat_id = chat_id
        self.user_id = user_id
        self.data = data
        self.query = query

    def answer(self, text=None, show_alert=False):
        payload = {
            "callback_query_id": self.query["id"],
            "show_alert": show_alert
        }

        if text is not None:
            payload["text"] = text

        return self.bot._request(
            "answerCallbackQuery",
            json=payload
        )

    def send(self, text):
        if self.chat_id is None:
            raise ValueError("El callback no tiene un chat asociado.")

        return self.bot.sendMessage(self.chat_id, text)


class Message:
    def __init__(self, bot, chat_id, text):
        self.bot = bot
        self.chat_id = chat_id
        self.text = text
        self.keyboard = []

    def buttons(self, data):
        row = []

        for text, function in data:
            callback_id = self.bot._register_callback(function)

            row.append({
                "text": text,
                "callback_data": callback_id
            })

        self.keyboard.append(row)
        return self

    def send(self):
        payload = {
            "chat_id": self.chat_id,
            "text": self.text
        }

        if self.keyboard:
            payload["reply_markup"] = {
                "inline_keyboard": self.keyboard
            }

        return self.bot._request(
            "sendMessage",
            json=payload
        )