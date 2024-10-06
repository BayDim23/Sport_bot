import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, BaseMiddleware, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN  # Импортируем токен из config

# Инициализация бота и диспетчера
API_TOKEN = TOKEN  # Замените 'TOKEN' на ваш реальный токен из config.py
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# Создание или подключение к базе данных SQLite
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы для хранения данных пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT,
                    country TEXT,
                    city TEXT,
                    gender TEXT,
                    role TEXT,
                    age TEXT,
                    height TEXT,
                    weight TEXT,
                    fat_percentage TEXT,
                    sprint_10m TEXT,
                    sprint_40m TEXT,
                    coda TEXT,
                    training_conditions TEXT)''')
conn.commit()


# Определение состояний бота
class Survey(StatesGroup):
    language = State()
    country = State()
    city = State()
    gender = State()
    role = State()
    age = State()
    height = State()
    weight = State()
    fat_percentage = State()
    sprint_10m = State()
    sprint_40m = State()
    coda = State()
    training_conditions = State()


# Кастомное middleware для логирования сообщений
class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        message = event if isinstance(event, types.Message) else None
        if message:
            logging.info(f"Пользователь {message.from_user.id} отправил сообщение: {message.text}")
        return await handler(event, data)


# Добавляем middleware в диспетчер
dp.message.middleware(LoggingMiddleware())


# Начало диалога - выбор языка
@dp.message(F.text == '/start')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Сброс состояния при новом старте

    # Приветственное сообщение
    await message.answer("Я бот, который поможет вам находиться в отличной физической форме!")

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="English")],
            [KeyboardButton(text="Русский")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Choose your language / Выберите ваш язык:", reply_markup=markup)
    await state.set_state(Survey.language)


# Обработка выбора языка
@dp.message(Survey.language)
async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO user_data (user_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE user_data SET language = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Страна 1")],
            [KeyboardButton(text="Страна 2")],
            [KeyboardButton(text="Страна 3")],
            [KeyboardButton(text="Другое")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите вашу страну:", reply_markup=markup)
    await state.set_state(Survey.country)


# Обработка выбора страны
@dp.message(Survey.country)
async def process_country(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(country=message.text)
    cursor.execute("UPDATE user_data SET country = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()
    await message.answer("Введите ваш город:")
    await state.set_state(Survey.city)


# Обработка ввода города
@dp.message(Survey.city)
async def process_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(city=message.text)
    cursor.execute("UPDATE user_data SET city = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской")],
            [KeyboardButton(text="Женский")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите ваш пол:", reply_markup=markup)
    await state.set_state(Survey.gender)


# Обработка выбора пола
@dp.message(Survey.gender)
async def process_gender(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(gender=message.text)
    cursor.execute("UPDATE user_data SET gender = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Главный судья")],
            [KeyboardButton(text="Ассистент судьи")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите свою роль:", reply_markup=markup)
    await state.set_state(Survey.role)


# Обработка выбора роли
@dp.message(Survey.role)
async def process_role(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(role=message.text)
    cursor.execute("UPDATE user_data SET role = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="18-24")],
            [KeyboardButton(text="25-34")],
            [KeyboardButton(text="35-44")],
            [KeyboardButton(text="45-54")],
            [KeyboardButton(text="55 и старше")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите ваш возраст:", reply_markup=markup)
    await state.set_state(Survey.age)


# Обработка выбора возраста
@dp.message(Survey.age)
async def process_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(age=message.text)
    cursor.execute("UPDATE user_data SET age = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="160-165 см")],
            [KeyboardButton(text="166-170 см")],
            [KeyboardButton(text="171-175 см")],
            [KeyboardButton(text="176-180 см")],
            [KeyboardButton(text="181 см и выше")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите ваш рост:", reply_markup=markup)
    await state.set_state(Survey.height)


# Обработка выбора роста
@dp.message(Survey.height)
async def process_height(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(height=message.text)
    cursor.execute("UPDATE user_data SET height = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Обновление создания клавиатуры с параметром `keyboard`
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="50-60 кг")],
            [KeyboardButton(text="61-70 кг")],
            [KeyboardButton(text="71-80 кг")],
            [KeyboardButton(text="81-90 кг")],
            [KeyboardButton(text="91 кг и выше")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите ваш вес:", reply_markup=markup)
    await state.set_state(Survey.weight)


# Обработка выбора веса
@dp.message(Survey.weight)
async def process_weight(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(weight=message.text)
    cursor.execute("UPDATE user_data SET weight = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    # Определяем набор кнопок в зависимости от роли
    user_data = await state.get_data()
    role = user_data.get("role")
    markup = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if role == "Главный судья":
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="<1,60 сек")],
                [KeyboardButton(text="1,61-1,68 сек")],
                [KeyboardButton(text="1,69-1,76 сек")],
                [KeyboardButton(text="1,77-1,84 сек")],
                [KeyboardButton(text=">1,84 сек")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="<4,2 сек")],
                [KeyboardButton(text="4,2-4,3 сек")],
                [KeyboardButton(text="4,4-4,5 сек")],
                [KeyboardButton(text=">4,5 сек")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    await message.answer("Введите ваш результат в тесте 10 м спринт:", reply_markup=markup)
    await state.set_state(Survey.sprint_10m)


# Обработка выбора результата в 10 м спринт
@dp.message(Survey.sprint_10m)
async def process_sprint_10m(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(sprint_10m=message.text)
    cursor.execute("UPDATE user_data SET sprint_10m = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    markup = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Введите ваш результат в тесте 40 м спринт:", reply_markup=markup)
    await state.set_state(Survey.sprint_40m)


# Обработка ввода результата 40 м спринт
@dp.message(Survey.sprint_40m)
async def process_sprint_40m(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(sprint_40m=message.text)
    cursor.execute("UPDATE user_data SET sprint_40m = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    markup = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Введите ваш результат в тесте CODA (Change of Directional Ability):", reply_markup=markup)
    await state.set_state(Survey.coda)


# Обработка ввода результата CODA
@dp.message(Survey.coda)
async def process_coda(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(coda=message.text)
    cursor.execute("UPDATE user_data SET coda = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="К футбольному полю")],
            [KeyboardButton(text="К стадиону")],
            [KeyboardButton(text="К парку")],
            [KeyboardButton(text="К тренажерному залу")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Какие у вас тренировочные условия?", reply_markup=markup)
    await state.set_state(Survey.training_conditions)


# Обработка выбора тренировочных условий
@dp.message(Survey.training_conditions)
async def process_training_conditions(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(training_conditions=message.text)
    cursor.execute("UPDATE user_data SET training_conditions = ? WHERE user_id = ?", (message.text, user_id))
    conn.commit()
    await message.answer("Спасибо за предоставленную информацию! Ваши данные сохранены.")
    await state.clear()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
