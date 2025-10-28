from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from typing import Dict, Any
import logging

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния диалога
(
    START,
    MAIN_MENU,
    ASSET_TYPE_SELECTION,
    AMOUNT_SELECTION,
    INVESTMENT_PERIOD,
    WITHDRAW,
    INCREASE_INVESTMENT,
    WARRANTY_INFO,
    CHECK_STATUS,
    RESULT,
) = range(10)

# Константы для текстовых сообщений
TEXTS = {
    "welcome": "Добро пожаловать! Хотите начать или узнать подробнее?",
    "about": "Здесь будет информация о нашем сервисе...",
    "asset_selection": "Выберите тип инвестиций:",
    "stocks_response": "Коротеев тобой не доволен",
    "amount_selection": "Выберите сумму инвестиций:",
    "period_selection": "Выберите срок инвестирования:",
    "withdraw_question": "Важна ли для Вас возможность снимать деньги в любой момент?",
    "increase_question": "Возможность пополнять вложения?",
    "warranty_question": "Гарантия сохранности?",
    "confirmation": "Все верно?",
    "restart": "Давайте начнем заново.",
    "result": "Ваше персональное предложение...",
    "invalid_choice": "Пожалуйста, используйте предложенные кнопки.",
}

# Клавиатуры
KEYBOARDS = {
    "main_menu": [["Начать", "Узнать подробнее"]],
    "asset_types": [["Низкорисковые активы", "Акции"]],
    "amount_options": [["до 50к", "50 - 100к"], ["100 - 500к", "больше 500к"]],
    "period_options": [["до 6 месяцев", "6 мес - 1 год"], ["1 - 3 года", "больше 3 лет"]],
    "yes_no": [["Да", "Нет"]],
    "confirmation": [["Все верно", "Изменить"]],
    "restart": [["Начать заново"]],
    "final": [["/start"]],
}


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога, главное меню."""
    await update.message.reply_text(
        TEXTS["welcome"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS["main_menu"], resize_keyboard=True
        ),
    )
    return MAIN_MENU


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора в главном меню."""
    user_choice = update.message.text

    if user_choice == "Начать":
        await update.message.reply_text(
            TEXTS["asset_selection"],
            reply_markup=ReplyKeyboardMarkup(
                KEYBOARDS["asset_types"], resize_keyboard=True
            ),
        )
        return ASSET_TYPE_SELECTION
    elif user_choice == "Узнать подробнее":
        await update.message.reply_text(
            TEXTS["about"],
            reply_markup=ReplyKeyboardMarkup(
                KEYBOARDS["restart"], resize_keyboard=True
            ),
        )
        return START
    else:
        await update.message.reply_text(TEXTS["invalid_choice"])
        return MAIN_MENU


async def handle_asset_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора типа активов."""
    selected_asset = update.message.text

    if selected_asset == "Акции":
        await update.message.reply_text(
            TEXTS["stocks_response"],
            reply_markup=ReplyKeyboardMarkup(
                KEYBOARDS["restart"], resize_keyboard=True
            ),
        )
        return START
    elif selected_asset == "Низкорисковые активы":
        await update.message.reply_text(
            TEXTS["amount_selection"],
            reply_markup=ReplyKeyboardMarkup(
                KEYBOARDS["amount_options"], resize_keyboard=True
            ),
        )
        return AMOUNT_SELECTION
    else:
        await update.message.reply_text(TEXTS["invalid_choice"])
        return ASSET_TYPE_SELECTION


async def handle_amount_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора суммы инвестиций."""
    context.user_data["investment_amount"] = update.message.text
    await update.message.reply_text(
        TEXTS["period_selection"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS["period_options"], resize_keyboard=True
        ),
    )
    return INVESTMENT_PERIOD


async def handle_period_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора срока инвестирования."""
    context.user_data["investment_period"] = update.message.text
    await update.message.reply_text(
        TEXTS["withdraw_question"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS["yes_no"], resize_keyboard=True),
    )
    return WITHDRAW


async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка вопроса о снятии средств."""
    context.user_data["is_withdraw"] = update.message.text
    await update.message.reply_text(
        TEXTS["increase_question"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS["yes_no"], resize_keyboard=True),
    )
    return INCREASE_INVESTMENT


async def handle_increase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка вопроса о пополнении вложений."""
    context.user_data["is_increase"] = update.message.text
    await update.message.reply_text(
        TEXTS["warranty_question"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS["yes_no"], resize_keyboard=True),
    )
    return WARRANTY_INFO


async def handle_warranty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка вопроса о гарантии сохранности."""
    context.user_data["is_warranty"] = update.message.text
    await update.message.reply_text(
        TEXTS["confirmation"],
        reply_markup=ReplyKeyboardMarkup(
            KEYBOARDS["confirmation"], resize_keyboard=True
        ),
    )
    return CHECK_STATUS


async def handle_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверка и подтверждение введенных данных."""
    answer = update.message.text

    if answer == "Все верно":
        await send_summary(update, context)
        return ConversationHandler.END
    elif answer == "Изменить":
        await update.message.reply_text(
            TEXTS["restart"],
            reply_markup=ReplyKeyboardMarkup(
                KEYBOARDS["main_menu"], resize_keyboard=True
            ),
        )
        return MAIN_MENU
    else:
        await update.message.reply_text(TEXTS["invalid_choice"])
        return CHECK_STATUS


async def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сводки с введенными данными."""
    user_data: Dict[str, Any] = context.user_data

    result_message = (
        "Ваши предпочтения:\n"
        f"Сумма инвестиций: {user_data.get('investment_amount', 'не указана')}\n"
        f"Срок инвестирования: {user_data.get('investment_period', 'не указан')}\n"
        f"Возможность снятия: {user_data.get('is_withdraw', 'не указана')}\n"
        f"Возможность пополнения: {user_data.get('is_increase', 'не указана')}\n"
        f"Гарантия сохранности: {user_data.get('is_warranty', 'не указана')}\n\n"
        "Спасибо за использование нашего бота!"
    )

    await update.message.reply_text(
        result_message,
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS["final"], resize_keyboard=True),
    )


async def handle_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Финальное сообщение с предложением."""
    await update.message.reply_text(
        TEXTS["result"],
        reply_markup=ReplyKeyboardMarkup(KEYBOARDS["final"], resize_keyboard=True),
    )
    return ConversationHandler.END


def setup_handlers(application: Application) -> None:
    """Настройка обработчиков команд и сообщений."""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_conversation)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_conversation)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            ASSET_TYPE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_asset_selection)
            ],
            AMOUNT_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_selection)
            ],
            INVESTMENT_PERIOD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period_selection)
            ],
            WITHDRAW: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw)],
            INCREASE_INVESTMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_increase)
            ],
            WARRANTY_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_warranty)
            ],
            CHECK_STATUS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_check)
            ],
            RESULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_result)],
        },
        fallbacks=[CommandHandler("start", start_conversation)],
    )

    application.add_handler(conv_handler)


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token("8025648753:AAHhQASmQP2-KadSxV-BzCOEctw9tbWtTe4").build()

    setup_handlers(application)
    application.run_polling()


if __name__ == "__main__":
    main()
