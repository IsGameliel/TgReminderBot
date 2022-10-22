import json
from datetime import datetime, timedelta

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
)

main_keyboard = [
    ["➕ Add Reminder", "➖ Delete History"],
    ["📃 All Reminders", "🌐 Change UTC"],
    ["💰 Donate"],
]

REMINDER_TITLE, REMINDER_DATE, REMINDER_TIME, REMINDER_INFO = range(4)
DELETE_REMINDER_INDEX = range(1)
ADD_UTC = range(1)

def json_add_reminder(user):
    user = str(user)
    with open("data.json", "r+") as file:
        content = json.load(file)
        content["users"][user]["reminders"].insert(
            0, {"title": "", "date": "", "time": "", "venue": "", "info": ""}
        )
        file.seek(0)
        json.dump(content, file)
        file.truncate()


def json_add_reminder_info(user, key, value):
    user = str(user)
    key = str(key)
    with open("data.json", "r+") as file:
        content = json.load(file)
        content["users"][user]["reminders"][0][key] = value
        file.seek(0)
        json.dump(content, file)
        file.truncate()


def json_cancel_add_reminder(user):
    user = str(user)
    with open("data.json", "r+") as file:
        content = json.load(file)
        del content["users"][user]["reminders"][0]
        file.seek(0)
        json.dump(content, file)
        file.truncate()


def json_delete_reminder(user, index):
    user = str(user)
    index = index - 1

    with open("data.json", "r+") as file:
        content = json.load(file)

        del content["users"][user]["reminders"][index]
        file.seek(0)
        json.dump(content, file)
        file.truncate()

def is_new_user(user, username, first_name, last_name):
    user = str(user)
    with open("data.json", "r+") as file:
        content = json.load(file)
        if user not in content["users"]:
            content["users"][user] = {
                "username": username,
                "first name": first_name,
                "last name": last_name,
                "utc": "",
                "reminders": [],
            }
            file.seek(0)
            json.dump(content, file)
            file.truncate()

            return True
        else:
            return False


def json_add_utc(user, utc):
    user = str(user)
    with open("data.json", "r+") as file:
        content = json.load(file)
        content["users"][user]["utc"] = utc
        file.seek(0)
        json.dump(content, file)
        file.truncate()


def json_get_utc(user):
    user = str(user)
    with open("data.json", "r") as file:
        content = json.load(file)
        return content["users"][user]["utc"]


def json_get_info(user):
    user = str(user)
    with open("data.json", "r") as file:
        content = json.load(file)
        return content["users"][user]["reminders"][0]



def json_get_reminders_list(user):
    user = str(user)
    with open("data.json", "r+") as file:
        content = json.load(file)
        content = content["users"][user]["reminders"]

        if len(content) == 0:
            message = "📪 You have no reminders!"
            return message

        else:
            message = ""
            for i in range(len(content)):
                title = content[i]["title"]
                date = content[i]["date"]
                time = content[i]["time"]
                info = content[i]["info"]

                message += f"""
*Reminder {i+1}*
------------------
_Title_ : {title}
_Date_ : {date}
_Time_ : {time}
_Info_ : {info}
"""
            return message

# Bot conversation with users

def start_command(update, context):
    update.message.reply_text(
        "👋 Welcome to my bot! It can remind you of anything in time!",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )

    new_user = is_new_user(
        update.message.from_user.id,
        update.message.from_user.username,
        update.message.from_user.first_name,
        update.message.from_user.last_name,
    )

    if new_user is True:
        update.message.reply_text(
            "‼ Set your timezone ‼\n\n"
            "Send me your UTC (exp: +2, -1)\n\n"
            "You can always change it later",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ADD_UTC
    else:
        pass


def request_utc(update, context):
    update.message.reply_text(
        "🌐 Please send me your UTC\n\n👉 exemple: +2, -1",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ADD_UTC


def add_utc(update, context):
    utc = str(update.message.text)

    try:
        utc = int(utc)
        json_add_utc(update.message.from_user.id, utc)
        update.message.reply_text(
            "✅ Your timezone was successfully set",
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
        )
        return ConversationHandler.END
    except:
        update.message.reply_text("❌ Wrong format, please send again")
        return ADD_UTC


def donate(update, context):
    update.message.reply_text(
        "Thank you for donating! ❤",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Buy Me A Coffee", "https://www.buymeacoffee.com/eugeneibisz"
                    )
                ]
            ]
        ),
    )


def all_reminders(update, context):
    update.message.reply_text(
        f"{json_get_reminders_list(update.message.from_user.id)}", parse_mode="Markdown"
    )


def add_reminder(update, context):
    """Starts the conversation and asks the user about the reminder title."""
    update.message.reply_text(
        "⚡ Adding a new reminder\n\n" "Send /cancel to stop the process.",
        reply_markup=ReplyKeyboardRemove(),
    )

    json_add_reminder(update.message.from_user.id)

    update.message.reply_text("💡 Reminder title :")

    return REMINDER_TITLE


def add_reminder_title(update, context):
    """Stores the reminder title and asks for a reminder date."""
    json_add_reminder_info(update.message.from_user.id, "title", update.message.text)

    update.message.reply_text("📅 Reminder date :\n\nFormat : dd/mm/yyyy")

    return REMINDER_DATE


def add_reminder_date(update, context):
    """Stores the reminder date and asks for a reminder time."""
    json_add_reminder_info(update.message.from_user.id, "date", update.message.text)

    update.message.reply_text("⏲ Reminder time :\n\nFormat : HH:MM AM/PM")

    return REMINDER_TIME


def add_reminder_time(update, context):
    """Stores the reminder time and asks for a reminder info."""
    json_add_reminder_info(update.message.from_user.id, "time", update.message.text)

    update.message.reply_text("ℹ Reminder info :")

    return REMINDER_INFO


def add_reminder_info(update, context):
    """Stores reminder info and ends the conversation."""
    json_add_reminder_info(update.message.from_user.id, "info", update.message.text)

    all_info = json_get_info(update.message.from_user.id)
    reminder_title, reminder_date, reminder_time, reminder_info = (
        all_info["title"],
        all_info["date"],
        all_info["time"],
        all_info["info"],
    )

    utc = json_get_utc(update.message.from_user.id)
    user = update.message.chat_id

    try:
        hours, minutes, m = (
            int(reminder_time.split(" ")[0].split(":")[0]),
            int(reminder_time.split(" ")[0].split(":")[1]),
            reminder_time.split(" ")[1],
        )

    except:
        update.message.reply_text(
            "❌ Wrong time format! We're sorry, you'll have to restart the process...",
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
        )
        json_cancel_add_reminder_process(update.message.from_user.id)

        return ConversationHandler.END

    if "pm" in m.lower():
        hours = hours + 12

    try:
        seconds = datetime.timestamp(
            datetime.strptime(reminder_date, "%d/%m/%Y")
            + timedelta(hours=hours, minutes=minutes)
        ) - (datetime.timestamp(datetime.now()) + (utc * 3600))

        if seconds < 0:
            update.message.reply_text(
                "❌ The time and date you entered are in the past! We're sorry, you'll have to restart the process...",
                reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
            )
            json_cancel_add_reminder_process(update.message.from_user.id)

            return ConversationHandler.END

        else:
            pass

    except:
        update.message.reply_text(
            "❌ Wrong date format! We're sorry, you'll have to restart the process...",
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
        )
        json_cancel_add_reminder_process(update.message.from_user.id)

        return ConversationHandler.END

    context.job_queue.run_once(
        notify,
        seconds,
        context=[user, reminder_title, reminder_date, reminder_time, reminder_info],
    )

    update.message.reply_text(
        "✅ Reminder succesfully added!",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )

    return ConversationHandler.END


def cancel_add_reminder_process(update, context):
    """Cancels and ends the reminder process."""
    update.message.reply_text(
        "❌ Process ended.",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )
    json_cancel_add_reminder_process(update.message.from_user.id)

    return ConversationHandler.END


def delete_reminder(update, context):
    with open("data.json", "r+") as file:
        content = json.load(file)
        content = content["users"][str(update.message.from_user.id)]["reminders"]

        if len(content) == 0:
            update.message.reply_text("📪 You have no reminders to delete!")

            return ConversationHandler.END

        else:
            update.message.reply_text(
                "Choose the number of the reminder you want to delete\n\n"
                "Send /cancel to stop the process.\n\n"
                "Note that deleting the reminder will only remove it from the reminders history list, you will be reminded of it anyway.\n\n"
                f"{json_get_reminders_list(update.message.from_user.id)}",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown",
            )

            return DELETE_REMINDER_INDEX


def delete_reminder_status(update, context):
    try:
        index = int(str(update.message.text))

        if index <= 0:
            update.message.reply_text(
                "❌ Please try again and send me only existing reminder number."
            )
            return DELETE_REMINDER_INDEX
        else:
            json_delete_reminder(update.message.from_user.id, index)

            update.message.reply_text(
                "✅ Reminder Deleted Succesfully",
                reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
            )

            return ConversationHandler.END

    except:
        update.message.reply_text(
            "❌ Please try again and send me only existing reminder number."
        )
        return DELETE_REMINDER_INDEX


def cancel_delete_reminder_process(update, context):

    update.message.reply_text(
        "❌ Process ended.",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True),
    )

    return ConversationHandler.END


def notify(context):
    job = context.job

    chat_id = job.context[0]
    reminder_title = job.context[1]
    reminder_date = job.context[2]
    reminder_time = job.context[3]
    reminder_info = job.context[4]

    context.bot.send_message(
        chat_id=chat_id,
        text="🚨 REMINDER 🚨\n\n"
        f"*{reminder_title}*\n"
        f"_Info_ : {reminder_info}\n\n"
        f"_Date_ : {reminder_date}\n"
        f"_Time_ : {reminder_time}",
        parse_mode="Markdown",
    )

def main():
    BOT_TOKEN = "5561132468:AAF8IpgclfpAlR0f6GJe3ywvGoZIIV2D9bg"
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    start_command_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ADD_UTC: [MessageHandler(Filters.text, add_utc)],
        },
        fallbacks=[CommandHandler("nevermind", start_command)],
    )
    dp.add_handler(start_command_handler)

    change_utc_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Change UTC"), request_utc)],
        states={
            ADD_UTC: [MessageHandler(Filters.text, add_utc)],
        },
        fallbacks=[CommandHandler("nevermind", request_utc)],
    )
    dp.add_handler(change_utc_handler)

    dp.add_handler(MessageHandler(Filters.regex("Donate"), donate))
    dp.add_handler(MessageHandler(Filters.regex("All Reminders"), all_reminders))

    add_reminder_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Add Reminder"), add_reminder)],
        states={
            REMINDER_TITLE: [
                MessageHandler(
                    Filters.text & ~Filters.regex("/cancel"), add_reminder_title
                )
            ],
            REMINDER_DATE: [
                MessageHandler(
                    Filters.text & ~Filters.regex("/cancel"), add_reminder_date
                )
            ],
            REMINDER_TIME: [
                MessageHandler(
                    Filters.text & ~Filters.regex("/cancel"), add_reminder_time
                )
            ],
            REMINDER_INFO: [
                MessageHandler(
                    Filters.text & ~Filters.regex("/cancel"), add_reminder_info
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_reminder_process)],
    )
    dp.add_handler(add_reminder_handler)

    delete_reminder_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Delete History"), delete_reminder)],
        states={
            DELETE_REMINDER_INDEX: [
                MessageHandler(
                    Filters.text & ~Filters.regex("/cancel"), delete_reminder_status
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_delete_reminder_process)],
    )
    dp.add_handler(delete_reminder_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    print("Bot is running...")
    main()