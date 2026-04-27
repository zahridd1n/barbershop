from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from django.conf import settings

# Initialize dispatcher
dp = Dispatcher()
router = Router()

class BarberApplication(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_experience = State()
    waiting_for_about = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Assalomu alaykum! BossBarber jamoasiga qo'shilish uchun ariza qoldirish botiga xush kelibsiz.\n\n"
        "Iltimos, to'liq ism-sharifingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(BarberApplication.waiting_for_name)

@router.message(StateFilter(BarberApplication.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    # Telefon raqamni so'rash uchun tugma
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "Rahmat! Endi telefon raqamingizni yuboring (tugmani bosing yoki yozib yuboring):",
        reply_markup=keyboard
    )
    await state.set_state(BarberApplication.waiting_for_phone)

@router.message(StateFilter(BarberApplication.waiting_for_phone))
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    
    await message.answer(
        "Sartaroshlik (barber) sohasida necha yillik tajribangiz bor?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(BarberApplication.waiting_for_experience)

@router.message(StateFilter(BarberApplication.waiting_for_experience))
async def process_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    
    await message.answer(
        "O'zingiz haqingizda qisqacha ma'lumot qoldiring (qayerlarda ishlagansiz, ijtimoiy tarmoqlardagi sahifangiz yoki portfel ssilkasi):"
    )
    await state.set_state(BarberApplication.waiting_for_about)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from barber.models import Barber
import random
import string

@router.message(StateFilter(BarberApplication.waiting_for_about))
async def process_about(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(about=message.text)
    data = await state.get_data()
    
    # Arizani foydalanuvchiga tasdiqlatish yoki to'g'ridan to'g'ri yuborish
    application_text = (
        "📩 <b>YANGI ARIZA (Sartarosh bo'lish uchun)</b>\n\n"
        f"👤 <b>Ism:</b> {data.get('name')}\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"💼 <b>Tajriba:</b> {data.get('experience')} yil\n"
        f"📝 <b>Haqida:</b> {data.get('about')}\n"
        f"🔗 <b>Telegram:</b> @{message.from_user.username if message.from_user.username else 'Yoq'}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
        ]
    ])
    
    # Admin ga yuborish
    try:
        await bot.send_message(
            chat_id=settings.ADMIN_CHAT_ID,
            text=application_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await message.answer("Arizangiz muvaffaqiyatli qabul qilindi! Tez orada ma'muriyat siz bilan bog'lanadi.")
    except Exception as e:
        print(f"Error sending application to admin: {e}")
        await message.answer("Kechirasiz, ariza yuborishda xatolik yuz berdi. Iltimos keyinroq urinib ko'ring.")
    
    await state.clear()


@sync_to_async
def create_approved_barber(telegram_id, name, experience, description):
    if Barber.objects.filter(telegram_id=str(telegram_id)).exists():
        return None, None
        
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    username = f"barber_{telegram_id}"
    
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = True # required to access admin panel
    user.save()
    
    Barber.objects.create(
        user=user,
        telegram_id=str(telegram_id),
        is_approved=True,
        name=name,
        experience=int(experience) if str(experience).isdigit() else 0,
        description=description,
        age=20 
    )
    return username, password

@router.callback_query(F.data.startswith("approve_"))
async def process_approve(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.data.split("_")[1]
    
    lines = callback.message.text.split('\n')
    name = lines[2].replace("👤 Ism: ", "").strip()
    experience = lines[4].replace("💼 Tajriba: ", "").replace(" yil", "").strip()
    description = lines[5].replace("📝 Haqida: ", "").strip()
    
    username, password = await create_approved_barber(telegram_id, name, experience, description)
    
    if username and password:
        await callback.message.edit_text(callback.message.html_text + "\n\n✅ <b>Tasdiqlandi</b>", parse_mode="HTML")
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=f"Tabriklaymiz! Arizangiz tasdiqlandi.\n\nSizning admin panelga kirish ma'lumotlaringiz:\n"
                     f"🌐 Sayt: {settings.SITE_URL}/admin/\n"
                     f"👤 Login: <code>{username}</code>\n"
                     f"🔑 Parol: <code>{password}</code>",
                parse_mode="HTML"
            )
            await callback.answer("Tasdiqlandi va sartaroshga ma'lumotlar yuborildi!", show_alert=True)
        except Exception as e:
            print(f"Failed to send credentials: {e}")
            await callback.answer("Foydalanuvchiga xabar yuborishda xatolik yuz berdi!", show_alert=True)
    else:
        await callback.answer("Bu sartarosh allaqachon ro'yxatdan o'tgan yoki xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def process_reject(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.data.split("_")[1]
    await callback.message.edit_text(callback.message.html_text + "\n\n❌ <b>Rad etildi</b>", parse_mode="HTML")
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text="Kechirasiz, sizning arizangiz ma'muriyat tomonidan rad etildi."
        )
        await callback.answer("Rad etildi va xabar yuborildi.")
    except Exception as e:
        print(f"Failed to send rejection message: {e}")
        await callback.answer("Rad etildi, lekin xabar yuborishda xatolik yuz berdi.", show_alert=True)

dp.include_router(router)
