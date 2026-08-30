from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "ru": {
        # Bot
        "start_welcome": (
            "👋 Добро пожаловать в маркетплейс запчастей для грузовиков!\n\n"
            "Нажмите кнопку ниже, чтобы открыть каталог."
        ),
        "choose_language": "Выберите язык / Tilni tanlang:",
        "language_set": "✅ Язык установлен: Русский",
        "btn_open_marketplace": "🛒 Открыть маркетплейс",
        "btn_become_master": "🔧 Зарегистрироваться как мастер",
        "btn_open_order": "📦 Посмотреть заказ",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_uz": "🇺🇿 O‘zbekcha",
        # Notifications — buyer
        "notif_order_confirmed_buyer": (
            "✅ Ваш заказ №{order_id} принят.\nСумма: {total} сум.\nМы свяжемся с вами."
        ),
        "notif_status_changed_buyer": (
            "🔔 Заказ №{order_id}: статус изменён на «{status}» (продавец: {seller})."
        ),
        "notif_new_message": "✉️ Новое сообщение от {sender}:\n{text}",
        # Notifications — seller
        "notif_new_order_seller": (
            "🆕 Новый заказ №{order_id}!\nПокупатель: {buyer}\nТоваров: {items}\n"
            "Сумма к получению: {payout} сум (комиссия {commission} сум)."
        ),
        # Notifications — admin
        "notif_new_order_admin": "📊 Новый заказ №{order_id} на сумму {total} сум.",
        "notif_new_seller_admin": "🏪 Новый продавец: {shop} ({name}).",
        # Order statuses (human readable)
        "status_new": "Новый",
        "status_confirmed": "Подтверждён",
        "status_processing": "В обработке",
        "status_shipped": "Отправлен",
        "status_delivered": "Доставлен",
        "status_completed": "Выполнен",
        "status_cancelled": "Отменён",
    },
    "uz": {
        # Bot
        "start_welcome": (
            "👋 Yuk mashinalari ehtiyot qismlari marketpleysiga xush kelibsiz!\n\n"
            "Katalogni ochish uchun quyidagi tugmani bosing."
        ),
        "choose_language": "Tilni tanlang / Выберите язык:",
        "language_set": "✅ Til o‘rnatildi: O‘zbekcha",
        "btn_open_marketplace": "🛒 Marketpleysni ochish",
        "btn_become_master": "🔧 Usta sifatida ro‘yxatdan o‘tish",
        "btn_open_order": "📦 Buyurtmani ko‘rish",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_uz": "🇺🇿 O‘zbekcha",
        # Notifications — buyer
        "notif_order_confirmed_buyer": (
            "✅ №{order_id} buyurtmangiz qabul qilindi.\nSumma: {total} so‘m.\n"
            "Tez orada siz bilan bog‘lanamiz."
        ),
        "notif_status_changed_buyer": (
            "🔔 №{order_id} buyurtma: holat «{status}» ga o‘zgardi (sotuvchi: {seller})."
        ),
        "notif_new_message": "✉️ {sender} dan yangi xabar:\n{text}",
        # Notifications — seller
        "notif_new_order_seller": (
            "🆕 Yangi buyurtma №{order_id}!\nXaridor: {buyer}\nMahsulotlar: {items}\n"
            "Qo‘lga tegadigan summa: {payout} so‘m (komissiya {commission} so‘m)."
        ),
        # Notifications — admin
        "notif_new_order_admin": "📊 №{order_id} yangi buyurtma, summa {total} so‘m.",
        "notif_new_seller_admin": "🏪 Yangi sotuvchi: {shop} ({name}).",
        # Order statuses
        "status_new": "Yangi",
        "status_confirmed": "Tasdiqlangan",
        "status_processing": "Ishlanmoqda",
        "status_shipped": "Jo‘natilgan",
        "status_delivered": "Yetkazilgan",
        "status_completed": "Bajarilgan",
        "status_cancelled": "Bekor qilingan",
    },
}
