# TelegramBot

Una pequeña librería de Python para interactuar con la [Telegram Bot API](https://core.telegram.org/bots/api) mediante una interfaz orientada a objetos. Permite consultar la información del bot, enviar mensajes y crear teclados inline cuyos botones ejecutan funciones de Python.

> **Estado del proyecto:** versión inicial / en desarrollo. La API puede cambiar y todavía hay limitaciones descritas al final de este documento.

## Características

- Obtener los datos del bot con `getInfo()`.
- Enviar mensajes de texto.
- Crear botones inline con `buttons()`.
- Asociar cada botón con una función de Python.

## Requisitos

- Python 3.9 o superior recomendado.
- Un bot de Telegram y su token.
- La dependencia `requests`.

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

## Inicio rápido: enviar un mensaje

```python
import telegramLib # Importa la libreria

bot = telegramLib.TelegramBot("TuToken") # Genera el bot

def saludar(ctx): # crea una funcion con el objeto ctx q controla el bot
    ctx.send("holAaaaaAAAAaAaAaAAaaaAaA") # utiliza el metodo send() del objeto ctx

def despedirse(ctx):
    ctx.send("adios :(")

bot.message("TuID", "Hola desde la mejor libreria del mundo")\
    .buttons([("Saludar", saludar), ("Despedirse", despedirse)]).send()
# Envia un mensaje cn dos botones funcionales a un ID especifica

bot.start() # Inicia el bot
```


## Crear un mensaje con botones inline

El método `message(chat_id, text)` crea un objeto `Message`. Puedes encadenar `buttons()` y `send()`:

```python
def saludar(ctx):
    ctx.send("¡Hola! Has pulsado el botón.")

bot.message(CHAT_ID, "¿Quieres saludar?") \
    .buttons([
        ("Saludar", saludar)
    ]) \
    .send()

bot.start()
```

**Importante:** escribe `saludar`, sin paréntesis. Así registras la función para que se ejecute después, cuando alguien pulse el botón. Si escribes `saludar()`, la ejecutarías inmediatamente y pasarías su resultado en lugar de la función.

## Varios botones en una fila

Cada elemento de la lista que recibe una llamada a `buttons()` se coloca en la misma fila:

```python
def saludar(ctx):
    ctx.send("¡Hola!")

def despedir(ctx):
    ctx.send("¡Hasta pronto!")

bot.message(CHAT_ID, "Elige una opción:") \
    .buttons([
        ("Saludar", saludar),
        ("Despedirse", despedir)
    ]) \
    .send()

bot.start()
```

## Organizar los botones en varias filas

Cada llamada a `buttons()` agrega una nueva fila al teclado:

```python
bot.message(CHAT_ID, "Menú principal") \
    .buttons([
        ("Opción A", opcion_a),
        ("Opción B", opcion_b)
    ]) \
    .buttons([
        ("Opción C", opcion_c)
    ]) \
    .send()

bot.start()
```

El resultado es una primera fila con los botones A y B y una segunda fila con el botón C.

## Usar el contexto de una pulsación

Las funciones asociadas a los botones reciben un objeto `ctx` de tipo `CallbackContext`. Este objeto contiene información de la pulsación y métodos auxiliares.

### Enviar un mensaje

```python
def bienvenida(ctx):
    ctx.send("¡Bienvenido!")
```

### Obtener el ID del usuario

```python
def mostrar_id(ctx):
    ctx.send(f"Tu ID de Telegram es {ctx.user_id}")
```

### Acceder al bot

```python
def info(ctx):
    ctx.bot.sendMessage(
        ctx.chat_id,
        f"Este bot se llama {ctx.bot.name}"
    )
```

### Responder a la pulsación

```python
def aviso(ctx):
    ctx.answer("¡Has pulsado el botón!")
    ctx.send("Aquí tienes el mensaje.")
```

`ctx.answer()` responde al `callback_query` y puede mostrar una notificación breve o una alerta. `ctx.send()` envía un mensaje nuevo al chat.

**Nota de implementación:** en la versión actual, `_handle_callback()` llama automáticamente a `answerCallbackQuery` antes de ejecutar la función. Por ello, si llamas también a `ctx.answer()` dentro del callback, Telegram puede recibir una segunda respuesta para la misma consulta. Para evitarlo, elimina la respuesta automática del controlador o no llames a `ctx.answer()` en las funciones. La opción más flexible para la librería es dejar que el callback responda por sí mismo.

## Ejemplo completo: menú interactivo

Guarda este ejemplo como `main.py`. Ajusta el nombre del módulo y define las variables de entorno antes de ejecutarlo.


Ejecuta:

```bash
python main.py
```

El proceso debe permanecer activo para seguir recibiendo pulsaciones. Este ejemplo envía el menú a un chat concreto al arrancar; todavía no implementa un manejador para que cualquier usuario envíe `/start` y reciba automáticamente el menú.

## ¿Cómo funcionan los callbacks?

Cuando se crea un botón, la librería:

1. Genera un identificador para la función.
2. Guarda la función en `bot.callbacks`.
3. Envía a Telegram el texto del botón y el identificador en `callback_data`.
4. Cuando se pulsa el botón, Telegram envía una actualización `callback_query`.
5. `bot.start()` recibe la actualización y busca el identificador en el registro.
6. Si encuentra la función, la ejecuta pasándole un `CallbackContext`.

Telegram no ejecuta funciones Python: la función se ejecuta en el proceso local de la librería.

## API de referencia

### `TelegramBot(token)`

Crea el bot y obtiene sus datos usando `getMe`.

Propiedades:

- `bot.token`: token del bot.
- `bot.url`: URL base de la Bot API.
- `bot.id`: identificador numérico del bot.
- `bot.name`: nombre visible del bot.
- `bot.username`: nombre de usuario del bot.
- `bot.callbacks`: registro interno de callbacks.
- `bot.offset`: posición de lectura de actualizaciones.

### `bot.getInfo()`

Devuelve el objeto con la información del bot que entrega el método `getMe` de Telegram.

### `bot.message(chat_id, text)`

Crea un objeto `Message` para construir y enviar un mensaje con teclado inline opcional.

### `bot.sendMessage(chat_id, text)`

Envía un mensaje de texto y devuelve el resultado de la API.

### `bot.sendPhoto(chatId, photo, isLink=False, caption="")`

Envía una fotografía desde una URL (`isLink=True`) o desde un archivo local (`isLink=False`).

### `Message.buttons(data)`

Agrega una fila de botones inline. `data` es una lista de pares `(texto, función)`.

### `Message.send()`

Envía el mensaje y su teclado, si lo hay.

### `bot.start()`

Inicia el bucle de long polling y procesa las actualizaciones `callback_query`. En la implementación actual, no procesa mensajes entrantes aunque solicita actualizaciones de tipo `message`.

### `CallbackContext`

Atributos:

- `ctx.bot`: instancia del bot.
- `ctx.chat_id`: ID del chat asociado al mensaje, si está disponible.
- `ctx.user_id`: ID del usuario que pulsó el botón.
- `ctx.data`: identificador `callback_data`.
- `ctx.query`: actualización completa `callback_query`.

Métodos:

- `ctx.send(text)`: envía un mensaje al chat asociado.
- `ctx.answer(text=None, show_alert=False)`: responde a la pulsación del botón.


<p>La libreria no tiene practicamente nada, esta en desarrollo aun</p>
