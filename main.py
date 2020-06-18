from aiogram import Bot, Dispatcher, types, executor
from config import TOKEN

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def make_screen(message: types.Message):
    await bot.send_message(message.from_user.id, message.text)

if __name__ == '__main__':
    executor.start_polling(dp)