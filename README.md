# TelegramBot

Una pequeña librería de Python para interactuar con la [Telegram Bot API](https://core.telegram.org/bots/api) mediante una interfaz orientada a objetos. Permite consultar la información del bot, enviar mensajes y tener un sistema de comandos.

> **Estado del proyecto:** versión inicial / en desarrollo.

## Características

- Obtener los datos del bot con `getInfo()`.
- Enviar mensajes de texto a un ID especifica.
- Crear botones inline con `buttons()` en un mensaje.
- Permite tener un sistema de comandos que permita interactuar con el bot

## Requisitos

- Python 3.9 o superior recomendado.
- Un bot de Telegram y su token.

## Instalación

```bash
git clone https://github.com/ropydev/telegram-bot-lib.git
cd telegram-bot-lib
pip install -r requirements.txt
```

## Crear un bot de Telegram

1. Abre Telegram y busca **@BotFather**.
2. Ejecuta `/newbot` y sigue las instrucciones.
3. Copia el token que BotFather te proporciona.

## Inicio rápido: crear comando /start

```python
import telegramLib # Importa la libreria

bot = telegramLib.TelegramBot("TuToken") # Genera el bot


def start(ctx):
    bot.message(ctx.chat_id, f"Hola, {ctx.name}. Yo soy {ctx.botName}, un bot construido en la libreria https://github.com/ropydev/telegram-bot-lib creada por Ronald (ropydev)").send() # Envia un mensaje cada que se use la funcion

commands = [
    ("/start", start) # Indica que el comando /start llamara a la funcion start()
]

bot.start("Bot iniciado", commands=commands) # Inicia el bot y le indica su lista de comandos
```

### Resultado

<img src="./examples/example_code.png">

## Crear un mensaje con botones inline

El método `message(chat_id, text)` crea un objeto `Message`. Puedes encadenar `buttons()` y `send()`:

```python
import telegramLib # importa la libreria

bot = telegramLib.TelegramBot("TuToken") # Generar bot

def saludar(ctx):
    bot.message(ctx.chat_id, f"<b>Hola, {ctx.name}</b>", parse_mode="HTML").send() # Mandar mensaje en HTML

def despedirse(ctx):
    bot.message(ctx.chat_id, f"Adios, {ctx.name}").send() # Mandar mensaje

def start(ctx):
    buttons = [
        ("Saludar", saludar),
        ("Despedirse", despedirse)
    ] # indicador de botones y sus funciones

    bot.message(ctx.chat_id, "Elija una opcion:").buttons(buttons).send() # Mensaje con botones

commands = [
    ("/start", start)
] # indicador de comandos

bot.start("Bot iniciado", commands=commands) # inicia el bot e indica sus comandos
```

### Resultado

<img src="./examples/inline_keyboard.png">


## Organizar los botones en varias filas

Cada llamada a `buttons()` agrega una nueva fila al teclado:

```python
import telegramLib # importa la libreria

bot = telegramLib.TelegramBot("TuToken") # Generar bot

def saludar(ctx):
    bot.message(ctx.chat_id, f"<b>Hola, {ctx.name}</b>", parse_mode="HTML").send() # Mandar mensaje en HTML

def despedirse(ctx):
    bot.message(ctx.chat_id, f"Adios, {ctx.name}").send() # Mandar mensaje

def info(ctx):
    bot.message(ctx.chat_id, f"Nombre: {ctx.name}\nUsername: {ctx.username}").send() # Mandar Info

def start(ctx):
    buttons = [
        ("Saludar", saludar),
        ("Despedirse", despedirse)
    ] # indicador de botones y sus funciones
    buttons1 = [
        ("Info", info)
    ] # otra fila de botones

    bot.message(ctx.chat_id, "Elija una opcion:")\
        .buttons(buttons)\
            .buttons(buttons1).send() # Mensaje con botones

commands = [
    ("/start", start)
] # indicador de comandos

bot.start("Bot iniciado", commands=commands) # inicia el bot e indica sus comandos
```

### Resultado

<img src="./examples/inline_keyboard2rows.png">

## Usar el contexto

Las funciones reciben un objeto `ctx` de tipo `CallbackContext` o `CommandContext`. Este objeto contiene información de la pulsación o comando, informacion del usuario y métodos auxiliares.

### ctx.bot
Comunicarse con el bot y sus metodos
Ejemplo:
```python
def sendMessage(ctx):
    ctx.bot.message("Hola").send()
```

### ctx.chat_id
Obtener el id del chat al q se le hizo la peticion
Ejemplo:
```python
def idMsg(ctx):
    bot.message(f"El id del chat es {ctx.chat_id}")

# Salida:
#    Bot: El id del chat es 192837465
```

### ctx.user_id
Obtener el id del usuario q hizo la peticion
Ejemplo:
```python
def idMsg(ctx):
    bot.message(f"Su id es {ctx.user_id}")
```

### ctx.username
Obtener el username del usuario q hizo la peticion
Ejemplo:
```python
def username(ctx):
    bot.message(f"Su id es {ctx.username}")
```

### ctx.name
Obtener el nombre del usuario q hizo la peticion
Ejemplo:
```python
def name(ctx):
    bot.message(f"Hola {ctx.username}")
```

## Funciones
### `TelegramBot(token)`

Crea el bot y obtiene sus datos usando `getMe`.

Propiedades:

- `bot.url`: URL base de la Bot API.
- `bot.id`: identificador numérico del bot.
- `bot.name`: nombre visible del bot.
- `bot.username`: nombre de usuario del bot.

### `bot.getInfo()`

Devuelve el objeto con la información del bot que entrega el método `getMe` de Telegram.

### `bot.message(chat_id, text).send()`

Crea un objeto `Message` para construir y enviar un mensaje con teclado inline opcional y envia el mensaje.

### `bot.message(chat_id, text).buttons([])`

Le apropia botones a un mensaje de la forma [ ("Texto del Boton", funcion), ("def", funcion) ]

### `Message.send()`

Envía el mensaje y su teclado, si lo hay.

### `bot.start(message, commands=[])`

Inicia el bucle del bot, recibe el argumento message (el mensaje q se imprime en consola cuando se inicia el bot) y commands (un array q contiene los comandos y sus funciones)

Ejemplo de array de comandos: [("/start", start), ("/help", helpMsg)]

