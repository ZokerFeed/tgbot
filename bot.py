from aiogram import Bot, Dispatcher, executor, types
import logging
import asyncio
import os.path
import sys
import json
import zmq

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    logging.warning("CONFIG FILE DOES NOT EXIST")
    sys.exit()

with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
    config = json.loads(file.read())

def save():
    with open(CONFIG_FILE, 'w+', encoding='utf-8') as file:
        file.write(json.dumps(config))


bot = Bot(token=config['token'])
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    if msg.chat.id not in config['users']:
        await msg.reply(
            text = "<i><b>Authorize: /login password</b></i>",
            parse_mode = types.ParseMode.HTML
        )

@dp.message_handler(commands=['login'])
async def login(msg: types.Message):
    if msg.chat.id not in config['users'] and len(msg.text.split()) == 2:
        if msg.text.split()[1] == config['key']:
            config['users'].append(msg.chat.id)
            await msg.reply(
                text = "<i><b>Success</b></i>",
                parse_mode = types.ParseMode.HTML
            )
        else:
            await msg.reply(
                text = "<i><b>Wrong password</b></i>",
                parse_mode = types.ParseMode.HTML
            )

async def LongPoll(host, timeout):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(host)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)
    while True:
        await asyncio.sleep(timeout)
        socks = dict(poll.poll(5000))
        if socks.get(socket) == zmq.POLLIN:
            message = socket.recv_json()
            for user in config['users']:
                await bot.send_message(
                    chat_id = user,
                    text = message
                )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(LongPoll("tcp://localhost:2222", 10))
    executor.start_polling(dp, skip_updates= True)


