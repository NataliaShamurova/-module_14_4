#t.me/PervyUr_bot
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import StateFilter, CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import asyncio

from aiogram.types import FSInputFile

from admin import admin_router
from kb13.reply import get_keyboard
from kb13.inline import get_callback_btns
import crud_functions

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))

dp = Dispatcher()
crud_functions.initiate_db()
dp.include_router(admin_router)

logging.basicConfig(level=logging.INFO)




@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.username}! Я бот, помогающий твоему здоровью.',
                         reply_markup=get_keyboard('Рассчитать', 'Информация', 'Купить',
                                                   placeholder="Выберите нужное действие",
                                                   sizes=(2, 1)),
                         )
    print('Привет! Я бот, помогающий твоему здоровью.')


class UserState(StatesGroup):
    age = State()  # Возраст
    growth = State()  # Рост
    weight = State()  # Вес


@dp.message(StateFilter(None), F.text == 'Рассчитать')
async def set_age(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=get_callback_btns(btns={
        'Рассчитать норму калорий': 'calories',
        'Формулы расчёта': 'formulas'
    })
                         )


@dp.callback_query(F.data.startswith('formulas'))
async def get_formulas(callback: types.CallbackQuery):
    await callback.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')


@dp.callback_query(F.data.startswith('calories'))
async def set_age(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите свой возраст:', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(UserState.age)


@dp.message(UserState.age, F.text)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer('Вы ввели неправильно, введите возраст еще раз:')
        return

    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await state.set_state(UserState.growth)


@dp.message(UserState.growth, F.text)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer('Вы ввели данные неправильно, введите рост в см еще раз:')
        return

    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await state.set_state(UserState.weight)


@dp.message(UserState.weight, F.text)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    try:
        int(message.text)
    except ValueError:
        await message.answer('Вы ввели данные о весе неправильно, введите вес в кг еще раз:')
        return

    data = await state.get_data()
    print(data)

    norm_calories = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161

    print(norm_calories)
    await message.answer(str(f'Ваша норма калорий: {norm_calories}'))
    await state.clear()


@dp.message(StateFilter(None), F.text == 'Купить')
async def get_buying_list(message: types.Message):
    products = crud_functions.get_all_products()
    for product in products:
        name = product[1]
        description = product[2]
        price = product[3]
        caption = f'Название: {name} | Описание: {description} | Цена: {price}'
        # Добавляем возможность отправить фото, если у продукта есть изображение
        if product_image_exists(product):
            image = FSInputFile(f'file/{name}.png')
            await message.answer_photo(image, caption=caption, show_caption_above_media=True)
        else:
            await message.answer(caption)
    await message.answer('Выберите продукт для покупки:', reply_markup=get_callback_btns(btns={
        'Продукт1': 'product_buying',
        'Продукт2': 'product_buying',
        'Продукт3': 'product_buying',
        'Продукт4': 'product_buying',
    }))
def product_image_exists(product):
    product_image_path = f'file/{product[1]}.png'
    return os.path.exists(product_image_path)


@dp.callback_query(F.data.startswith('product_buying'))
async def send_confirm_message(callback: types.CallbackQuery):
    await callback.message.answer("Вы успешно приобрели продукт!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
