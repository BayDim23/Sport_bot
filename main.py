import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN  # Импортируем токен из config

API_TOKEN = TOKEN
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных SQLite и создание таблицы
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы для хранения данных пользователя, если её нет
cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    gender TEXT,
                    city TEXT,
                    role TEXT)''')
conn.commit()


# Определение состояний бота
class Survey(StatesGroup):
    start = State()
    name = State()
    gender = State()
    city = State()
    role = State()
    main_menu = State()
    training_program = State()
    workout_stage = State()


# Массив этапов тренировок
training_stages = [
    {
        "title": "Подготовительная часть",
        "content": (
            "1. Скручивания – 10 повторений. [Смотреть](https://disk.yandex.ru/i/7yDXy-wDJ5ofeg)\n"
            "2. Боковая планка – 10 секунд на каждую сторону. [Смотреть](https://disk.yandex.ru/i/5-EUO_28YcMo_A)\n"
            "3. Bird Dog – 10 повторений на каждую сторону. [Смотреть](https://disk.yandex.ru/i/xWGj17nJ2RKfww)"
        ),
    },
    {
        "title": "Основная часть, этап 1",
        "content": (
            "4. Бег с барьерами, лежа на животе – 12 повторений на каждую сторону.\n"
            "5. Приседания с лентой над головой – 12 повторений. [Смотреть](https://disk.yandex.ru/i/Pf8kWkMsqRUJwA)"
        ),
    },
    {
        "title": "Основная часть, этап 2",
        "content": (
            "6. Прыгающий Джек (без рук) – 15 повторений.\n"
            "7. Прыгающий Джек (руки вверх) – 15 повторений.\n"
            "8. Подскоки на месте с прямыми ногами – 20 секунд.\n"
            "9. Выпады вперед или в сторону – 10 повторений на каждую ногу."
        ),
    },
    {
        "title": "Основная подводящая часть",
        "content": (
            "1. Бег с активной постановкой стопы – 10 метров. [Смотреть](https://disk.yandex.ru/i/CtvsdmD_VgQRCQ)\n"
            "2. Бег с акцентом на вынос бедра – 20 метров.\n"
            "3. Прыжки на двух ногах через невысокие барьеры – 5 повторений. [Смотреть](https://disk.yandex.ru/i/B4JCsY9gbOUqgw)"
        ),
    },
    {
        "title": "Заключительная часть",
        "content": (
            "1. Растяжка квадрицепсов – 20-30 секунд на каждую ногу.\n"
            "2. Растяжка подколенных сухожилий – 20-30 секунд.\n"
            "3. Растяжка икроножных мышц – 20-30 секунд на каждую ногу.\n"
            "4. Растяжка ягодичных мышц – 20-30 секунд на каждую сторону.\n"
            "5. Растяжка мышц спины (поза ребенка) – 20-30 секунд."
        ),
    },
]


# Функция для отправки текущего этапа тренировки
async def send_training_stage(message: types.Message, state: FSMContext, stage_index: int):
    if 0 <= stage_index < len(training_stages):
        stage = training_stages[stage_index]
        await state.update_data(stage_index=stage_index)  # Сохраняем текущий индекс этапа
        await message.answer(
            f"{stage['title']}\n\n{stage['content']}\n\nВыберите действие:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Далее"), KeyboardButton(text="Назад")],
                    [KeyboardButton(text="Главное меню")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            ),
        )
    else:
        await message.answer("Вы завершили все этапы тренировки!", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Главное меню")]],
            resize_keyboard=True,
            one_time_keyboard=True
        ))
        await state.set_state(Survey.main_menu)


# Начало диалога - приветствие и условия
@dp.message(F.text == '/start')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
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


@dp.message(Survey.start, F.text == "Ознакомиться и согласиться")
async def accept_terms(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(Survey.name)


@dp.message(Survey.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Выберите ваш пол:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚹 Мужской")], [KeyboardButton(text="🚺 Женский")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.gender)


@dp.message(Survey.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Введите ваш город:")
    await state.set_state(Survey.city)


@dp.message(Survey.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Выберите вашу роль:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Главный судья")], [KeyboardButton(text="Ассистент судьи")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.role)


@dp.message(Survey.role)
async def process_role(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    cursor.execute(
        "INSERT OR IGNORE INTO user_data (user_id, name, gender, city, role) VALUES (?, ?, ?, ?, ?)",
        (user_id, user_data['name'], user_data['gender'], user_data['city'], message.text))
    conn.commit()

    await message.answer("Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировочные занятия")],
            [KeyboardButton(text="📜 Правила игры")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Survey.main_menu)


@dp.message(Survey.main_menu, F.text == "🏋️ Тренировочные занятия")
async def show_training_programs(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите программу тренировок:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Подготовительная часть")],
                [KeyboardButton(text="Основная часть, этап 1")],
                [KeyboardButton(text="Основная часть, этап 2")],
                [KeyboardButton(text="Основная подводящая часть")],
                [KeyboardButton(text="Заключительная часть")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await state.set_state(Survey.training_program)


@dp.message(Survey.training_program, F.text.in_([stage["title"] for stage in training_stages]))
async def start_training_stage(message: types.Message, state: FSMContext):
    stage_index = next(i for i, stage in enumerate(training_stages) if stage["title"] == message.text)
    await send_training_stage(message, state, stage_index)
    await state.set_state(Survey.workout_stage)


@dp.message(Survey.workout_stage, F.text == "Далее")
async def next_training_stage(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_stage = data.get("stage_index", 0) + 1
    await send_training_stage(message, state, current_stage)


@dp.message(Survey.workout_stage, F.text == "Назад")
async def previous_training_stage(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_stage = max(data.get("stage_index", 0) - 1, 0)
    await send_training_stage(message, state, current_stage)


@dp.message(Survey.workout_stage, F.text == "Главное меню")
async def end_training(message: types.Message, state: FSMContext):
    await message.answer(
        "Вы вернулись в главное меню. Выберите программу тренировок:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Подготовительная часть")],
                [KeyboardButton(text="Основная часть, этап 1")],
                [KeyboardButton(text="Основная часть, этап 2")],
                [KeyboardButton(text="Основная подводящая часть")],
                [KeyboardButton(text="Заключительная часть")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await state.set_state(Survey.training_program)


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
