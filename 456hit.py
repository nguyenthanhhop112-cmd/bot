import telebot
from telebot import types
import json
import os
from telebot.types import ChatMemberAdministrator
from filelock import FileLock
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading



TOKEN = "8548769965:AAGiFT1QufOG4IBLgo0RjnRAMa0uM5ugCh8"
bot = telebot.TeleBot(TOKEN)
admins = [6302038392]  # Danh sách ID admin


# Hàm thêm người mời vào invited.json
def add_invited(user_id, referrer):
    """Thêm user vào danh sách mời (invited.json)."""
    lock = FileLock("invited.json.lock")
    with lock:
        invited = {}
        if os.path.exists("invited.json"):
            with open("invited.json", "r", encoding="utf-8") as f:
                invited = json.load(f)
        if user_id not in invited:
            invited[user_id] = referrer
            with open("invited.json", "w", encoding="utf-8") as f:
                json.dump(invited, f, indent=2)

# Hàm lấy và xoá người mời khỏi invited.json
def pop_referrer(user_id):
    """Lấy và xoá người mời khỏi danh sách (invited.json)."""
    lock = FileLock("invited.json.lock")
    with lock:
        if not os.path.exists("invited.json"):
            return None
        with open("invited.json", "r", encoding="utf-8") as f:
            invited = json.load(f)
        referrer = invited.pop(user_id, None)
        if referrer:
            with open("invited.json", "w", encoding="utf-8") as f:
                json.dump(invited, f, indent=2)
        return referrer

# Hàm cập nhật số dư người dùng trong userdata.json
def update_user_balance(user_id, new_balance):
    """Cập nhật số dư của người dùng trong file userdata.json."""
    lock = FileLock("userdata.json.lock")
    with lock:
        userdata = {}
        if os.path.exists("userdata.json"):
            with open("userdata.json", "r", encoding="utf-8") as f:
                userdata = json.load(f)
        userdata[user_id] = {"balance": new_balance}
        with open("userdata.json", "w", encoding="utf-8") as f:
            json.dump(userdata, f, indent=2)

# Hàm lấy số dư người dùng từ userdata.json
def get_user_balance(user_id):
    """Lấy số dư của người dùng từ file userdata.json."""
    if not os.path.exists("userdata.json"):
        return 0
    with open("userdata.json", "r", encoding="utf-8") as f:
        userdata = json.load(f)
    return userdata.get(user_id, {}).get("balance", 0)

# ==== TẠO FILE config.json NẾU CHƯA CÓ ====
def init_config():
    if not os.path.exists("config.json"):
        default_config = {
            "ref_bonus": 1,
            "min_rut": 1000
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

# ==== TẠO FILE invited.json NẾU CHƯA CÓ ====
def init_invited():
    if not os.path.exists("invited.json"):
        with open("invited.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

admins = [6302038392]
# ==== GỌI NGAY KHI CHẠY ====
init_config()
init_invited()

def get_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def check_admin_channel(bot, channel_username):
    try:
        member = bot.get_chat_member(channel_username, bot.get_me().id)
        return isinstance(member, ChatMemberAdministrator)
    except Exception as e:
        print(f"Lỗi kiểm tra kênh {channel_username}: {e}")
        return False


# Tên file lưu dữ liệu
invited = {}
USER_FILE = "users.txt"
INVITED_FILE = "invited.json"
CHANNEL_FILE = "channels.txt"
CONFIG_PATH = "config.json"

def is_admins(user_id):
    try:
        with open('admins.txt', 'r') as f:
            admin_ids = [line.strip() for line in f.readlines()]
            return str(user_id) in admin_ids
    except FileNotFoundError:
        return False

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
    
with open("invited.json", "r", encoding="utf-8") as f:
    invited = json.load(f)

def is_banned(user_id):
    if not os.path.exists("ban_user.json"):
        return False
    with open("ban_user.json", "r") as f:
        banned = json.load(f)
    return str(user_id) in banned

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def load_channels():
    if not os.path.exists(CHANNEL_FILE):
        open(CHANNEL_FILE, "w").close()
    with open(CHANNEL_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    if not os.path.exists("admins.txt"):
        return False
    with open("admins.txt", "r") as f:
        return str(user_id) in f.read().splitlines()
def is_admin(user_id):
    return (user_id) in admins


def save_config(data):
    with open("config.json", "w") as f:
        json.dump(data, f)

@bot.message_handler(commands=['doibot'])
def doi_token(message):
    user_id = str(message.from_user.id)

    # Kiểm tra quyền admin
    with open("admins.txt", "r") as f:
        admins = [line.strip() for line in f.readlines()]

    if user_id not in admins:
        bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")
        return

    try:
        # Lấy token mới từ nội dung tin nhắn
        parts = message.text.split(" ")
        if len(parts) != 2:
            bot.reply_to(message, "Vui lòng dùng đúng định dạng: /doibot api_TOKEN")
            return
        new_token = parts[1]

        # Cập nhật config.json
        import json
        with open("config.json", "r") as f:
            config = json.load(f)

        config["bot_token"] = new_token

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

        bot.reply_to(message, "✅ Đã cập nhật token mới. Đang khởi động lại bot...")

        # Khởi động lại bot (tuỳ môi trường)
        import os
        os.execl(sys.executable, sys.executable, *sys.argv)

    except Exception as e:
        bot.reply_to(message, f"Lỗi: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    from telebot import types
    user_id = str(message.from_user.id)
    args = message.text.split()

    # Lưu người dùng mới vào users.txt và tạo số dư ban đầu
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    if user_id not in users:
        with open("users.txt", "a") as f:
            f.write(user_id + "\n")
        update_user_balance(user_id, 0)

        # Lưu người mời nếu có
        if len(args) > 1:
            referrer = args[1]
            if referrer != user_id:
                add_invited(user_id, referrer)

    # Gửi danh sách kênh cần tham gia
    channels = load_channels()
    if not channels:
        bot.send_message(message.chat.id, "Hiện tại chưa có kênh nào để tham gia.")
        return

    text = "🔍 Vui lòng vào tất cả các nhóm sau để sử dụng bot\n"
    for ch in channels:
        text += f"\n💠 {ch}"


    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✅ Tôi đã tham gia", callback_data="check_join")
    markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    try:
        # Trả lời callback ngay để tránh lỗi timeout
        bot.answer_callback_query(call.id, text="⏳ Đang kiểm tra...")
    except Exception as e:
        print("Lỗi trả lời callback:", e)

    # Xử lý logic trong thread để không bị delay
    threading.Thread(target=check_join_logic, args=(call,)).start()

def check_join_logic(call):
    user_id = str(call.from_user.id)
    channels = load_channels()
    not_joined = []
    ref_bonus = get_config().get("ref_bonus", 1)

    # Kiểm tra user đã vào đủ kênh chưa
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, int(user_id))
            if member.status in ['left', 'kicked']:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        msg = "❌ Bạn chưa tham gia các kênh sau:\n" + "\n".join(f"💠 {ch}" for ch in not_joined)
        bot.send_message(call.message.chat.id, msg)
        return

    # Người dùng đã tham gia đầy đủ kênh
    # Cộng thưởng cho người mời nếu có
    referrer = pop_referrer(user_id)
    if referrer:
        old_balance = get_user_balance(referrer)
        update_user_balance(referrer, old_balance + ref_bonus)
        try:
            bot.send_message(referrer, f"🎁 BẠN NHẬN {ref_bonus}đ TỪ LƯỢT GIỚI THIỆU {user_id}!")
        except:
            pass

    # Gửi menu chính
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("💰 Số dư của tôi")
    menu.row("🛒 Rút code", "📮MỜI BẠN BÈ")
    menu.row("📄 Link Game", "📊 Thống kê bot")
    bot.send_message(call.message.chat.id, "✅ Vui lòng thả cảm xúc!3 bài gần nhất để được ưu tiên @ChiaSeKinhNghiemGame!", reply_markup=menu)
    



@bot.message_handler(func=lambda message: message.text == "💰 Số dư của tôi")
def show_balance(message):
    if is_banned(message.from_user.id):
        return bot.reply_to(message, "Bạn đã bị cấm sử dụng bot.")

    user_id = str(message.from_user.id)
    balance = 0
    config = get_config()

    # Mặc định lấy balance = 0
    if os.path.exists("userdata.json"):
        with open("userdata.json", "r") as f:
            data = json.load(f)
        if user_id in data:
            balance = data[user_id].get("balance", 0)

    # Luôn gửi text, kể cả khi balance = 0
    text = f"""
💰 Số dư của bạn
─────
✨ Hiện tại: {balance} VND
👉 Mời bạn bè để nhận thêm ngẫu nhiên {config["ref_bonus"]} VND mỗi người!
"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['napcode'])
def handle_themcode(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")

    msg = bot.reply_to(message, "Gửi tất cả code, mỗi dòng 1 code.")
    bot.register_next_step_handler(msg, save_codes)

def save_codes(message):
    codes = message.text.strip().splitlines()

    if not os.path.exists("codes.txt"):
        open("codes.txt", "w", encoding="utf-8").close()

    with open("codes.txt", "r", encoding="utf-8") as f:
        existing_codes = set(line.strip() for line in f if line.strip())

    new_codes = [code.strip() for code in codes if code.strip() and code.strip() not in existing_codes]

    if not new_codes:
        return bot.reply_to(message, "Không có code mới nào được thêm (tất cả đều trùng).")

    with open("codes.txt", "a", encoding="utf-8") as f:
        for code in new_codes:
            f.write(code + "\n")

    bot.reply_to(message, f"✅Đã thêm {len(new_codes)} code mới thành công!")

@bot.message_handler(commands=['themcode'])
def handle_themcode(message):
    user_id = str(message.from_user.id)
    if not os.path.exists("admins.txt") or user_id not in open("admins.txt").read():
        return bot.reply_to(message, "⛔️ Bạn không có quyền sử dụng lệnh này.")

    lines = message.text.split('\n')
    
    if len(lines) < 2:
        return bot.reply_to(message, "Vui lòng gửi các code sau lệnh /themcode, mỗi code 1 dòng.")

    codes = [line.strip() for line in lines[1:] if line.strip()]

    if not os.path.exists("codes.txt"):
        open("codes.txt", "w", encoding="utf-8").close()

    with open("codes.txt", "r", encoding="utf-8") as f:
        existing_codes = set(line.strip() for line in f if line.strip())

    new_codes = [code for code in codes if code not in existing_codes]

    if not new_codes:
        return bot.reply_to(message, "Không có code mới nào được thêm (tất cả đều trùng).")

    with open("codes.txt", "a", encoding="utf-8") as f:
        for code in new_codes:
            f.write(code + "\n")

    bot.reply_to(message, f"Đã thêm {len(new_codes)} code mới.")

@bot.message_handler(commands=['rutcode'])
def rutcode_command(message):
    if is_banned(message.from_user.id):
       return bot.reply_to(message, "Bạn đã bị cấm sử dụng bot.")
    args = message.text.split()
    if len(args) < 3:
        return bot.reply_to(message, "Dùng: /rutcode <ghi_chú> <số_tiền>")

    note = args[1]
    try:
        amount = int(args[2])
    except:
        return bot.reply_to(message, "Số tiền không hợp lệ.")

    user_id = str(message.from_user.id)

    # Kiểm tra tham gia kênh
    channels = load_channels()
    not_joined = []
    for ch in channels:
        try:
            status = bot.get_chat_member(ch, message.from_user.id).status
            if status in ['left', 'kicked']:
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    if not_joined:
        msg = "❌Bạn chưa tham gia đủ kiểm tra lại:\n"
        for ch in not_joined:
            msg += f"• {ch}\n"
        return bot.reply_to(message, msg)

    # Lấy số dư
    if not os.path.exists("userdata.json"):
        return bot.reply_to(message, "Không có dữ liệu số dư.")
    with open("userdata.json", "r", encoding="utf-8") as f:
        balances = json.load(f)

    if user_id not in balances:
        return bot.reply_to(message, "Bạn chưa có tài khoản số dư.")
    balance = balances[user_id]["balance"]

    # Kiểm tra min_rut
    config = get_config()
    min_rut = config.get("min_rut", 10000)

    if amount < min_rut:
        return bot.reply_to(message, f"Số tiền rút tối thiểu là {min_rut}đ.")
    if balance < amount:
        return bot.reply_to(message, f"Bạn không đủ số dư để rút {amount}đ.")

    # Rút code từ file
    if not os.path.exists("codes.txt"):
        return bot.reply_to(message, "Không tìm thấy file codes.txt.")
    with open("codes.txt", "r", encoding="utf-8") as f:
        codes = f.read().splitlines()
    if not codes:
        return bot.reply_to(message, "⚠️ Hiện tại không còn code nào.")

    code = codes.pop(0)
    with open("codes.txt", "w", encoding="utf-8") as f:
        for c in codes:
            f.write(c + "\n")

    # Trừ tiền
    balances[user_id]["balance"] -= amount
    with open("userdata.json", "w", encoding="utf-8") as f:
        json.dump(balances, f)

    # Ghi log
    log_entry = {"user_id": user_id, "amount": amount}
    if os.path.exists("log_rutcode.json"):
        with open("log_rutcode.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with open("log_rutcode.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    # Gửi code cho người dùng
    bot.reply_to(message, f"📤 Rút Thành Công {note} \n\n 💵SỐ TIỀN: {amount} VNDD\n CODE: {code}")

    # Thông báo admin
    if os.path.exists("admins.txt"):
        with open("admins.txt", "r") as f:
            admin_ids = [line.strip() for line in f if line.strip()]
        for admin_id in admin_ids:
            try:
                bot.send_message(
                    int(admin_id),
                    f"Yêu cầu rút từ @{message.from_user.username} \n(🆔: {message.from_user.id})\n\n-TÊN NHÂN VẬT: {note}\n-Số tiền: {amount} VND.\n-CODE: {code}"
                )
            except:
                pass

@bot.message_handler(commands=['themadmin'])
def add_admin(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")
    
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /themadmin <user_id>")

    new_admin = args[1]

    if not os.path.exists("admins.txt"):
        open("admins.txt", "w").close()

    with open("admins.txt", "r") as f:
        admins = f.read().splitlines()

    if new_admin in admins:
        return bot.reply_to(message, "Người này đã là admin.")

    with open("admins.txt", "a") as f:
        f.write(new_admin + "\n")

    bot.reply_to(message, f"Đã thêm admin mới: {new_admin}")

@bot.message_handler(commands=['xoaadmin'])
def remove_admin(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /xoaadmin user_id")

    remove_id = args[1]

    if not os.path.exists("admins.txt"):
        return bot.reply_to(message, "Danh sách admin trống.")

    with open("admins.txt", "r") as f:
        admins = f.read().splitlines()

    if remove_id not in admins:
        return bot.reply_to(message, "Người này không phải admin.")

    admins.remove(remove_id)

    with open("admins.txt", "w") as f:
        for admin in admins:
            f.write(admin + "\n")

    bot.reply_to(message, f"Đã xoá admin: {remove_id}")

@bot.message_handler(commands=['themkenh'])
def add_channel(message):
    user_id = str(message.from_user.id)
    if not os.path.exists("admins.txt") or user_id not in open("admins.txt").read():
        return bot.reply_to(message, "⛔️ Bạn không có quyền sử dụng lệnh này.")

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /themkenh @tenkenh")

    chat_id = args[1]
    channels = load_channels()

    if chat_id in channels:
        return bot.reply_to(message, "Kênh đã có trong danh sách.")

    channels.append(chat_id)
    with open("channels.txt", "w") as f:
        for ch in channels:
            f.write(ch + "\n")

    bot.reply_to(message, f"Đã thêm kênh: {chat_id}")

@bot.message_handler(commands=['xoakenh'])
def remove_channel(message):
    user_id = str(message.from_user.id)
    if not os.path.exists("admins.txt") or user_id not in open("admins.txt").read():
        return bot.reply_to(message, "⛔️ Bạn không có quyền sử dụng lệnh này.")

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /xoakenh @tenkenh")

    chat_id = args[1]
    channels = load_channels()

    if chat_id not in channels:
        return bot.reply_to(message, "Không tìm thấy kênh trong danh sách.")

    channels.remove(chat_id)
    with open("channels.txt", "w") as f:
        for ch in channels:
            f.write(ch + "\n")

    bot.reply_to(message, f"Đã xoá kênh: {chat_id}")

@bot.message_handler(commands=['minrut'])
def set_min_rut_command(message):
    user_id = str(message.from_user.id)
    if not os.path.exists("admins.txt") or user_id not in open("admins.txt").read():
        return bot.reply_to(message, "⛔️ Bạn không có quyền sử dụng.")

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /minrut <số_tiền>")

    try:
        value = int(args[1])
        config = get_config()
        config["min_rut"] = value
        save_config(config)
        bot.reply_to(message, f"✅ Đã cập nhật min_rut = {value}đ")
    except:
        bot.reply_to(message, "Vui lòng nhập số hợp lệ.")

@bot.message_handler(commands=['thuongmoiban'])
def set_ref_bonus(message):
    user_id = str(message.from_user.id)
    if not os.path.exists("admins.txt") or user_id not in open("admins.txt").read():
        return bot.reply_to(message, "⛔️ Bạn không có quyền sử dụng.")

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Dùng: /thuongmoiban <số_tiền>")

    try:
        value = int(args[1])
        config = get_config()
        config["ref_bonus"] = value
        save_config(config)
        bot.reply_to(message, f"✅ Đã cập nhật tiền thưởng mời bạn = {value}đ")
    except:
        bot.reply_to(message, "Vui lòng nhập số hợp lệ.")

@bot.message_handler(commands=["dsadmin"])
def check_admins(message):
    user_id = str(message.from_user.id)

    try:
        with open("admins.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            admins = [line.strip() for line in lines if line.strip()]

        if not os.path.exis
