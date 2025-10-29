import asyncio
from loguru import logger
from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import AiogramError


async def display_error(user_message: Message, error_text: str, delay: int = 3):
    error_msg = await user_message.answer(error_text)

    await user_message.delete()
    await asyncio.sleep(delay)
    try:
        await error_msg.delete()
    except AiogramError as e:
        logger.error(f"Failed to delete error message: {e}")


async def edit_flow_message(
    bot: Bot,
    chat_id: int,
    flow_msg_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup,
    state: FSMContext,
) -> None:
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=flow_msg_id,
            reply_markup=reply_markup,
        )
    except AiogramError as e:
        logger.error(f"Failed to edit flow message: {e}")
        msg = await bot.send_message(
            chat_id=chat_id, text=text, reply_markup=reply_markup
        )
        await state.update_data(flow_message_id=msg.message_id)


async def edit_flow_message_from_callback(
    message: Message, text: str, reply_markup: InlineKeyboardMarkup, state: FSMContext
) -> None:
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
    except AiogramError as e:
        logger.error(f"Failed to edit flow message from callback: {e}")
        try:
            await message.delete()
        except AiogramError:
            pass

        msg = await message.answer(text=text, reply_markup=reply_markup)
        await state.update_data(flow_message_id=msg.message_id)
