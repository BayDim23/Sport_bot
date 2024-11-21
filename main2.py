import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN  # Импортируем токен из config

API_TOKEN = TOKEN  # Замените 'TOKEN' на ваш реальный токен из config.py
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных SQLite и создание таблицы
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Проверка существования столбца name и добавление, если его нет
try:
    cursor.execute("ALTER TABLE user_data ADD COLUMN name TEXT")
except sqlite3.OperationalError:
    # Столбец уже существует
    pass

# Создание таблицы для хранения данных пользователя, если её нет
cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    language TEXT,
                    gender TEXT,
                    city TEXT,
                    role TEXT)''')
conn.commit()


# Определение состояний бота
class Survey(StatesGroup):
    start = State()
    name = State()
    language = State()
    gender = State()
    city = State()
    role = State()
    main_menu = State()
    training_program = State()
    speed_training = State()


# Начало диалога - приветствие и условия
@dp.message(F.text == '/start')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Сброс состояния при новом старте
    await message.answer(
        "Добро пожаловать в сервис тренировок для футбольных судей! "
        "Наш бот поможет вам развивать физические навыки и улучшить координацию.\n\n"
        "Примите условия обработки данных, чтобы продолжить.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Ознакомиться и согласиться")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(Survey.start)


# Принятие соглашения
@dp.message(Survey.start, F.text == "Ознакомиться и согласиться")
async def accept_terms(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(Survey.name)


# Запрос имени
@dp.message(Survey.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Выберите язык:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇬🇧 English")], [KeyboardButton(text="🇷🇺 Русский")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.language)


# Запрос языка
@dp.message(Survey.language)
async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer("Выберите ваш пол:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚹 Мужской")], [KeyboardButton(text="🚺 Женский")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.gender)


# Запрос пола
@dp.message(Survey.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Введите ваш город:")
    await state.set_state(Survey.city)


# Запрос города
@dp.message(Survey.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Выберите вашу роль:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Главный судья")], [KeyboardButton(text="Ассистент судьи")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.role)


# Запрос роли и переход в главное меню
@dp.message(Survey.role)
async def process_role(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    cursor.execute(
        "INSERT OR IGNORE INTO user_data (user_id, name, language, gender, city, role) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, user_data['name'], user_data['language'], user_data['gender'], user_data['city'], message.text))
    conn.commit()

    await message.answer("Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировочные занятия"), KeyboardButton(text="📜 Правила игры")],
            [KeyboardButton(text="🧩 Шарады"), KeyboardButton(text="📋 Тест по правилам")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.main_menu)


# Обработка нажатия на тренировочные занятия
@dp.message(Survey.main_menu, F.text == "🏋️ Тренировочные занятия")
async def show_training_programs(message: types.Message, state: FSMContext):
    await message.answer("Выберите программу тренировки:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Скорость")],
            [KeyboardButton(text="Выносливость")],
            [KeyboardButton(text="Сила и мощность")],
            [KeyboardButton(text="Гибкость и восстановление")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.training_program)


# Обработка выбора программ тренировок
@dp.message(Survey.training_program, F.text == "Скорость")
async def speed_training(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Скорость'. Доступен уровень 1.\nВыберите неделю:",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="Неделя 1")], [KeyboardButton(text="Неделя 2")]],
                             resize_keyboard=True,
                             one_time_keyboard=True
                         ))
    await state.set_state(Survey.speed_training)


# Обработка выбора недели в тренировках
@dp.message(Survey.speed_training, F.text.in_({"Неделя 1", "Неделя 2"}))
async def week_training(message: types.Message, state: FSMContext):
    await message.answer(f"Вы выбрали {message.text}. Выполните следующее упражнение: \n"
                         "1. Бег на месте в течение 2 минут\n"
                         "2. Отдых 1 минута\n"
                         "3. Прыжки с разворотом 10 раз\n\n"
                         "Когда закончите, вы можете выбрать другую тренировку или вернуться в главное меню.",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="🏋️ Тренировочные занятия")]],
                             resize_keyboard=True,
                             one_time_keyboard=True
                         ))
    await state.set_state(Survey.main_menu)


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
