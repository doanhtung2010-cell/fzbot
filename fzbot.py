# language: Python, file: fzbot_checkbank_fix.py, target: Python 3.10+ / python-telegram-bot v20+
import logging
import asyncio
import httpx
import json
import string
import os
import io
import base64
import random
import re
from urllib.parse import urlencode
import pytz
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

try:
    import qrcode
    from PIL import Image
    HAS_LOCAL_QR = True
except ImportError:
    HAS_LOCAL_QR = False

TOKEN = "9013814469:AAFejc8zagffNtXldhGQuhnFrBgbJgtDVQ4"
MAIN_BOT_USERNAME = "fztooltxvip_bot"
NOTIFY_BOT_TOKEN = "9073534499:AAHiHoICs6-iwEAZg9CdKlnIbvCT8e5wpMw"
NOTIFY_BOT_USERNAME = "@fzteamthongbao_bot"
OPEN_BOT_TARGET = "@fztooltxfree_bot"
ADMIN_ID = 7504960222
DATAKEY_FILE = "datakey.json"
HANOI_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Cấu hình API Bank & VietQR
APIBANK_URL = "https://thueapibank.vn/historyapivcb/0dd2a2e9204ffa1585a143b22ed076e3"
VIETQR_BANK_ID = "VCB"
VIETQR_ACCOUNT_NO = "1072492580"
VIETQR_ACCOUNT_NAME = "DO ANH TUNG"
VIETQR_TEMPLATE = "compact2"

BANK_BIN_MAP = {
    "VCB": "970436", "VIETCOMBANK": "970436",
    "ICB": "970415", "VIETINBANK": "970415",
    "BIDV": "970418",
    "VBA": "970405", "AGRIBANK": "970405",
    "TCB": "970407", "TECHCOMBANK": "970407",
    "MB": "970422", "MBBANK": "970422",
    "ACB": "970416",
    "VPB": "970432", "VPBANK": "970432",
    "TPB": "970423", "TPBANK": "970423",
    "STB": "970403", "SACOMBANK": "970403",
    "HDB": "970437", "HDBANK": "970437",
    "VIB": "970441",
    "SHB": "970443",
    "OCB": "970448",
    "MSB": "970426",
    "SEAB": "970440",
    "EIB": "970431",
    "LPB": "970449",
    "NAB": "970428",
    "ABB": "970425",
    "BAB": "970409",
    "SCB": "970429",
    "CAKE": "546034",
    "UBANK": "546035",
    "TIMO": "963388",
}

CHANNEL_THONG_BAO = "https://t.me/kenhthongbaofzteam"
CHANNEL_CHAT = "https://t.me/kenhchatfzteam"
CHANNEL_BILL = "https://t.me/fzteambill"
CHECKBILL_CHAT_ID = None
ADMIN_HANDLE = "@tungocbo"
FREE_KEY_BOT = "@fztooltxfree_bot"

REQUIRED_BOXES = [
    {"name": "Kênh Thông Báo FZ Team", "url": CHANNEL_THONG_BAO, "chat_id": None},
    {"name": "Nhóm Chat FZ Team", "url": CHANNEL_CHAT, "chat_id": None},
    {"name": "Kênh Check Bill FZ Team", "url": CHANNEL_BILL, "chat_id": None},
]

# Danh sách API game
API_URLS = {
    "sun_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/sunwintx",
    "hit_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/hitclubtx",
    "hit_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/hitclubmd5",
    "b52_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/b52tx",
    "b52_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/b52md5",
    "betvip_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/betviptx",
    "betvip_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/betvipmd5",
    "xd88_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/xocdia88tx",
    "xd88_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/xocdia88md5",
    "lc79_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/lc79tx",
    "lc79_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/lc79md5",
    "g68_hu": "https://leaf-reflect-disco-baker.trycloudflare.com/68gbbnxanh",
    "g68_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/68gbbnmd5",
    "max789_tx": "https://leaf-reflect-disco-baker.trycloudflare.com/max789tx",
    "max789_md5": "https://leaf-reflect-disco-baker.trycloudflare.com/max789md5",
}

EMOJI_MAP = {
    "pig": "6325835396433322385",
    "bell": "6327857028949616018",
    "cart": "6138892426569326890",
    "bank": "6138573709931202245",
    "clover": "6140985076369859188",
    "mail": "5253742260054409879",
    "bolt": "5210846102386927365",
    "alert": "6187956445036682670",
    "gift": "6327659078201910163",
    "party": "6186045798770286978",
    "bag": "5229064374403998351",
    "percent": "5386367538735104399",
    "spinner": "5406745015365943482",
    "down": "6282981642977944453",
    "net": "6283020430827594914",
    "pin": "6282807323140301774",
    "crown": "6282574544502793568",
    "calendar": "6282563411947561888",
    "game": "6285240855905182667",
    "gear": "6282526771581558537",
    "clip": "6282961933373024331",
    "check": "6282757029073265526",
    "cross": "6187956445036682670",
    "game68": "6282892088614856711",
    "club789": "6161305782122980113",
    "go88": "6282946544505202249",
    "sumclub": "6282887140812532517",
    "tx_md5": "6282907829669994559",
    "dice": "6283010225985300164",
    "luck8": "6282582722120524545",
    "rikvip": "6282554036033956435",
    "iwin": "6282752862954989731",
    "son789": "6285090510575013655",
    "mega": "6282542147564480286",
    "money": "6282688322481431358",
    "dice_3d": "6282625534354531452",
    "monitor": "6283064591681333288",
    "cash": "6282581652673667827",
    "fire": "6282779899774117162",
    "sunwin": "6282567672555120082",
    "hitclub": "6283010225985300164",
    "b52_logo": "6282887140812532517",
    "betvip_logo": "6282946544505202249",
    "lc79_logo": "6282554036033956435",
    "xd88_logo": "6284957224854889656",
    "table_tx": "6131914320189071678",
    "table_md5": "6129639044084147418",
    "table_sicbo": "5357334165404537258",
}

GAME_MAP_NAME = {
    "sun_tx": "SUNWIN TÀI XỈU",
    "hit_tx": "HITCLUB TÀI XỈU",
    "hit_md5": "HITCLUB MD5",
    "b52_tx": "B52 TÀI XỈU",
    "b52_md5": "B52 MD5",
    "betvip_tx": "BETVIP TÀI XỈU",
    "betvip_md5": "BETVIP MD5",
    "xd88_tx": "XOCDIA88 TÀI XỈU",
    "xd88_md5": "XOCDIA88 MD5",
    "lc79_tx": "LC79 TÀI XỈU",
    "lc79_md5": "LC79 MD5",
    "g68_hu": "GAME 68 HŨ",
    "g68_md5": "GAME 68 MD5",
    "max789_tx": "MAX789 TÀI XỈU",
    "max789_md5": "MAX789 MD5",
}

KEY_PACKAGES = {
    "buy_1d": {"days": 1, "price": 30000, "name": "1 Ngày"},
    "buy_3d": {"days": 3, "price": 70000, "name": "3 Ngày"},
    "buy_7d": {"days": 7, "price": 90000, "name": "7 Ngày"},
    "buy_30d": {"days": 30, "price": 130000, "name": "1 Tháng"},
}


def ce(key, fallback):
    return f'<tg-emoji emoji-id="{EMOJI_MAP[key]}">{fallback}</tg-emoji>'


def btn_icon(key):
    return {"icon_custom_emoji_id": EMOJI_MAP[key]}


E_PIG = ce("pig", "🐷")
E_BELL = ce("bell", "🔔")
E_CART = ce("cart", "🛒")
E_BANK = ce("bank", "🏦")
E_CLOVER = ce("clover", "🍀")
E_MAIL = ce("mail", "✉️")
E_BOLT = ce("bolt", "⚡️")

E_ALERT = ce("alert", "🚨")
E_GIFT = ce("gift", "🎁")
E_PARTY = ce("party", "🎉")
E_BAG = ce("bag", "🛍")
E_PCT = ce("percent", "%")
E_SPIN = ce("spinner", "⌛")
E_DOWN = ce("down", "⬇️")
E_NET = ce("net", "🌐")
E_PIN = ce("pin", "📌")
E_CROWN = ce("crown", "👑")
E_CAL = ce("calendar", "🗓")
E_GAME = ce("game", "🎮")
E_GEAR = ce("gear", "⚙️")
E_CLIP = ce("clip", "📎")
E_CHECK = ce("check", "✔️")
E_CROSS = ce("cross", "❌")
E_DICE = ce("dice", "🎲")
E_DICE3D = ce("dice_3d", "🎲")
E_MD5 = ce("tx_md5", "🔐")
E_MEGA = ce("mega", "📣")
E_MONEY = ce("money", "💸")
E_MON = ce("monitor", "🖥")
E_CASH = ce("cash", "💵")
E_FIRE = ce("fire", "🔥")

E_WIN = '<tg-emoji emoji-id="6282961933373024331">✔️</tg-emoji>'
E_LOSE = '<tg-emoji emoji-id="6282757029073265526">❌</tg-emoji>'

E_SUNWIN = ce("sunwin", "☀️")
E_HITCLUB = ce("hitclub", "🎰")
E_B52 = ce("b52_logo", "🃏")
E_BETVIP = ce("betvip_logo", "🏆")
E_LC79 = ce("lc79_logo", "💎")
E_XD88 = ce("xd88_logo", "🍀")
E_GAME68 = ce("game68", "🎮")
E_MAX789 = ce("club789", "🎮")

E_TABLE_TX = ce("table_tx", "🎮")
E_TABLE_MD5 = ce("table_md5", "🎮")
E_TABLE_SB = ce("table_sicbo", "👽")

MEDIA_GROUP_BUFFERS = {}
MEDIA_GROUP_CAPTIONS = {}
MEDIA_GROUP_TIMERS = {}
MEDIA_GROUP_ACTIVE_MODE = {}

AUTO_SESSIONS = {}
DATA_LOCK = asyncio.Lock()


async def safe_edit_or_send(q, text, reply_markup=None, parse_mode="HTML"):
    msg = q.message
    try:
        if msg and msg.photo:
            return await q.edit_message_caption(caption=text, parse_mode=parse_mode, reply_markup=reply_markup)
        return await q.edit_message_text(text=text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        err_s = str(e).lower()
        if "message is not modified" in err_s:
            return msg
        try:
            return await msg.reply_text(text=text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception:
            return None


def _game_emoji(api_key):
    if api_key.startswith("sun"):
        return E_SUNWIN
    if api_key.startswith("hit"):
        return E_HITCLUB
    if api_key.startswith("b52"):
        return E_B52
    if api_key.startswith("betvip"):
        return E_BETVIP
    if api_key.startswith("lc79"):
        return E_LC79
    if api_key.startswith("xd88"):
        return E_XD88
    if api_key.startswith("g68"):
        return E_GAME68
    if api_key.startswith("max789"):
        return E_MAX789
    return E_GAME


def _table_emoji(api_key):
    if api_key.endswith("_sb"):
        return E_TABLE_SB
    if api_key.endswith("_md5"):
        return E_TABLE_MD5
    return E_TABLE_TX


def _mask_key_for_bill(key_str):
    s = (key_str or "").strip()
    if len(s) <= 6:
        return "***"
    return f"{s[:3]}{'*' * (len(s) - 6)}{s[-3:]}"


def _mask_uid_for_bill(uid_str):
    s = str(uid_str or "").strip()
    if len(s) <= 4:
        return "***"
    return f"{s[:2]}***{s[-2:]}"


def get_hanoi_time():
    return datetime.now(HANOI_TZ)


def parse_hanoi_time(t):
    return datetime.fromisoformat(t).astimezone(HANOI_TZ) if t else None


def save_datakey(data):
    tmp_file = f"{DATAKEY_FILE}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp_file, DATAKEY_FILE)


def ensure_admin_owner(data):
    admin_int = int(ADMIN_ID)
    admin_str = str(admin_int)
    subs = [int(x) for x in data.get("sub_admins", []) if int(x) != admin_int]
    changed = False
    if data.get("owner_id") != admin_int:
        data["owner_id"] = admin_int
        changed = True
    if data.get("sub_admins") != ([admin_int] + subs):
        data["sub_admins"] = [admin_int] + subs
        changed = True
    users = data.setdefault("users", {})
    if admin_str not in users:
        users[admin_str] = {
            "username": "Admin",
            "first_name": "Chủ Bot",
            "join_date": get_hanoi_time().isoformat(),
            "key_expires": None,
            "balance": 0,
            "analysis_count": 0,
            "verified_3box": True,
            "is_owner": True,
        }
        changed = True
    else:
        if not users[admin_str].get("is_owner"):
            users[admin_str]["is_owner"] = True
            changed = True
        if not users[admin_str].get("verified_3box"):
            users[admin_str]["verified_3box"] = True
            changed = True
    if changed:
        save_datakey(data)
    return data


def init_datakey_file():
    if not os.path.exists(DATAKEY_FILE):
        data = {
            "owner_id": int(ADMIN_ID),
            "users": {},
            "keys": {},
            "history": [],
            "deposits": {},
            "giftcodes": {},
            "game_history": {},
            "deposit_requests": {},
            "free_key_requests": {},
            "sub_admins": [int(ADMIN_ID)],
            "free_key_claims": {},
            "processed_tx_ids": [],
            "settings": {
                "last_user_id": 0,
                "last_key_id": 0,
                "last_deposit_id": 0,
                "last_giftcode_id": 0,
                "last_freekey_id": 0,
            },
        }
        save_datakey(data)
        ensure_admin_owner(data)


def load_datakey():
    try:
        with open(DATAKEY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("sub_admins", [])
            data.setdefault("free_key_claims", {})
            data.setdefault("free_key_requests", {})
            data.setdefault("processed_tx_ids", [])
            return ensure_admin_owner(data)
    except Exception:
        data = {
            "owner_id": int(ADMIN_ID),
            "users": {},
            "keys": {},
            "history": [],
            "deposits": {},
            "giftcodes": {},
            "game_history": {},
            "deposit_requests": {},
            "free_key_requests": {},
            "sub_admins": [int(ADMIN_ID)],
            "free_key_claims": {},
            "processed_tx_ids": [],
            "settings": {
                "last_user_id": 0,
                "last_key_id": 0,
                "last_deposit_id": 0,
                "last_giftcode_id": 0,
                "last_freekey_id": 0,
            },
        }
        return ensure_admin_owner(data)


def is_admin(user_id, data=None):
    if not user_id:
        return False
    uid_int = int(user_id)
    if uid_int == int(ADMIN_ID):
        return True
    if data is None:
        data = load_datakey()
    return uid_int in [int(x) for x in data.get("sub_admins", [])]


def get_admin_recipients(data):
    return {int(ADMIN_ID)} | {int(x) for x in data.get("sub_admins", [])}


def _resolve_checkbill_target():
    if CHECKBILL_CHAT_ID not in (None, "", 0):
        return CHECKBILL_CHAT_ID
    url = (CHANNEL_BILL or "").strip()
    if url.startswith("https://t.me/") and "/+" not in url and "/c/" not in url:
        handle = url.split("https://t.me/", 1)[1].strip("/").split("/")[0]
        if handle and not handle.startswith("joinchat"):
            return f"@{handle}"
    return None


def _open_bot_keyboard(button_text="Mở Bot", icon_key="bolt"):
    bot_handle = (OPEN_BOT_TARGET or FREE_KEY_BOT or MAIN_BOT_USERNAME).lstrip("@")
    bot_url = f"https://t.me/{bot_handle}"
    return {
        "inline_keyboard": [
            [
                {
                    "text": button_text,
                    "url": bot_url,
                    "icon_custom_emoji_id": EMOJI_MAP[icon_key],
                }
            ]
        ]
    }


async def notify_checkbill_bot(text, button_text="Mở Bot", icon_key="bolt"):
    target = _resolve_checkbill_target()
    if not NOTIFY_BOT_TOKEN or not target:
        return
    api_url = f"https://api.telegram.org/bot{NOTIFY_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": _open_bot_keyboard(button_text=button_text, icon_key=icon_key),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(api_url, json=payload)
    except Exception as e:
        logging.warning("notify_checkbill_bot failed: %s", e)


def ensure_user(data, user):
    uid = str(user.id)
    if uid not in data.setdefault("users", {}):
        data["users"][uid] = {
            "username": user.username or "No Username",
            "first_name": user.first_name or "Vô Danh",
            "join_date": get_hanoi_time().isoformat(),
            "key_expires": None,
            "balance": 0,
            "analysis_count": 0,
            "verified_3box": False,
        }
        save_datakey(data)
    else:
        data["users"][uid].setdefault("verified_3box", False)
    return uid


def next_request_id(data):
    s = data.setdefault("settings", {})
    s["last_deposit_id"] = s.get("last_deposit_id", 0) + 1
    return s["last_deposit_id"]


def next_freekey_id(data):
    s = data.setdefault("settings", {})
    s["last_freekey_id"] = s.get("last_freekey_id", 0) + 1
    return s["last_freekey_id"]


def is_key_active(user_record, user_id=None, data=None):
    if is_admin(user_id, data):
        return True
    exp = parse_hanoi_time(user_record.get("key_expires")) if user_record else None
    return exp is not None and get_hanoi_time() < exp


def _normalize_kq(v):
    if not v:
        return None
    s = str(v).strip().upper()
    if "TAI" in s or "TÀI" in s:
        return "Tài"
    if "XIU" in s or "XỈU" in s:
        return "Xỉu"
    return None


def _normalize_pred(v):
    kq = _normalize_kq(v)
    if kq:
        return kq.upper()
    if not v:
        return None
    s = str(v).strip().upper()
    return s if s else None


def _clean_session_code(val):
    if val is None:
        return None
    s = str(val).strip().lstrip("#")
    return s if s else None


def _parse_api_history_items(raw_data):
    if not isinstance(raw_data, dict):
        return []

    candidates = None
    for k in (
        "lich_su", "lich_su_du_doan", "lich_su_phien", "history",
        "recent_history", "last_50", "ket_qua_50_phien", "list", "items",
    ):
        val = raw_data.get(k)
        if isinstance(val, list) and val:
            candidates = val
            break

    if candidates is None and isinstance(raw_data.get("data"), list):
        candidates = raw_data.get("data")

    if not candidates:
        return []

    parsed = []
    for idx, item in enumerate(candidates):
        if isinstance(item, dict):
            phien = _clean_session_code(
                item.get("phien") or item.get("Phien") or item.get("session") or item.get("id") or f"auto_{idx}"
            )
            pred_raw = item.get("du_doan") or item.get("Du_doan") or item.get("pred") or item.get("chon")
            kq_raw = item.get("ket_qua") or item.get("Ket_qua") or item.get("result") or item.get("kq")
            status_raw = (
                item.get("trang_thai") or item.get("Trang_thai") or item.get("status")
                or item.get("danh_gia") or item.get("ket_qua_du_doan")
            )
            win_flag = item.get("win") if "win" in item else item.get("is_win")
            if win_flag is None and "dung" in item:
                win_flag = item.get("dung")

            pred_norm = _normalize_pred(pred_raw)
            kq_norm = _normalize_kq(kq_raw)

            status = None
            if isinstance(win_flag, bool):
                status = "ĐÚNG" if win_flag else "SAI"
            elif status_raw is not None:
                st_up = str(status_raw).strip().upper()
                if any(x in st_up for x in ("WIN", "ĐÚNG", "DUNG", "TRUE", "THẮNG", "THANG", "1", "OK", "✓", "✔")):
                    status = "ĐÚNG"
                elif any(x in st_up for x in ("LOSE", "SAI", "FALSE", "THUA", "0", "MISS", "✗", "✘", "❌")):
                    status = "SAI"

            if not status and pred_norm and kq_norm:
                status = "ĐÚNG" if pred_norm == kq_norm.upper() else "SAI"

            if status in ("ĐÚNG", "SAI"):
                parsed.append({"phien": str(phien), "pred": pred_norm, "ket_qua": kq_norm, "status": status})
        elif isinstance(item, str):
            st_up = item.strip().upper()
            if st_up in ("W", "WIN", "ĐÚNG", "DUNG", "T", "1", "✓", "✔"):
                parsed.append({"phien": f"str_{idx}", "pred": None, "ket_qua": None, "status": "ĐÚNG"})
            elif st_up in ("L", "LOSE", "SAI", "THUA", "F", "0", "✗", "✘", "❌"):
                parsed.append({"phien": f"str_{idx}", "pred": None, "ket_qua": None, "status": "SAI"})

    return parsed[-50:]


def _extract_direct_50_counts(raw_data):
    if not isinstance(raw_data, dict):
        return None
    w = None
    l = None
    for wk in ("dung_50", "win_50", "so_phien_dung", "thang_50", "thang", "win", "dung"):
        if raw_data.get(wk) is not None and str(raw_data.get(wk)).isdigit():
            w = int(raw_data.get(wk))
            break
    for lk in ("sai_50", "lose_50", "so_phien_sai", "thua_50", "thua", "lose", "sai"):
        if raw_data.get(lk) is not None and str(raw_data.get(lk)).isdigit():
            l = int(raw_data.get(lk))
            break
    if w is not None and l is not None:
        total = w + l
        if total > 50 and total > 0:
            w = round(w * 50 / total)
            l = 50 - w
        return w, l
    return None


def sync_api_history_50(game_key, api_items=None, direct_counts=None):
    data = load_datakey()
    hist = data.setdefault("game_history", {}).setdefault(game_key, [])
    changed = False

    if api_items:
        by_phien = {str(x.get("phien")): x for x in hist if x.get("phien")}
        for item in api_items:
            p = str(item.get("phien"))
            if not p:
                continue
            if p in by_phien:
                ex = by_phien[p]
                if item.get("pred") and not ex.get("pred"):
                    ex["pred"] = item["pred"]
                    changed = True
                if item.get("ket_qua") and not ex.get("ket_qua"):
                    ex["ket_qua"] = item["ket_qua"]
                    changed = True
                if item.get("status") in ("ĐÚNG", "SAI") and ex.get("status") != item["status"]:
                    ex["status"] = item["status"]
                    changed = True
            else:
                rec = {
                    "phien": p,
                    "ket_qua": item.get("ket_qua"),
                    "pred": item.get("pred"),
                    "status": item.get("status"),
                    "time": get_hanoi_time().isoformat(),
                }
                hist.append(rec)
                by_phien[p] = rec
                changed = True

    if len(hist) > 200:
        del hist[:-200]
        changed = True

    if changed:
        save_datakey(data)

    if direct_counts is not None:
        w, l = direct_counts
        return w, l, w + l

    if api_items:
        settled_api = [x for x in api_items if x.get("status") in ("ĐÚNG", "SAI")][-50:]
        if settled_api:
            win_50 = sum(1 for x in settled_api if x.get("status") == "ĐÚNG")
            lose_50 = sum(1 for x in settled_api if x.get("status") == "SAI")
            return win_50, lose_50, len(settled_api)

    settled = [x for x in hist if x.get("status") in ("ĐÚNG", "SAI")][-50:]
    if settled:
        win_50 = sum(1 for x in settled if x.get("status") == "ĐÚNG")
        lose_50 = sum(1 for x in settled if x.get("status") == "SAI")
        return win_50, lose_50, len(settled)

    return 0, 0, 0


def get_50_window_stats(game_key, data=None):
    if data is None:
        data = load_datakey()
    hist = data.get("game_history", {}).get(game_key, [])
    settled = [x for x in hist if x.get("status") in ("ĐÚNG", "SAI")][-50:]
    win_50 = sum(1 for x in settled if x.get("status") == "ĐÚNG")
    lose_50 = sum(1 for x in settled if x.get("status") == "SAI")
    return win_50, lose_50, len(settled)


def record_result(game_key, phien, ket_qua, pred=None):
    if not phien:
        return
    data = load_datakey()
    hist = data.setdefault("game_history", {}).setdefault(game_key, [])
    kq_norm = _normalize_kq(ket_qua)
    pred_norm = _normalize_pred(pred)
    for entry in hist:
        if entry["phien"] == phien:
            if pred_norm and not entry.get("pred"):
                entry["pred"] = pred_norm
            if kq_norm:
                entry["ket_qua"] = kq_norm
                if entry.get("pred"):
                    entry["status"] = "ĐÚNG" if _normalize_pred(entry["pred"]) == kq_norm.upper() else "SAI"
            save_datakey(data)
            return
    rec = {
        "phien": phien,
        "ket_qua": kq_norm,
        "pred": pred_norm,
        "status": None,
        "time": get_hanoi_time().isoformat(),
    }
    if pred_norm and kq_norm:
        rec["status"] = "ĐÚNG" if pred_norm == kq_norm.upper() else "SAI"
    hist.append(rec)
    if len(hist) > 200:
        hist.pop(0)
    save_datakey(data)


def _extract_chat_target(box):
    cid = box.get("chat_id")
    if cid not in (None, "", 0):
        return cid
    url = (box.get("url") or "").strip()
    if url.startswith("https://t.me/") and "/+" not in url and "/c/" not in url:
        handle = url.split("https://t.me/", 1)[1].strip("/").split("/")[0]
        if handle and not handle.startswith("joinchat"):
            return f"@{handle}"
    return None


async def check_3box_membership(bot, user_id):
    checked_count = 0
    for idx, box in enumerate(REQUIRED_BOXES, 1):
        target = _extract_chat_target(box)
        if not target:
            return False, box["name"], f"Box #{idx} ({box['name']}) chưa điền chat_id trong REQUIRED_BOXES.", checked_count
        try:
            member = await bot.get_chat_member(chat_id=target, user_id=int(user_id))
            if member.status in ("left", "kicked"):
                return False, box["name"], None, checked_count
            checked_count += 1
        except Exception as e:
            logging.warning("get_chat_member failed for %s (%s): %s", box["name"], target, e)
            return False, box["name"], f"Không kiểm tra được {box['name']} ({target}). Hãy kiểm tra bot đã vào box đó chưa.", checked_count
    return True, None, None, checked_count


def get_gate_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1. Kênh Thông Báo FZ Team", url=CHANNEL_THONG_BAO, api_kwargs=btn_icon("bell"))],
        [InlineKeyboardButton("2. Nhóm Chat FZ Team", url=CHANNEL_CHAT, api_kwargs=btn_icon("mega"))],
        [InlineKeyboardButton("3. Kênh Check Bill FZ Team", url=CHANNEL_BILL, api_kwargs=btn_icon("cash"))],
        [InlineKeyboardButton("Check OK — Xác Nhận Đã Vào 3 Box", callback_data="check_3box_ok", api_kwargs=btn_icon("check"))],
    ])


async def send_3box_gate(update_or_query, edit=False, reason=None):
    extra = f"\n{E_ALERT} <b>Chi tiết:</b> <i>{reason}</i>" if reason else ""
    text = (
        f"{E_ALERT} <b>BẮT BUỘC THAM GIA ĐỦ 3 BOX</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PIN} Vui lòng vào đủ <b>3 box</b> để mở khóa bot:\n"
        f"1. {E_BELL} Kênh Thông Báo: {CHANNEL_THONG_BAO}\n"
        f"2. {E_MEGA} Nhóm Chat: {CHANNEL_CHAT}\n"
        f"3. {E_CASH} Kênh Check Bill: {CHANNEL_BILL}\n"
        f"{E_CHECK} Xong bấm <b>Check OK</b>.{extra}"
    )
    kb = get_gate_keyboard()
    if edit and hasattr(update_or_query, "message"):
        return await safe_edit_or_send(update_or_query, text, reply_markup=kb)
    return await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def enforce_3box_or_block(update, context, user, data, is_callback=False):
    uid = str(user.id)
    u = data["users"][uid]
    ok, missing_box, reason, _ = await check_3box_membership(context.bot, user.id)
    if not ok:
        u["verified_3box"] = False
        save_datakey(data)
        alert_msg = reason or f"Bạn chưa vào đủ 3 box (thiếu: {missing_box})!"
        if is_callback:
            q = update.callback_query
            await q.answer(alert_msg[:200], show_alert=True)
            return True, await send_3box_gate(q, edit=True, reason=reason)
        return True, await send_3box_gate(update, edit=False, reason=reason)
    u["verified_3box"] = True
    save_datakey(data)
    return False, None


def build_main_header(user, u, data=None):
    uid = str(user.id)
    name = user.first_name or "Vô Danh"
    username = f"@{user.username}" if user.username else "Không có"
    if is_key_active(u, user.id, data):
        if is_admin(user.id, data) and not u.get("key_expires"):
            role_label = "CHỦ BOT / ADMIN CHÍNH" if int(user.id) == int(ADMIN_ID) else "ADMIN PHỤ"
            key_status = f"{E_CROWN} <b>{role_label} VIP VĨNH VIỄN</b>"
        else:
            exp = parse_hanoi_time(u["key_expires"])
            key_status = f"{E_CROWN} <b>VIP tới {exp.strftime('%d/%m/%Y %H:%M')}</b>"
    elif u.get("key_expires"):
        key_status = f"{E_CROSS} <b>Đã hết hạn</b>"
    else:
        key_status = f"{E_SPIN} <b>Chưa kích hoạt</b>"

    return (
        f"{E_CROWN} <b>BOT DOP SACH TIEN CUA NHA CAI</b> {E_FIRE}\n"
        f"{E_CHECK} <b>REAL-TIME NHANH GỌN - CHUẨN XÁC</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} <b>Xin chào:</b> <b>{name}</b>\n"
        f"{E_PIN} <b>ID:</b> <code>{uid}</code>\n"
        f"{E_CLIP} <b>Nick:</b> {username}\n"
        f"{E_MONEY} <b>Số dư:</b> <code>{u.get('balance', 0):,}đ</code> {E_CASH}\n"
        f"{E_CROWN} <b>KEY VIP:</b> {key_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_BELL} <b>KÊNH THÔNG BÁO:</b> {CHANNEL_THONG_BAO}\n"
        f"{E_MEGA} <b>NHÓM CHAT:</b> {CHANNEL_CHAT}\n"
        f"{E_CASH} <b>KÊNH CHECK BILL:</b> {CHANNEL_BILL}\n"
        f"{E_CROWN} <b>ADMIN HỖ TRỢ:</b> {ADMIN_HANDLE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GAME} <b>CHỌN CHỨC NĂNG BÊN DƯỚI</b> {E_FIRE}"
    )


def _resolve_session_pair(raw_prev, raw_pred, shift=-1):
    prev_s = _clean_session_code(raw_prev)
    pred_s = _clean_session_code(raw_pred)

    if prev_s and prev_s.isdigit() and pred_s and pred_s.isdigit():
        p_int = int(prev_s)
        n_int = int(pred_s)
        if n_int == p_int + 1:
            pass
        elif p_int == n_int + 1:
            prev_s, pred_s = str(n_int), str(p_int)
        else:
            prev_s, pred_s = str(p_int), str(p_int + 1)

        if shift and int(prev_s) + shift > 0:
            prev_s = str(int(prev_s) + shift)
            pred_s = str(int(prev_s) + 1)
        return prev_s, pred_s

    if prev_s and prev_s.isdigit():
        p_val = int(prev_s) + (shift or 0)
        if p_val <= 0:
            p_val = int(prev_s)
        return str(p_val), str(p_val + 1)

    if pred_s and pred_s.isdigit():
        n_val = int(pred_s) + (shift or 0)
        if n_val <= 1:
            n_val = int(pred_s)
        return str(n_val - 1), str(n_val)

    return prev_s, pred_s


async def fetch_api_data(api_url, tool_type):
    if not api_url:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(api_url)
            if r.status_code != 200:
                return None
            d = r.json()
            raw_prev = d.get("phien_hien_tai") or d.get("Phien_Hien_tai") or d.get("phien_truoc")
            raw_pred = d.get("Phien_du_doan") or d.get("phien_du_doan") or d.get("phien_ke_tiep")
            prev_s, pred_s = _resolve_session_pair(raw_prev, raw_pred, shift=0)
            live_kq = _normalize_kq(
                d.get("ket_qua") or d.get("Ket_qua") or d.get("ket_qua_phien") or d.get("Du_doan_hien_tai")
            )
            api_history = _parse_api_history_items(d)
            direct_50 = _extract_direct_50_counts(d)
            return {
                "game": tool_type.split("_")[0].upper(),
                "session": pred_s,
                "pred": _normalize_pred(d.get("Du_doan") or d.get("du_doan")),
                "dice": (
                    f"{d.get('Xuc_xac1')}-{d.get('Xuc_xac2')}-{d.get('Xuc_xac3')}"
                    if d.get("Xuc_xac1") else None
                ),
                "total": d.get("Tong") or d.get("tong_diem"),
                "rate": d.get("ty_le_thang", "89.2%"),
                "live_phien": prev_s,
                "live_kq": live_kq,
                "api_history": api_history,
                "direct_50": direct_50,
            }
    except Exception:
        return None


def _session_key(user_id, api_key):
    return f"{int(user_id)}:{api_key}"


def stop_auto_session(user_id, api_key=None):
    prefix = f"{int(user_id)}:"
    keys_to_stop = []
    for k, st in AUTO_SESSIONS.items():
        if api_key:
            if k == _session_key(user_id, api_key):
                keys_to_stop.append(k)
        elif k.startswith(prefix):
            keys_to_stop.append(k)

    for k in keys_to_stop:
        st = AUTO_SESSIONS.pop(k, None)
        if st:
            task = st.get("task")
            if task and not task.done():
                task.cancel()


def build_auto_analysis_message(api_key, res, win_count, lose_count, total_50=0, last_status_text=None):
    g_icon = _game_emoji(api_key)
    t_icon = _table_emoji(api_key)
    full_game_name = GAME_MAP_NAME.get(api_key, res.get("game") or api_key.upper())
    prev_session = res.get("live_phien") or "-"
    prev_result = res.get("live_kq") or "Đang chờ kết quả"
    pred_session = res.get("session") or "-"
    pred_choice = _normalize_pred(res.get("pred")) or "-"
    win_rate = res.get("rate") or "89.2%"
    sample_n = total_50 if total_50 > 0 else (win_count + lose_count)
    acc_pct = f"{(win_count / sample_n * 100):.1f}%" if sample_n > 0 else "0.0%"

    lines = [
        f"{g_icon} <b>BÀN CHƠI:</b> <b>{full_game_name}</b> {t_icon}",
        f"{E_CAL} <b>PHIÊN TRƯỚC:</b> <code>#{prev_session}</code> — <b>{prev_result}</b>",
        f"{E_PIN} <b>PHIÊN DỰ ĐOÁN:</b> <code>#{pred_session}</code> {E_FIRE}",
    ]
    if res.get("dice"):
        lines.append(f"{E_DICE3D} <b>XÚC XẮC GẦN NHẤT:</b> <code>{res['dice']}</code>")
    if res.get("total"):
        lines.append(f"{E_PCT} <b>TỔNG ĐIỂM:</b> <code>{res['total']}</code>")
    lines.append(f"{E_FIRE} <b>CHỐT CẦU:</b> <code>{pred_choice}</code> {E_CROWN}")
    lines.append(f"{E_CASH} <b>TỈ LỆ THẮNG:</b> <code>{win_rate}</code>")
    lines.append(
        f"{E_MON} <b>THỐNG KÊ ({sample_n}/50 PHIÊN):</b> {E_WIN} <b>THẮNG:</b> <code>{win_count}</code> | {E_LOSE} <b>THUA:</b> <code>{lose_count}</code> (<code>{acc_pct}</code>)"
    )
    if last_status_text:
        lines.append(last_status_text)

    body = "\n".join(lines)
    return (
        f"{E_CROWN} <b>KẾT QUẢ PHÂN TÍCH AUTO</b> {E_FIRE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{body}"
    )


def get_auto_keyboard(api_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tắt Auto Bàn Này", callback_data=f"stop_auto:{api_key}", api_kwargs=btn_icon("cross"))],
        [
            InlineKeyboardButton("Đổi Bàn / Game", callback_data="menu_games", api_kwargs=btn_icon("game")),
            InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down")),
        ],
    ])


async def _auto_loop_worker(bot, chat_id, message_id, user_id, api_key):
    s_key = _session_key(user_id, api_key)
    last_rendered = None

    try:
        while s_key in AUTO_SESSIONS:
            st = AUTO_SESSIONS.get(s_key)
            if not st:
                break

            res = await fetch_api_data(API_URLS.get(api_key), api_key)
            if not res:
                await asyncio.sleep(3.5)
                continue

            win_50, lose_50, total_50 = sync_api_history_50(
                api_key, api_items=res.get("api_history"), direct_counts=res.get("direct_50"),
            )
            st["win"] = win_50
            st["lose"] = lose_50
            st["total_50"] = total_50

            live_phien = res.get("live_phien")
            live_kq = res.get("live_kq")
            pred_session = res.get("session")
            pred_choice = _normalize_pred(res.get("pred"))

            has_api_50 = bool(res.get("api_history") or res.get("direct_50"))

            if live_phien and live_kq:
                record_result(api_key, live_phien, live_kq)
                if not has_api_50:
                    win_50, lose_50, total_50 = get_50_window_stats(api_key)
                    st["win"] = win_50
                    st["lose"] = lose_50
                    st["total_50"] = total_50

            settled_notice = st.get("last_status_text")
            active_phien = st.get("active_session")
            active_pred = st.get("active_pred")

            if (
                active_phien and active_pred and live_phien == active_phien
                and live_kq and live_kq != st.get("baseline_kq_for_active")
            ):
                is_win = active_pred == live_kq.upper()
                record_result(api_key, active_phien, live_kq, pred=active_pred)
                if not has_api_50:
                    win_50, lose_50, total_50 = get_50_window_stats(api_key)
                    st["win"] = win_50
                    st["lose"] = lose_50
                    st["total_50"] = total_50
                else:
                    win_50 = st["win"]
                    lose_50 = st["lose"]
                    total_50 = st["total_50"]

                if is_win:
                    settled_notice = f"{E_WIN} <b>PHIÊN #{active_phien}: THẮNG</b> (Chốt <code>{active_pred}</code> / Ra <b>{live_kq}</b>)"
                else:
                    settled_notice = f"{E_LOSE} <b>PHIÊN #{active_phien}: THUA</b> (Chốt <code>{active_pred}</code> / Ra <b>{live_kq}</b>)"
                st["last_status_text"] = settled_notice

                st["active_session"] = None
                st["active_pred"] = None
                st["baseline_kq_for_active"] = None

            new_pred_signature = f"{pred_session}:{pred_choice}"
            if pred_session and pred_choice and st.get("last_pred_sig") != new_pred_signature:
                st["last_pred_sig"] = new_pred_signature
                st["active_session"] = pred_session
                st["active_pred"] = pred_choice
                st["baseline_kq_for_active"] = live_kq if live_phien == pred_session else None
                record_result(api_key, pred_session, None, pred=pred_choice)

                async with DATA_LOCK:
                    d_now = load_datakey()
                    u_rec = d_now.get("users", {}).get(str(user_id))
                    if u_rec is not None:
                        u_rec["analysis_count"] = u_rec.get("analysis_count", 0) + 1
                        save_datakey(d_now)

            msg_text = build_auto_analysis_message(
                api_key, res, st.get("win", 0), st.get("lose", 0),
                total_50=st.get("total_50", 0), last_status_text=settled_notice,
            )
            if msg_text != last_rendered:
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id, text=msg_text,
                        parse_mode="HTML", reply_markup=get_auto_keyboard(api_key),
                    )
                    last_rendered = msg_text
                except Exception:
                    pass

            await asyncio.sleep(4.0)
    except asyncio.CancelledError:
        return
    finally:
        AUTO_SESSIONS.pop(s_key, None)


# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    stop_auto_session(user.id)
    data = load_datakey()
    uid = ensure_user(data, user)
    u = data["users"][uid]
    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return
    await update.message.reply_text(
        build_main_header(user, u, data),
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard(user.id, data),
    )


# --- ADMIN COMMANDS ---
async def handle_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text(
            f"{E_ALERT} Dùng: <code>/key &lt;số&gt; &lt;m|h|d&gt; [số_thiết_bị]</code>\n"
            f"Ví dụ: <code>/key 30 m</code> — 30 phút, 1 thiết bị\n"
            f"        <code>/key 1 h 3</code> — 1 giờ, 3 thiết bị\n"
            f"        <code>/key 3 d 2</code> — 3 ngày, 2 thiết bị",
            parse_mode="HTML",
        )

    try:
        val = int(args[0])
        if val <= 0:
            raise ValueError
    except ValueError:
        return await update.message.reply_text(f"{E_CROSS} Số lượng không hợp lệ.", parse_mode="HTML")

    unit_raw = args[1].strip().lower()
    if unit_raw in ("m", "min", "mins", "minute", "minutes", "phut", "phút", "p"):
        unit = "m"
        duration_label = f"{val} phút"
    elif unit_raw in ("h", "hour", "hours", "gio", "giờ", "g"):
        unit = "h"
        duration_label = f"{val} giờ"
    elif unit_raw in ("d", "day", "days", "ngay", "ngày", "n"):
        unit = "d"
        duration_label = f"{val} ngày"
    else:
        return await update.message.reply_text(
            f"{E_CROSS} Đơn vị không hợp lệ — dùng <code>m</code> (phút), <code>h</code> (giờ) hoặc <code>d</code> (ngày).",
            parse_mode="HTML",
        )

    max_devices = 1
    if len(args) >= 3:
        try:
            max_devices = int(args[2])
            if max_devices <= 0:
                raise ValueError
        except ValueError:
            return await update.message.reply_text(f"{E_CROSS} Số thiết bị không hợp lệ.", parse_mode="HTML")

    key = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
    rec = {
        "used": False,
        "created_at": get_hanoi_time().isoformat(),
        "used_by": None,
        "max_devices": max_devices,
        "devices": [],
        "minutes": 0,
        "hours": 0,
        "days": 0,
    }
    if unit == "m":
        rec["minutes"] = val
    elif unit == "h":
        rec["hours"] = val
    else:
        rec["days"] = val
    data.setdefault("keys", {})[key] = rec
    save_datakey(data)

    await update.message.reply_text(
        f"{E_PARTY} <b>Tạo Key thành công</b> {E_CROWN}\n"
        f"{E_PIN} Mã: <code>{key}</code>\n"
        f"{E_CAL} Thời hạn: <code>{duration_label}</code>\n"
        f"{E_MON} Thiết bị tối đa: <code>{max_devices}</code>",
        parse_mode="HTML",
    )


async def _approve_deposit_core(bot, data, req_id, amount, reviewer_id=None):
    req_key = str(req_id)
    req = data.get("deposit_requests", {}).get(req_key)
    if not req:
        return False, "Không tìm thấy yêu cầu nạp."
    if req.get("status") not in ("pending", "awaiting_admin"):
        return False, f"Đơn #{req_key} đã xử lý ({req.get('status')})."

    uid_str = str(req["user_id"])
    data["users"].setdefault(uid_str, {"balance": 0, "first_name": "N/A"})
    data["users"][uid_str]["balance"] = data["users"][uid_str].get("balance", 0) + int(amount)
    now_str = get_hanoi_time().strftime("%d/%m/%Y %H:%M:%S")
    req["status"] = "approved"
    req["approved_at"] = get_hanoi_time().isoformat()
    req["approved_amount"] = int(amount)
    if reviewer_id:
        req["reviewed_by"] = int(reviewer_id)
    save_datakey(data)

    u_info = data["users"][uid_str]
    acc_name = (
        f"@{u_info.get('username')}"
        if u_info.get("username") and u_info.get("username") != "No Username"
        else u_info.get("first_name", uid_str)
    )
    masked_uid = _mask_uid_for_bill(uid_str)
    await notify_checkbill_bot(
        f"{E_PIG} <b>NẠP TIỀN THÀNH CÔNG</b> {E_CLOVER}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_MAIL} Tài khoản: <code>{acc_name}</code> (<code>{masked_uid}</code>)\n"
        f"{E_BANK} Số tiền: <code>+{int(amount):,}đ</code>\n"
        f"{E_BELL} Mã đơn: <tg-spoiler>FZ{req_key}</tg-spoiler>\n"
        f"{E_CART} Hình thức: <b>Bank Auto</b>\n"
        f"{E_CLOVER} Thời gian: <code>{now_str}</code>\n"
        f"{E_BOLT} Trạng thái: <b>Đã xử lí</b>",
        button_text="Mở Bot",
        icon_key="pig",
    )

    try:
        await bot.send_message(
            int(uid_str),
            f"{E_PARTY} <b>NẠP TIỀN THÀNH CÔNG</b> {E_MONEY}\n"
            f"{E_PIN} Mã đơn: <code>#FZ{req_key}</code>\n"
            f"{E_CASH} Cộng ví: <code>+{int(amount):,}đ</code>\n"
            f"{E_CROWN} Số dư hiện tại: <code>{u_info['balance']:,}đ</code>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    return True, u_info["balance"]


async def handle_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text(
            f"{E_ALERT} Dùng: <code>/approve &lt;request_id&gt; &lt;số_tiền&gt;</code>",
            parse_mode="HTML",
        )
    try:
        req_id = args[0]
        amount = int(args[1].replace(",", "").replace(".", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await update.message.reply_text(f"{E_CROSS} Tham số không hợp lệ.", parse_mode="HTML")

    async with DATA_LOCK:
        data_fresh = load_datakey()
        ok, info = await _approve_deposit_core(
            context.bot, data_fresh, req_id, amount, reviewer_id=update.effective_user.id
        )
    if not ok:
        return await update.message.reply_text(f"{E_CROSS} {info}", parse_mode="HTML")

    req = data_fresh["deposit_requests"][str(req_id)]
    await update.message.reply_text(
        f"{E_CHECK} <b>Đã duyệt đơn #{req_id}</b> {E_PARTY}\n"
        f"{E_PIN} Khách: <code>{req['user_id']}</code>\n"
        f"{E_MONEY} Cộng: <code>+{amount:,}đ</code>\n"
        f"{E_CASH} Số dư mới: <code>{info:,}đ</code>",
        parse_mode="HTML",
    )


async def handle_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if not args:
        return await update.message.reply_text(f"{E_ALERT} Dùng: <code>/broadcast &lt;tin_nhắn&gt;</code>", parse_mode="HTML")
    message = " ".join(args)
    users = data.get("users", {})
    sent_count = 0
    for user_id in users.keys():
        try:
            await context.bot.send_message(
                int(user_id),
                f"{E_MEGA} <b>THÔNG BÁO TỪ ADMIN</b> {E_FIRE}\n\n{message}",
                parse_mode="HTML",
            )
            sent_count += 1
        except Exception:
            continue
    await update.message.reply_text(
        f"{E_CHECK} <b>Đã gửi broadcast tới {sent_count}/{len(users)} người dùng</b> {E_PARTY}",
        parse_mode="HTML",
    )


async def handle_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    await update.message.reply_text(build_stats_text(data), parse_mode="HTML")


def build_stats_text(data=None):
    if data is None:
        data = load_datakey()
    total_users = len(data.get("users", {}))
    active_users = sum(1 for u in data.get("users", {}).values() if is_key_active(u, None, data))
    active_keys = sum(1 for k in data.get("keys", {}).values() if not k.get("used", False))
    used_keys = sum(1 for k in data.get("keys", {}).values() if k.get("used", False))
    pending_dep = sum(
        1 for r in data.get("deposit_requests", {}).values() if r.get("status") in ("pending", "awaiting_admin")
    )
    pending_fk = sum(1 for r in data.get("free_key_requests", {}).values() if r.get("status") == "awaiting_admin")
    sub_count = len([x for x in data.get("sub_admins", []) if int(x) != int(ADMIN_ID)])
    price_by_days = {1: 30000, 3: 70000, 7: 90000, 30: 130000}
    revenue = sum(
        price_by_days.get(k.get("days", 0), 0)
        for k in data.get("keys", {}).values()
        if k.get("used", False) and not k.get("free_key", False)
    )
    return (
        f"{E_MON} <b>THỐNG KÊ HỆ THỐNG</b> {E_FIRE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_CROWN} Chủ bot / Admin chính: <code>{ADMIN_ID}</code>\n"
        f"{E_PARTY} Tổng Users: <code>{total_users}</code>\n"
        f"{E_CROWN} Đang có VIP: <code>{active_users}</code>\n"
        f"{E_GEAR} Admin phụ: <code>{sub_count}</code>\n"
        f"{E_CHECK} Key đã dùng: <code>{used_keys}</code>\n"
        f"{E_GIFT} Key còn trống: <code>{active_keys}</code>\n"
        f"{E_SPIN} Đơn nạp chờ duyệt: <code>{pending_dep}</code>\n"
        f"{E_BELL} Đơn Free Key 30p chờ duyệt: <code>{pending_fk}</code>\n"
        f"{E_CASH} Tổng doanh thu Key: <code>{revenue:,}đ</code> {E_MONEY}"
    )


async def build_check_game_report():
    tasks = [fetch_api_data(url, gkey) for gkey, url in API_URLS.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    rows = []
    for (gkey, _), res in zip(API_URLS.items(), results):
        if isinstance(res, dict) and res:
            w, l, total = sync_api_history_50(
                gkey, api_items=res.get("api_history"), direct_counts=res.get("direct_50"),
            )
            online = True
        else:
            w, l, total = get_50_window_stats(gkey)
            online = False
        pct = (w / total * 100.0) if total > 0 else -1.0
        rows.append({
            "key": gkey,
            "name": GAME_MAP_NAME.get(gkey, gkey.upper()),
            "win": w,
            "lose": l,
            "total": total,
            "pct": pct,
            "online": online,
        })

    rows.sort(key=lambda r: (r["pct"], r["win"], -r["lose"]), reverse=True)

    lines = [
        f"{E_CROWN} <b>CHECK GAME — TOP CHUẨN 50 PHIÊN</b> {E_FIRE}",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    valid_rows = [r for r in rows if r["total"] > 0]
    if valid_rows:
        best = valid_rows[0]
        lines.append(
            f"{E_PARTY} <b>ĐANG CHUẨN NHẤT:</b> <b>{best['name']}</b> — "
            f"{E_WIN} <code>{best['win']}</code> Đúng / {E_LOSE} <code>{best['lose']}</code> Sai (<code>{best['pct']:.1f}%</code>)"
        )
        lines.append("━━━━━━━━━━━━━━━━━━━━")

    for idx, r in enumerate(rows, 1):
        g_icon = _game_emoji(r["key"])
        t_icon = _table_emoji(r["key"])
        if r["total"] > 0:
            pct_str = f"{r['pct']:.1f}%"
            stat_part = f"{E_WIN} <code>{r['win']}</code> Đúng | {E_LOSE} <code>{r['lose']}</code> Sai (<code>{pct_str}</code>)"
        else:
            status_tag = "Online — chưa có lịch sử 50p" if r["online"] else "API offline"
            stat_part = f"{E_SPIN} <i>{status_tag}</i>"
        crown_mark = f" {E_CROWN}" if idx == 1 and r["total"] > 0 else ""
        lines.append(f"<b>{idx}.</b> {g_icon} <b>{r['name']}</b> {t_icon}{crown_mark}\n    {stat_part}")

    return "\n".join(lines)


# --- KEYBOARDS ---
def get_main_inline_keyboard(user_id, data=None):
    kb = [
        [InlineKeyboardButton("Danh Sách Game VIP", callback_data="menu_games", api_kwargs=btn_icon("game"))],
        [
            InlineKeyboardButton("Check Game (50p)", callback_data="user_checkgame", api_kwargs=btn_icon("fire")),
            InlineKeyboardButton("Hồ Sơ Cá Nhân", callback_data="menu_profile", api_kwargs=btn_icon("clip")),
        ],
        [
            InlineKeyboardButton("Mua Gói Key VIP", callback_data="menu_buykey", api_kwargs=btn_icon("bag")),
            InlineKeyboardButton("Get Key Free 30p", callback_data="menu_freekey", api_kwargs=btn_icon("gift")),
        ],
        [
            InlineKeyboardButton("Kích Hoạt Key", callback_data="menu_activate", api_kwargs=btn_icon("crown")),
            InlineKeyboardButton("Nạp Tiền Ví", callback_data="menu_deposit", api_kwargs=btn_icon("money")),
        ],
        [
            InlineKeyboardButton("Nhập Giftcode", callback_data="menu_giftcode", api_kwargs=btn_icon("party")),
            InlineKeyboardButton("Lịch Sử Mua KEY", callback_data="menu_history", api_kwargs=btn_icon("calendar")),
        ],
        [
            InlineKeyboardButton("Hỗ Trợ Khác", callback_data="menu_support", api_kwargs=btn_icon("net")),
            InlineKeyboardButton("Feedback Tool", callback_data="menu_feedback", api_kwargs=btn_icon("bell")),
        ],
    ]
    if is_admin(user_id, data):
        kb.append([InlineKeyboardButton("ADMIN TOOLS QUẢN TRỊ", callback_data="admin_tools", api_kwargs=btn_icon("gear"))])
    return InlineKeyboardMarkup(kb)


def get_game_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("SUNWIN", callback_data="game_SUNWIN", api_kwargs=btn_icon("sunwin")),
            InlineKeyboardButton("HITCLUB", callback_data="game_HITCLUB", api_kwargs=btn_icon("hitclub")),
        ],
        [
            InlineKeyboardButton("B52 CLUB", callback_data="game_B52", api_kwargs=btn_icon("b52_logo")),
            InlineKeyboardButton("BETVIP", callback_data="game_BETVIP", api_kwargs=btn_icon("betvip_logo")),
        ],
        [
            InlineKeyboardButton("LC79", callback_data="game_LC79", api_kwargs=btn_icon("lc79_logo")),
            InlineKeyboardButton("XOCDIA88", callback_data="game_XD88", api_kwargs=btn_icon("xd88_logo")),
        ],
        [
            InlineKeyboardButton("GAME 68", callback_data="game_GAME68", api_kwargs=btn_icon("game68")),
            InlineKeyboardButton("MAX789", callback_data="game_MAX789", api_kwargs=btn_icon("club789")),
        ],
        [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ])


def get_sub_inline_keyboard(game):
    menus = {
        "SUNWIN": [[InlineKeyboardButton("SUNWIN TÀI XỈU", callback_data="run_sun_tx", api_kwargs=btn_icon("table_tx"))]],
        "HITCLUB": [[
            InlineKeyboardButton("HIT TÀI XỈU", callback_data="run_hit_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("HIT MD5", callback_data="run_hit_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "B52": [[
            InlineKeyboardButton("B52 TÀI XỈU", callback_data="run_b52_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("B52 MD5", callback_data="run_b52_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "BETVIP": [[
            InlineKeyboardButton("BETVIP TÀI XỈU", callback_data="run_betvip_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("BETVIP MD5", callback_data="run_betvip_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "LC79": [[
            InlineKeyboardButton("LC79 TÀI XỈU", callback_data="run_lc79_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("LC79 MD5", callback_data="run_lc79_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "XD88": [[
            InlineKeyboardButton("XD88 TÀI XỈU", callback_data="run_xd88_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("XD88 MD5", callback_data="run_xd88_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "GAME68": [[
            InlineKeyboardButton("68 HŨ", callback_data="run_g68_hu", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("68 MD5", callback_data="run_g68_md5", api_kwargs=btn_icon("table_md5")),
        ]],
        "MAX789": [[
            InlineKeyboardButton("MAX789 TÀI XỈU", callback_data="run_max789_tx", api_kwargs=btn_icon("table_tx")),
            InlineKeyboardButton("MAX789 MD5", callback_data="run_max789_md5", api_kwargs=btn_icon("table_md5")),
        ]],
    }
    kb = [row[:] for row in menus.get(game, [])]
    kb.append([InlineKeyboardButton("Quay Lại", callback_data="menu_games", api_kwargs=btn_icon("down"))])
    return InlineKeyboardMarkup(kb)


def get_admin_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Tạo Giftcode", callback_data="admin_giftcode", api_kwargs=btn_icon("gift")),
            InlineKeyboardButton("Tạo Key VIP", callback_data="admin_createkey", api_kwargs=btn_icon("crown")),
        ],
        [
            InlineKeyboardButton("Check Game (50p)", callback_data="admin_checkgame", api_kwargs=btn_icon("fire")),
            InlineKeyboardButton("Thống Kê", callback_data="admin_stats", api_kwargs=btn_icon("monitor")),
        ],
        [
            InlineKeyboardButton("Broadcast", callback_data="admin_broadcast", api_kwargs=btn_icon("mega")),
            InlineKeyboardButton("Đơn Nạp Chờ", callback_data="admin_deposits", api_kwargs=btn_icon("money")),
        ],
        [
            InlineKeyboardButton("Danh Sách User", callback_data="admin_users", api_kwargs=btn_icon("clip")),
            InlineKeyboardButton("Add / Xóa Admin Phụ", callback_data="admin_manage_sub", api_kwargs=btn_icon("gear")),
        ],
        [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ])


def get_back_keyboard(target="menu_back", label="Quay Lại"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=target, api_kwargs=btn_icon("down"))]])


def get_deposit_keyboard(req_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Đã Chuyển Khoản", callback_data=f"dep_done:{req_id}", api_kwargs=btn_icon("check"))],
        [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ])


def get_admin_deposit_keyboard(req_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Duyệt Đơn", callback_data=f"dep_ok:{req_id}", api_kwargs=btn_icon("check")),
            InlineKeyboardButton("Từ Chối", callback_data=f"dep_no:{req_id}", api_kwargs=btn_icon("cross")),
        ],
    ])


def get_admin_freekey_keyboard(req_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Duyệt Key 30p", callback_data=f"fk_ok:{req_id}", api_kwargs=btn_icon("check")),
            InlineKeyboardButton("Từ Chối", callback_data=f"fk_no:{req_id}", api_kwargs=btn_icon("cross")),
        ],
    ])


async def send_photos_to_admins(bot, data, photo_file_ids, caption, reply_markup=None):
    if not photo_file_ids:
        return
    recipients = get_admin_recipients(data)
    chunks = [photo_file_ids[i : i + 10] for i in range(0, len(photo_file_ids), 10)]
    for aid in recipients:
        try:
            if len(photo_file_ids) == 1:
                await bot.send_photo(
                    chat_id=aid, photo=photo_file_ids[0], caption=caption,
                    parse_mode="HTML", reply_markup=reply_markup,
                )
            else:
                for c_idx, chunk in enumerate(chunks):
                    media = []
                    for idx, fid in enumerate(chunk):
                        if c_idx == 0 and idx == 0:
                            media.append(InputMediaPhoto(media=fid, caption=caption, parse_mode="HTML"))
                        else:
                            media.append(InputMediaPhoto(media=fid))
                    await bot.send_media_group(chat_id=aid, media=media)
                if reply_markup:
                    await bot.send_message(
                        chat_id=aid,
                        text=f"{E_CROWN} <b>Thao tác xử lý ({len(photo_file_ids)} ảnh)</b> {E_GEAR}",
                        parse_mode="HTML", reply_markup=reply_markup,
                    )
        except Exception as e:
            logging.warning("Send photos to admin %s failed: %s", aid, e)
            continue


def can_claim_free_key(uid_str, data):
    last_claim = data.get("free_key_claims", {}).get(uid_str)
    if not last_claim:
        return True, None
    t = parse_hanoi_time(last_claim)
    if not t:
        return True, None
    next_available = t + timedelta(hours=24)
    now = get_hanoi_time()
    if now < next_available:
        return False, next_available
    return True, None


def issue_free_30m_key(uid_str, data):
    key = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
    now = get_hanoi_time()
    data.setdefault("keys", {})[key] = {
        "days": 0, "hours": 0, "minutes": 30,
        "used": False, "created_at": now.isoformat(), "used_by": None,
        "free_key": True, "claimed_by": uid_str, "max_devices": 1, "devices": [],
    }
    data.setdefault("free_key_claims", {})[uid_str] = now.isoformat()
    save_datakey(data)
    return key


async def submit_freekey_photos_for_review(bot, chat_id, user, uid_str, photo_file_ids, note=""):
    async with DATA_LOCK:
        data = load_datakey()
        allowed, next_dt = can_claim_free_key(uid_str, data)
        if not allowed:
            return await bot.send_message(
                chat_id=chat_id,
                text=f"{E_CROSS} Đã nhận Key Free 30p hôm nay — lượt kế: <code>{next_dt.strftime('%d/%m/%Y %H:%M')}</code> {E_BELL}",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(user.id, data),
            )

        req_id = next_freekey_id(data)
        now_iso = get_hanoi_time().isoformat()
        data.setdefault("free_key_requests", {})[str(req_id)] = {
            "user_id": uid_str, "username": user.username or "", "first_name": user.first_name or "",
            "photo_file_ids": photo_file_ids, "photo_file_id": photo_file_ids[0],
            "note": note, "status": "awaiting_admin", "created_at": now_iso,
        }
        save_datakey(data)

    note_line = f"\n{E_CLIP} Ghi chú: <i>{note}</i>" if note else ""
    admin_caption = (
        f"{E_GIFT} <b>ĐƠN KEY FREE 30P #{req_id}</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} Khách: <code>{uid_str}</code> (@{user.username or 'no_username'})\n"
        f"{E_CLIP} Tên: <b>{user.first_name or 'Vô Danh'}</b>\n"
        f"{E_PIN} Số ảnh: <b>{len(photo_file_ids)}</b> — Rải <code>{FREE_KEY_BOT}</code> tối thiểu 3 box{note_line}"
    )
    await send_photos_to_admins(
        bot, data, photo_file_ids, admin_caption, reply_markup=get_admin_freekey_keyboard(req_id),
    )

    return await bot.send_message(
        chat_id=chat_id,
        text=(
            f"{E_CHECK} <b>ĐÃ GỬI {len(photo_file_ids)} ẢNH CHỜ DUYỆT</b> {E_GIFT}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PIN} Mã đơn: <code>#{req_id}</code>\n"
            f"{E_CROWN} Duyệt xong bot gửi thẳng <b>Key Free 30p</b> cho bạn."
        ),
        parse_mode="HTML", reply_markup=get_main_inline_keyboard(user.id, data),
    )


async def handle_admin_freekey_callback(update, context, action, req_id):
    q = update.callback_query
    reviewer_id = q.from_user.id

    async with DATA_LOCK:
        data = load_datakey()
        if not is_admin(reviewer_id, data):
            return await q.answer("Chỉ Admin mới có quyền duyệt!", show_alert=True)

        req_key = str(req_id)
        req = data.get("free_key_requests", {}).get(req_key)
        if not req:
            return await q.answer("Đơn không tồn tại.", show_alert=True)
        if req.get("status") != "awaiting_admin":
            return await q.answer(f"Đơn #{req_key} đã xử lý ({req.get('status')}).", show_alert=True)

        uid_str = str(req["user_id"])
        if action == "no":
            req["status"] = "rejected"
            req["reviewed_at"] = get_hanoi_time().isoformat()
            req["reviewed_by"] = reviewer_id
            save_datakey(data)
            msg_done = f"{E_CROSS} <b>Đã từ chối đơn Key Free 30p #{req_key}</b> (Khách: <code>{uid_str}</code>)."
            await safe_edit_or_send(q, msg_done)
            try:
                await context.bot.send_message(
                    int(uid_str),
                    f"{E_CROSS} <b>ĐƠN KEY FREE 30P #{req_key} BỊ TỪ CHỐI</b> {E_ALERT}\n"
                    f"{E_CLIP} Kiểm tra lại ảnh rải <code>{FREE_KEY_BOT}</code> đủ 3 box hoặc liên hệ {ADMIN_HANDLE}.",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return

        if action == "ok":
            allowed, _ = can_claim_free_key(uid_str, data)
            if not allowed:
                req["status"] = "rejected"
                req["reviewed_at"] = get_hanoi_time().isoformat()
                req["reviewed_by"] = reviewer_id
                save_datakey(data)
                return await q.answer("Khách này đã nhận Key Free 30p trong 24h qua!", show_alert=True)

            key = issue_free_30m_key(uid_str, data)
            now_str = get_hanoi_time().strftime("%d/%m/%Y %H:%M:%S")
            req["status"] = "approved"
            req["issued_key"] = key
            req["reviewed_at"] = get_hanoi_time().isoformat()
            req["reviewed_by"] = reviewer_id
            save_datakey(data)

            u_info = data.get("users", {}).get(uid_str, {})
            acc_name = (
                f"@{u_info.get('username')}"
                if u_info.get("username") and u_info.get("username") != "No Username"
                else req.get("first_name") or uid_str
            )
            masked_key = _mask_key_for_bill(key)
            masked_uid = _mask_uid_for_bill(uid_str)
            await notify_checkbill_bot(
                f"{E_GIFT} <b>DUYỆT KEY FREE 30P THÀNH CÔNG</b> {E_CLOVER}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_MAIL} Tài khoản: <code>{acc_name}</code> (<code>{masked_uid}</code>)\n"
                f"{E_CART} Gói & giá: <b>Key Free 30 Phút</b> — <code>0đ</code>\n"
                f"{E_BANK} Mã key: <tg-spoiler>{masked_key}</tg-spoiler>\n"
                f"{E_CLOVER} Thời gian: <code>{now_str}</code>\n"
                f"{E_BOLT} Trạng thái: <b>Đã xử lí</b>",
                button_text="Mở Bot", icon_key="bolt",
            )

            msg_done = (
                f"{E_CHECK} <b>Đã duyệt & gửi Key Free 30p #{req_key}</b> {E_PARTY}\n"
                f"{E_PIN} Khách: <code>{uid_str}</code>\n"
                f"{E_GIFT} Key 30p: <code>{key}</code>"
            )
            await safe_edit_or_send(q, msg_done)
            try:
                await context.bot.send_message(
                    int(uid_str),
                    f"{E_PARTY} <b>ĐÃ DUYỆT KEY FREE 30P</b> {E_GIFT}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{E_PIN} Mã đơn: <code>#{req_key}</code>\n"
                    f"{E_CROWN} Key 30p: <code>{key}</code>\n"
                    f"{E_BELL} Hạn dùng: <b>30 phút</b> {E_FIRE}\n"
                    f"{E_CHECK} Vào <b>Kích Hoạt Key</b> dán mã để dùng ngay.",
                    parse_mode="HTML",
                )
            except Exception:
                pass


# --- DEPOSIT & VIETQR + APIBANK AUTO VERIFY ---
def _tlv(tag, val):
    return f"{tag}{len(val):02d}{val}"


def _crc16_ccitt(data_bytes):
    crc = 0xFFFF
    for b in data_bytes:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def build_emvco_vietqr_payload(bank_id, account_no, amount, memo):
    bin_code = BANK_BIN_MAP.get(str(bank_id).upper().strip(), str(bank_id).strip())
    acc_clean = str(account_no).strip()
    amt_str = str(int(amount))
    memo_clean = re.sub(r"[^A-Za-z0-9 ]", "", str(memo)).strip()[:25]

    beneficiary_info = _tlv("00", bin_code) + _tlv("01", acc_clean)
    merchant_acc_info = _tlv("00", "A000000727") + _tlv("01", beneficiary_info) + _tlv("02", "QRIBFTTA")
    additional_data = _tlv("08", memo_clean)

    raw_payload = (
        _tlv("00", "01")
        + _tlv("01", "12")
        + _tlv("38", merchant_acc_info)
        + _tlv("53", "704")
        + _tlv("54", amt_str)
        + _tlv("58", "VN")
        + _tlv("62", additional_data)
        + "6304"
    )
    return raw_payload + _crc16_ccitt(raw_payload.encode("utf-8"))


def render_local_vietqr_png(bank_id, account_no, amount, memo):
    if not HAS_LOCAL_QR:
        raise RuntimeError("Thiếu thư viện qrcode/pillow (chạy: pip install qrcode[pil] pillow)")
    payload = build_emvco_vietqr_payload(bank_id, account_no, amount, memo)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _normalize_to_png_bytes(raw_bytes):
    if HAS_LOCAL_QR:
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    return raw_bytes


def build_vietqr_image_url(amount, memo):
    query = urlencode({
        "amount": int(amount),
        "addInfo": str(memo),
        "accountName": str(VIETQR_ACCOUNT_NAME),
    })
    return f"https://img.vietqr.io/image/{VIETQR_BANK_ID}-{VIETQR_ACCOUNT_NO}-{VIETQR_TEMPLATE}.png?{query}"


async def download_vietqr_bytes(amount, memo):
    qr_url = build_vietqr_image_url(amount, memo)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "image/png,image/jpeg,image/webp,*/*",
        "Referer": "https://vietqr.io/",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False, headers=headers) as client:
            r = await client.get(qr_url)
            if r.status_code == 200 and len(r.content) > 500:
                ctype = r.headers.get("content-type", "").lower()
                if "svg" not in ctype and "html" not in ctype:
                    return _normalize_to_png_bytes(r.content), qr_url

            acq_id = BANK_BIN_MAP.get(VIETQR_BANK_ID.upper(), VIETQR_BANK_ID)
            payload = {
                "accountNo": str(VIETQR_ACCOUNT_NO),
                "accountName": str(VIETQR_ACCOUNT_NAME),
                "acqId": int(acq_id) if str(acq_id).isdigit() else acq_id,
                "amount": int(amount),
                "addInfo": str(memo),
                "template": VIETQR_TEMPLATE,
            }
            api_r = await client.post("https://api.vietqr.io/v2/generate", json=payload)
            if api_r.status_code == 200:
                j = api_r.json()
                data_url = (j.get("data") or {}).get("qrDataURL") or ""
                if "base64," in data_url:
                    b64_str = data_url.split("base64,", 1)[1]
                    return _normalize_to_png_bytes(base64.b64decode(b64_str)), qr_url
    except Exception as e:
        logging.warning("VietQR remote fetch failed (%s), using local EMVCo QR: %s", qr_url, e)

    local_png = render_local_vietqr_png(VIETQR_BANK_ID, VIETQR_ACCOUNT_NO, amount, memo)
    return local_png, qr_url


def _parse_bank_amount(val):
    if val is None or isinstance(val, bool):
        return 0
    if isinstance(val, (int, float)):
        return int(round(val))
    s = str(val).strip()
    if not s:
        return 0
    m = re.search(r"[-+]?\d[\d,\.]*", s)
    if not m:
        return 0
    num_str = m.group(0)
    if "," in num_str and "." in num_str:
        if num_str.rfind(",") > num_str.rfind("."):
            num_str = num_str.replace(".", "").replace(",", ".")
        else:
            num_str = num_str.replace(",", "")
    elif "," in num_str:
        parts = num_str.split(",")
        if len(parts[-1]) == 3 and all(len(p) <= 3 for p in parts[1:]):
            num_str = num_str.replace(",", "")
        else:
            num_str = num_str.replace(",", ".")
    elif "." in num_str:
        parts = num_str.split(".")
        if len(parts[-1]) == 3 and all(len(p) <= 3 for p in parts[1:]):
            num_str = num_str.replace(".", "")
    try:
        return int(round(float(num_str)))
    except ValueError:
        digits = re.sub(r"[^\d]", "", num_str)
        return int(digits) if digits else 0


def _collect_tx_dicts(obj, out, depth=0):
    if depth > 5 or obj is None:
        return
    if isinstance(obj, list):
        if obj and all(isinstance(x, dict) for x in obj):
            out.extend(obj)
            return
        for item in obj:
            _collect_tx_dicts(item, out, depth + 1)
    elif isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _collect_tx_dicts(v, out, depth + 1)


def _extract_bank_transactions(raw):
    found = []
    _collect_tx_dicts(raw, found, depth=0)
    dedup = []
    seen = set()
    for tx in found:
        sig = json.dumps(tx, sort_keys=True, ensure_ascii=False)
        if sig not in seen:
            seen.add(sig)
            dedup.append(tx)
    return dedup


def _extract_tx_description(tx):
    parts = []
    for k, val in tx.items():
        kl = str(k).lower()
        if any(
            w in kl
            for w in (
                "desc", "content", "noi_dung", "comment", "memo",
                "remark", "narration", "detail", "note", "msg", "text", "body",
            )
        ):
            if isinstance(val, (str, int, float)):
                parts.append(str(val))
    return " ".join(parts).upper()


def _extract_tx_amount(tx):
    priority_keys = (
        "amount", "creditamount", "credit_amount", "so_tien", "money",
        "tien_vao", "in_amount", "value", "total", "price",
    )
    for pk in priority_keys:
        for k, v in tx.items():
            if str(k).lower() == pk and v is not None:
                amt = _parse_bank_amount(v)
                if amt > 0:
                    return amt
    for k, v in tx.items():
        kl = str(k).lower()
        if any(w in kl for w in ("amount", "tien", "money", "value")) and "balance" not in kl and "so_du" not in kl:
            amt = _parse_bank_amount(v)
            if amt > 0:
                return amt
    return 0


def _memo_matches_desc(memo, desc):
    memo_u = re.sub(r"[^A-Z0-9]", "", str(memo).upper())
    desc_compact = re.sub(r"[^A-Z0-9]", "", str(desc).upper())
    if not memo_u or not desc_compact:
        return False
    if memo_u in desc_compact:
        return True
    m = re.match(r"^([A-Z]+)(\d+)$", memo_u)
    if m:
        prefix, num = m.group(1), m.group(2)
        pattern = rf"{re.escape(prefix)}[\s_\-:/#]*0*{re.escape(num)}(?!\d)"
        if re.search(pattern, str(desc).upper()):
            return True
    return False


async def scan_bank_and_approve(bot, target_req_id=None):
    """Quét APIBANK_URL và duyệt đơn ngay khi khớp đúng nội dung + số tiền."""
    if not APIBANK_URL:
        return None, "Chưa cấu hình APIBANK_URL."
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            r = await client.get(APIBANK_URL)
    except Exception as e:
        logging.warning("scan_bank_and_approve request failed: %s", e)
        return None, f"Lỗi gọi API Bank: {e}"

    if r.status_code != 200:
        logging.warning("APIBANK_URL HTTP %s: %s", r.status_code, r.text[:300])
        return None, f"API Bank lỗi HTTP {r.status_code}."

    try:
        payload = r.json()
    except Exception as e:
        logging.warning("APIBANK_URL invalid JSON (%s): %s", e, r.text[:300])
        return None, f"API Bank không trả JSON hợp lệ."

    txs = _extract_bank_transactions(payload)
    if not txs:
        logging.info("APIBANK_URL returned 0 tx items. Raw snippet: %s", str(payload)[:400])
        return None, "Chưa thấy giao dịch nào từ API Bank."

    async with DATA_LOCK:
        data = load_datakey()
        all_pending = {
            k: v
            for k, v in data.get("deposit_requests", {}).items()
            if v.get("status") == "pending" and int(v.get("expected_amount", 0)) > 0
        }
        if not all_pending:
            return None, "Không có đơn nạp nào đang chờ duyệt."

        if target_req_id is not None:
            t_key = str(target_req_id)
            if t_key not in all_pending:
                cur_st = data.get("deposit_requests", {}).get(t_key, {}).get("status", "unknown")
                return None, f"Đơn #{t_key} trạng thái: {cur_st}."
            pending_reqs = {t_key: all_pending[t_key]}
        else:
            pending_reqs = all_pending

        processed_set = set(str(x) for x in data.get("processed_tx_ids", []))

        for tx in txs:
            amt = _extract_tx_amount(tx)
            desc = _extract_tx_description(tx)
            if amt <= 0 or not desc:
                continue

            raw_tx_id = (
                tx.get("id")
                or tx.get("transactionID")
                or tx.get("refNo")
                or tx.get("ma_gd")
                or tx.get("transId")
                or tx.get("tid")
            )
            fallback_id = f"tx_{amt}_{re.sub(r'[^A-Z0-9]', '', desc)[:40]}"
            tx_id = str(raw_tx_id) if raw_tx_id not in (None, "") else fallback_id

            for req_k, req_v in pending_reqs.items():
                memo = str(req_v.get("memo") or f"FZ{req_k}").upper()
                expected_amt = int(req_v.get("expected_amount", 0))

                # Chỉ bỏ qua tx_id đã dùng nếu đơn đó không còn pending
                if tx_id in processed_set and req_v.get("status") != "pending":
                    continue

                if _memo_matches_desc(memo, desc) and amt == expected_amt:
                    processed_set.add(tx_id)
                    data["processed_tx_ids"] = list(processed_set)[-1000:]
                    save_datakey(data)
                    ok, _ = await _approve_deposit_core(bot, data, req_k, amt, reviewer_id=None)
                    if ok:
                        return req_k, f"Khớp nội dung {memo} và số tiền {amt:,}đ!"

        if target_req_id is not None:
            t_v = pending_reqs.get(str(target_req_id))
            if t_v:
                memo = str(t_v.get("memo") or f"FZ{target_req_id}").upper()
                exp_a = int(t_v.get("expected_amount", 0))
                sample_txs = [
                    f"{_extract_tx_amount(x):,}đ | {_extract_tx_description(x)[:35]}"
                    for x in txs[:3]
                ]
                logging.info(
                    "No match for req #%s (memo=%s, amt=%s). Sample bank txs: %s",
                    target_req_id, memo, exp_a, sample_txs,
                )
                return None, f"Chưa thấy giao dịch đúng nội dung {memo} và số tiền {exp_a:,}đ."

    return None, "Chưa có giao dịch khớp nội dung và số tiền."


async def apibank_auto_verify_worker(bot):
    while True:
        try:
            await scan_bank_and_approve(bot, target_req_id=None)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logging.warning("apibank_auto_verify_worker error: %s", e)

        await asyncio.sleep(3.0)


async def send_vietqr_deposit_card(chat_id, user, context, amount):
    async with DATA_LOCK:
        data = load_datakey()
        uid = ensure_user(data, user)
        req_id = next_request_id(data)
        memo = f"FZ{req_id}"
        data.setdefault("deposit_requests", {})[str(req_id)] = {
            "user_id": uid,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "expected_amount": int(amount),
            "memo": memo,
            "status": "pending",
            "created_at": get_hanoi_time().isoformat(),
            "approved_at": None,
            "approved_amount": None,
        }
        save_datakey(data)

    caption = (
        f"{E_MONEY} <b>CỔNG NẠP TIỀN TỰ ĐỘNG (VIETQR)</b> {E_CASH}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PIN} Mã đơn: <code>#{req_id}</code>\n"
        f"{E_BANK} Ngân hàng: <b>{VIETQR_BANK_ID}</b> — STK: <code>{VIETQR_ACCOUNT_NO}</code>\n"
        f"{E_CROWN} Chủ TK: <b>{VIETQR_ACCOUNT_NAME}</b>\n"
        f"{E_CASH} Số tiền: <code>{int(amount):,}đ</code>\n"
        f"{E_CLIP} Nội dung CK: <code>{memo}</code>\n"
        f"{E_CHECK} Chuyển khoản xong bấm <b>Đã Chuyển Khoản</b> (hoặc chờ bot tự duyệt)."
    )

    try:
        qr_bytes, _ = await download_vietqr_bytes(amount, memo)
        bio = io.BytesIO(qr_bytes)
        bio.name = f"vietqr_{memo}.png"
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(bio, filename=f"vietqr_{memo}.png"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_deposit_keyboard(req_id),
        )
    except Exception as e:
        logging.exception("send_vietqr_deposit_card failed: %s", e)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{caption}\n\n{E_ALERT} <i>Lỗi tạo ảnh QR ({e}) — vui lòng chuyển khoản đúng thông tin trên.</i>",
            parse_mode="HTML",
            reply_markup=get_deposit_keyboard(req_id),
        )


async def handle_deposit_callback(update, context, action, req_id):
    q = update.callback_query
    uid = str(q.from_user.id)

    data = load_datakey()
    req = data.get("deposit_requests", {}).get(str(req_id))
    if not req:
        return await q.answer("Đơn nạp không tồn tại.", show_alert=True)
    if str(req["user_id"]) != uid and not is_admin(q.from_user.id, data):
        return await q.answer("Đơn này không thuộc tài khoản của bạn!", show_alert=True)

    if action == "done":
        if req.get("status") == "approved":
            u_bal = data.get("users", {}).get(uid, {}).get("balance", 0)
            return await safe_edit_or_send(
                q,
                f"{E_PARTY} <b>ĐƠN #{req_id} ĐÃ ĐƯỢC DUYỆT</b> {E_CHECK}\n"
                f"{E_CASH} Số dư hiện tại: <code>{u_bal:,}đ</code>",
                reply_markup=get_back_keyboard(),
            )

        matched_id, info_msg = await scan_bank_and_approve(context.bot, target_req_id=req_id)
        if matched_id:
            data_after = load_datakey()
            u_bal = data_after.get("users", {}).get(uid, {}).get("balance", 0)
            return await safe_edit_or_send(
                q,
                f"{E_PARTY} <b>NẠP TIỀN THÀNH CÔNG (ĐƠN #{req_id})</b> {E_MONEY}\n"
                f"{E_CHECK} {info_msg}\n"
                f"{E_CROWN} Số dư hiện tại: <code>{u_bal:,}đ</code>",
                reply_markup=get_back_keyboard(),
            )

        memo = str(req.get("memo") or f"FZ{req_id}").upper()
        exp_a = int(req.get("expected_amount", 0))
        return await q.answer(
            f"Chưa thấy giao dịch đúng nội dung {memo} và số tiền {exp_a:,}đ. Bấm lại sau vài giây!",
            show_alert=True,
        )


async def handle_admin_deposit_callback(update, context, action, req_id):
    q = update.callback_query
    reviewer_id = q.from_user.id

    async with DATA_LOCK:
        data = load_datakey()
        if not is_admin(reviewer_id, data):
            return await q.answer("Chỉ Admin mới có quyền duyệt!", show_alert=True)

        req_key = str(req_id)
        req = data.get("deposit_requests", {}).get(req_key)
        if not req:
            return await q.answer("Đơn nạp không tồn tại.", show_alert=True)
        if req["status"] not in ("awaiting_admin", "pending"):
            return await q.answer(f"Đơn #{req_key} đã xử lý ({req['status']}).", show_alert=True)

        if action == "no":
            req["status"] = "rejected"
            req["approved_at"] = get_hanoi_time().isoformat()
            req["reviewed_by"] = reviewer_id
            save_datakey(data)
            await safe_edit_or_send(q, f"{E_CROSS} <b>Đã từ chối đơn nạp #{req_key}</b>")
            try:
                await context.bot.send_message(
                    int(req["user_id"]),
                    f"{E_CROSS} <b>ĐƠN NẠP #{req_key} BỊ TỪ CHỐI</b> {E_ALERT}\n"
                    f"{E_BELL} Liên hệ {ADMIN_HANDLE} nếu cần hỗ trợ.",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return

        if action == "ok":
            pending_map = context.bot_data.setdefault("pending_deposit_approvals", {})
            pending_map[str(reviewer_id)] = req_key
            context.user_data["admin_approve_req"] = req_key
            context.user_data["waiting_approve_amount"] = True
            await safe_edit_or_send(
                q,
                f"{E_CHECK} <b>DUYỆT ĐƠN NẠP #{req_key}</b> {E_MONEY}\n"
                f"{E_PIN} Khách: <code>{req['user_id']}</code>\n"
                f"{E_CASH} Nhập số tiền cần cộng (VD: 50000):",
            )


async def handle_approve_amount(update, context):
    msg = update.message.text.strip()
    reviewer_id = str(update.effective_user.id)
    try:
        amount = int(msg.replace(",", "").replace(".", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await update.message.reply_text(f"{E_CROSS} Số tiền không hợp lệ — nhập lại số nguyên dương:", parse_mode="HTML")

    req_id = context.bot_data.get("pending_deposit_approvals", {}).get(reviewer_id) or context.user_data.get("admin_approve_req")
    if not req_id:
        return await update.message.reply_text(f"{E_CROSS} Không có đơn nạp đang chờ nhập tiền.", parse_mode="HTML")

    async with DATA_LOCK:
        data = load_datakey()
        ok, info = await _approve_deposit_core(
            context.bot, data, req_id, amount, reviewer_id=update.effective_user.id
        )

    context.bot_data.get("pending_deposit_approvals", {}).pop(reviewer_id, None)
    context.user_data.pop("waiting_approve_amount", None)
    context.user_data.pop("admin_approve_req", None)

    if not ok:
        return await update.message.reply_text(f"{E_CROSS} {info}", parse_mode="HTML")

    req = data["deposit_requests"][str(req_id)]
    await update.message.reply_text(
        f"{E_PARTY} <b>Đã duyệt đơn #{req_id}</b> {E_CHECK}\n"
        f"{E_PIN} Khách: <code>{req['user_id']}</code>\n"
        f"{E_MONEY} Cộng: <code>+{amount:,}đ</code>\n"
        f"{E_CASH} Số dư mới: <code>{info:,}đ</code>",
        parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
    )


async def forward_feedback_to_admin(bot, chat_id, user, photo_file_ids=None, content_text=""):
    photo_list = photo_file_ids or []
    uid = user.id
    data = load_datakey()
    safe_content = content_text.strip() if content_text else "(Không có nội dung chữ)"
    count_info = f"<b>{len(photo_list)} ảnh</b>" if photo_list else "<b>không có ảnh</b>"
    admin_caption = (
        f"{E_BELL} <b>FEEDBACK MỚI TỪ KHÁCH</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} Tên: <b>{user.first_name}</b> (@{user.username or 'no_username'})\n"
        f"{E_PIN} ID: <code>{uid}</code>\n"
        f"{E_CLIP} Đính kèm: {count_info}\n"
        f"{E_MEGA} Nội dung:\n<i>{safe_content}</i>"
    )
    if photo_list:
        await send_photos_to_admins(bot, data, photo_list, admin_caption)
    else:
        recipients = get_admin_recipients(data)
        for aid in recipients:
            try:
                await bot.send_message(chat_id=aid, text=admin_caption, parse_mode="HTML")
            except Exception:
                continue

    summary_part = f"<b>{len(photo_list)} ảnh + nội dung</b>" if photo_list else "<b>nội dung</b>"
    await bot.send_message(
        chat_id=chat_id,
        text=(
            f"{E_PARTY} <b>ĐÃ GỬI FEEDBACK TỚI ADMIN</b> {E_CHECK}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_CROWN} Đã chuyển {summary_part} cho Admin.\n"
            f"{E_BELL} Cảm ơn bạn đã góp ý."
        ),
        parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
    )


def _schedule_album_debounce(context, chat_id, user, uid_str, group_key, mode):
    old_task = MEDIA_GROUP_TIMERS.get(group_key)
    if old_task and not old_task.done():
        old_task.cancel()

    async def _worker():
        try:
            await asyncio.sleep(1.2)
        except asyncio.CancelledError:
            return
        MEDIA_GROUP_TIMERS.pop(group_key, None)
        MEDIA_GROUP_ACTIVE_MODE.pop(group_key, None)
        photo_ids = MEDIA_GROUP_BUFFERS.pop(group_key, [])
        cap_final = MEDIA_GROUP_CAPTIONS.pop(group_key, "")
        if not photo_ids:
            return

        if mode == "freekey":
            context.user_data.pop("waiting_freekey_photo", None)
            await submit_freekey_photos_for_review(
                context.bot, chat_id, user, uid_str, photo_ids, note=cap_final
            )
        elif mode == "feedback":
            if cap_final:
                context.user_data.pop("waiting_feedback", None)
                context.user_data.pop("feedback_photo_ids", None)
                await forward_feedback_to_admin(
                    context.bot, chat_id, user, photo_file_ids=photo_ids, content_text=cap_final
                )
            else:
                existing = context.user_data.get("feedback_photo_ids", [])
                existing.extend(photo_ids)
                context.user_data["feedback_photo_ids"] = existing
                context.user_data["waiting_feedback"] = True
                kb = [
                    [InlineKeyboardButton(f"Gửi {len(existing)} Ảnh Ngay", callback_data="fb_send_photo_only", api_kwargs=btn_icon("check"))],
                    [InlineKeyboardButton("Hủy Feedback", callback_data="menu_back", api_kwargs=btn_icon("down"))],
                ]
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"{E_CHECK} <b>Đã nhận {len(existing)} ảnh feedback</b> {E_CLIP}\n"
                        f"{E_BELL} Nhập nội dung mô tả hoặc bấm gửi ảnh ngay."
                    ),
                    parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb),
                )

    MEDIA_GROUP_TIMERS[group_key] = asyncio.create_task(_worker())


# --- HANDLE PHOTO MESSAGE ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_datakey()
    uid = ensure_user(data, user)

    photo = update.message.photo[-1]
    caption = (update.message.caption or "").strip()
    media_group_id = update.message.media_group_id

    if media_group_id:
        for prefix, m_name in (("fk", "freekey"), ("fb", "feedback")):
            g_key = f"{prefix}:{uid}:{media_group_id}"
            if MEDIA_GROUP_ACTIVE_MODE.get(g_key) == m_name:
                MEDIA_GROUP_BUFFERS.setdefault(g_key, []).append(photo.file_id)
                if caption:
                    MEDIA_GROUP_CAPTIONS[g_key] = caption
                _schedule_album_debounce(context, update.effective_chat.id, user, uid, g_key, m_name)
                return

    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return

    if context.user_data.get("waiting_freekey_photo"):
        if media_group_id:
            group_key = f"fk:{uid}:{media_group_id}"
            MEDIA_GROUP_ACTIVE_MODE[group_key] = "freekey"
            MEDIA_GROUP_BUFFERS[group_key] = [photo.file_id]
            if caption:
                MEDIA_GROUP_CAPTIONS[group_key] = caption
            _schedule_album_debounce(context, update.effective_chat.id, user, uid, group_key, "freekey")
            return

        context.user_data.pop("waiting_freekey_photo", None)
        return await submit_freekey_photos_for_review(
            context.bot, update.effective_chat.id, user, uid, [photo.file_id], note=caption
        )

    if not context.user_data.get("waiting_feedback"):
        return

    if media_group_id:
        group_key = f"fb:{uid}:{media_group_id}"
        MEDIA_GROUP_ACTIVE_MODE[group_key] = "feedback"
        MEDIA_GROUP_BUFFERS[group_key] = [photo.file_id]
        if caption:
            MEDIA_GROUP_CAPTIONS[group_key] = caption
        _schedule_album_debounce(context, update.effective_chat.id, user, uid, group_key, "feedback")
        return

    if caption:
        context.user_data.pop("waiting_feedback", None)
        context.user_data.pop("feedback_photo_ids", None)
        return await forward_feedback_to_admin(
            context.bot, update.effective_chat.id, user, photo_file_ids=[photo.file_id], content_text=caption
        )

    existing_ids = context.user_data.get("feedback_photo_ids", [])
    existing_ids.append(photo.file_id)
    context.user_data["feedback_photo_ids"] = existing_ids
    kb = [
        [InlineKeyboardButton(f"Gửi {len(existing_ids)} Ảnh Ngay", callback_data="fb_send_photo_only", api_kwargs=btn_icon("check"))],
        [InlineKeyboardButton("Hủy Feedback", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ]
    await update.message.reply_text(
        f"{E_CHECK} <b>Đã nhận {len(existing_ids)} ảnh feedback</b> {E_CLIP}\n"
        f"{E_BELL} Nhập nội dung mô tả hoặc bấm gửi ảnh ngay.",
        parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb),
    )


# --- HANDLE TEXT INPUT ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    user = update.effective_user
    uid = user.id
    data = load_datakey()
    uid_str = ensure_user(data, user)

    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return

    if context.user_data.get("waiting_deposit_amount"):
        try:
            amount = int(msg.replace(",", "").replace(".", "").replace("đ", "").replace("d", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            return await update.message.reply_text(
                f"{E_CROSS} Số tiền không hợp lệ — nhập số tiền muốn nạp (VD: <code>30000</code>):",
                parse_mode="HTML", reply_markup=get_back_keyboard(),
            )
        context.user_data.pop("waiting_deposit_amount", None)
        return await send_vietqr_deposit_card(update.effective_chat.id, user, context, amount)

    if context.user_data.get("waiting_approve_amount") or context.bot_data.get("pending_deposit_approvals", {}).get(str(uid)):
        return await handle_approve_amount(update, context)

    if context.user_data.get("waiting_freekey_photo"):
        return await update.message.reply_text(
            f"{E_ALERT} Gửi ảnh chứng minh rải <code>{FREE_KEY_BOT}</code> tối thiểu 3 box để duyệt.",
            parse_mode="HTML", reply_markup=get_back_keyboard(),
        )

    if context.user_data.get("waiting_sub_admin"):
        context.user_data.pop("waiting_sub_admin", None)
        if not is_admin(uid, data):
            return
        try:
            target_id = int(msg)
            if target_id == int(ADMIN_ID):
                return await update.message.reply_text(
                    f"{E_ALERT} ID <code>{ADMIN_ID}</code> là Chủ Bot / Admin chính.",
                    parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
                )
            sub_list = [int(x) for x in data.get("sub_admins", []) if int(x) != int(ADMIN_ID)]
            if target_id in sub_list:
                sub_list.remove(target_id)
                data["sub_admins"] = [int(ADMIN_ID)] + sub_list
                save_datakey(data)
                status_text = f"{E_CROSS} Đã gỡ Admin phụ ID <code>{target_id}</code>."
            else:
                sub_list.append(target_id)
                data["sub_admins"] = [int(ADMIN_ID)] + sub_list
                save_datakey(data)
                status_text = f"{E_CHECK} Đã thêm Admin phụ ID <code>{target_id}</code>."
            return await update.message.reply_text(
                status_text, parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
            )
        except ValueError:
            return await update.message.reply_text(
                f"{E_CROSS} ID không hợp lệ — nhập số ID Telegram.",
                parse_mode="HTML", reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
            )

    if context.user_data.get("waiting_for_giftcode"):
        try:
            amount = int(msg.replace(",", "").replace(".", ""))
            if amount <= 0:
                await update.message.reply_text(f"{E_CROSS} Số tiền phải lớn hơn 0.", parse_mode="HTML")
                return
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
            data.setdefault("giftcodes", {})[code] = {
                "amount": amount, "created_at": get_hanoi_time().isoformat(),
                "created_by": uid, "used_by": None, "used_at": None, "is_used": False,
            }
            save_datakey(data)
            context.user_data["waiting_for_giftcode"] = False
            await update.message.reply_text(
                f"{E_GIFT} <b>TẠO GIFTCODE THÀNH CÔNG</b> {E_PARTY}\n"
                f"{E_MONEY} Giá trị: <code>{amount:,}đ</code>\n"
                f"{E_PIN} Mã: <code>{code}</code>",
                parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
            )
        except ValueError:
            await update.message.reply_text(f"{E_CROSS} Nhập số tiền hợp lệ.", parse_mode="HTML")
        return

    if context.user_data.get("awaiting_key"):
        key = msg.upper()
        if key in data.get("keys", {}) and not data["keys"][key].get("used"):
            kinfo = data["keys"][key]
            max_devices = int(kinfo.get("max_devices", 1) or 1)
            devices = kinfo.setdefault("devices", [])
            if uid_str not in devices:
                if len(devices) >= max_devices:
                    context.user_data["awaiting_key"] = False
                    return await update.message.reply_text(
                        f"{E_CROSS} <b>KEY ĐÃ ĐẠT GIỚI HẠN THIẾT BỊ</b>\n"
                        f"{E_MON} Tối đa: <code>{max_devices}</code> thiết bị\n"
                        f"{E_PIN} Đã dùng: <code>{len(devices)}</code>",
                        parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
                    )
                devices.append(uid_str)

            now = get_hanoi_time()
            cur_exp = parse_hanoi_time(data["users"][uid_str].get("key_expires"))
            base_time = cur_exp if (cur_exp and cur_exp > now) else now
            if kinfo.get("minutes"):
                exp = base_time + timedelta(minutes=int(kinfo["minutes"]))
                duration_label = f"{int(kinfo['minutes'])} phút"
            elif kinfo.get("hours"):
                exp = base_time + timedelta(hours=int(kinfo["hours"]))
                duration_label = f"{int(kinfo['hours'])} giờ"
            else:
                days = kinfo.get("days", 0)
                exp = base_time + timedelta(days=days)
                duration_label = f"{days} ngày"

            data["users"][uid_str]["key_expires"] = exp.isoformat()
            if len(devices) >= max_devices:
                data["keys"][key]["used"] = True
                data["keys"][key]["used_by"] = uid_str
            data["keys"][key]["used_at"] = now.isoformat()
            save_datakey(data)
            context.user_data["awaiting_key"] = False

            acc_name = f"@{user.username}" if user.username else (user.first_name or uid_str)
            masked_key = _mask_key_for_bill(key)
            masked_uid = _mask_uid_for_bill(uid_str)
            await notify_checkbill_bot(
                f"{E_CLOVER} <b>KÍCH HOẠT KEY THÀNH CÔNG</b> {E_BOLT}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_MAIL} Tài khoản: <code>{acc_name}</code> (<code>{masked_uid}</code>)\n"
                f"{E_CART} Gói & hạn: <b>{duration_label}</b>\n"
                f"{E_MON} Thiết bị: <code>{len(devices)}/{max_devices}</code>\n"
                f"{E_BANK} Mã key: <tg-spoiler>{masked_key}</tg-spoiler>\n"
                f"{E_BELL} Hết hạn: <code>{exp.strftime('%d/%m/%Y %H:%M')}</code>\n"
                f"{E_BOLT} Trạng thái: <b>Đã xử lí</b>",
                button_text="Mở Bot", icon_key="bolt",
            )

            await update.message.reply_text(
                f"{E_PARTY} <b>KÍCH HOẠT KEY THÀNH CÔNG</b> {E_CROWN}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_PIN} Key: <code>{key}</code>\n"
                f"{E_CAL} Thời hạn: <code>{duration_label}</code>\n"
                f"{E_BELL} Hết hạn: <code>{exp.strftime('%d/%m/%Y %H:%M')}</code>\n"
                f"{E_MON} Thiết bị: <code>{len(devices)}/{max_devices}</code> {E_FIRE}",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
            )
        else:
            context.user_data["awaiting_key"] = False
            await update.message.reply_text(
                f"{E_CROSS} <b>Key không tồn tại hoặc đã sử dụng hết slot</b>",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
            )
        return

    if context.user_data.get("waiting_giftcode_input"):
        gc = msg.upper()
        if gc in data.get("giftcodes", {}):
            info = data["giftcodes"][gc]
            if info.get("is_used", False):
                context.user_data["waiting_giftcode_input"] = False
                await update.message.reply_text(
                    f"{E_CROSS} <b>Giftcode đã được sử dụng</b>",
                    parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
                )
            else:
                amount = info["amount"]
                data["users"][uid_str]["balance"] = data["users"][uid_str].get("balance", 0) + amount
                info.update({"is_used": True, "used_by": uid_str, "used_at": get_hanoi_time().isoformat()})
                save_datakey(data)
                context.user_data["waiting_giftcode_input"] = False
                await update.message.reply_text(
                    f"{E_PARTY} <b>NHẬP GIFTCODE THÀNH CÔNG</b> {E_GIFT}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{E_MONEY} Cộng ví: <code>+{amount:,}đ</code>\n"
                    f"{E_CASH} Số dư mới: <code>{data['users'][uid_str]['balance']:,}đ</code> {E_CROWN}",
                    parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
                )
        else:
            context.user_data["waiting_giftcode_input"] = False
            await update.message.reply_text(
                f"{E_CROSS} <b>Giftcode không hợp lệ</b>",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data),
            )
        return

    if context.user_data.get("waiting_feedback"):
        photo_ids = context.user_data.pop("feedback_photo_ids", [])
        context.user_data["waiting_feedback"] = False
        return await forward_feedback_to_admin(
            context.bot, update.effective_chat.id, user, photo_file_ids=photo_ids, content_text=msg
        )

    if context.user_data.get("waiting_create_key"):
        parts = msg.split()
        if len(parts) < 2:
            return await update.message.reply_text(
                f"{E_ALERT} Nhập: <code>&lt;số&gt; &lt;m|h|d&gt; [số_thiết_bị]</code>\n"
                f"VD: <code>30 m</code> / <code>1 h 3</code> / <code>3 d 2</code>",
                parse_mode="HTML",
            )
        try:
            val = int(parts[0])
            if val <= 0:
                raise ValueError
        except ValueError:
            return await update.message.reply_text(f"{E_CROSS} Số lượng không hợp lệ.", parse_mode="HTML")

        unit_raw = parts[1].lower()
        if unit_raw in ("m", "min", "mins", "minute", "minutes", "phut", "phút", "p"):
            unit = "m"
            duration_label = f"{val} phút"
        elif unit_raw in ("h", "hour", "hours", "gio", "giờ", "g"):
            unit = "h"
            duration_label = f"{val} giờ"
        elif unit_raw in ("d", "day", "days", "ngay", "ngày", "n"):
            unit = "d"
            duration_label = f"{val} ngày"
        else:
            return await update.message.reply_text(
                f"{E_CROSS} Đơn vị không hợp lệ — dùng <code>m</code>, <code>h</code> hoặc <code>d</code>.",
                parse_mode="HTML",
            )

        max_devices = 1
        if len(parts) >= 3:
            try:
                max_devices = int(parts[2])
                if max_devices <= 0:
                    raise ValueError
            except ValueError:
                return await update.message.reply_text(f"{E_CROSS} Số thiết bị không hợp lệ.", parse_mode="HTML")

        key = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
        rec = {
            "used": False, "created_at": get_hanoi_time().isoformat(), "used_by": None,
            "max_devices": max_devices, "devices": [], "minutes": 0, "hours": 0, "days": 0,
        }
        if unit == "m":
            rec["minutes"] = val
        elif unit == "h":
            rec["hours"] = val
        else:
            rec["days"] = val
        data.setdefault("keys", {})[key] = rec
        save_datakey(data)
        context.user_data["waiting_create_key"] = False
        return await update.message.reply_text(
            f"{E_PARTY} <b>TẠO KEY THÀNH CÔNG</b> {E_CROWN}\n"
            f"{E_PIN} Key: <code>{key}</code>\n"
            f"{E_CAL} Thời hạn: <code>{duration_label}</code>\n"
            f"{E_MON} Thiết bị tối đa: <code>{max_devices}</code>",
            parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
        )

    if context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        users = data.get("users", {})
        sent_count, failed = 0, 0
        status = await update.message.reply_text(f"{E_SPIN} Đang gửi broadcast...", parse_mode="HTML")
        for target in users.keys():
            try:
                await context.bot.send_message(
                    int(target), f"{E_MEGA} <b>THÔNG BÁO TỪ ADMIN</b> {E_FIRE}\n\n{msg}", parse_mode="HTML",
                )
                sent_count += 1
                if sent_count % 10 == 0:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id, message_id=status.message_id,
                        text=f"{E_SPIN} Đang gửi... ({sent_count}/{len(users)})", parse_mode="HTML",
                    )
                await asyncio.sleep(0.08)
            except Exception:
                failed += 1
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, message_id=status.message_id,
            text=(
                f"{E_PARTY} <b>Broadcast hoàn tất</b> {E_CHECK}\n"
                f"{E_CHECK} Thành công: <code>{sent_count}</code>\n"
                f"{E_CROSS} Thất bại: <code>{failed}</code>"
            ),
            parse_mode="HTML", reply_markup=get_admin_inline_keyboard(),
        )
        return


# --- CALLBACK ROUTER ---
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data_tag = q.data
    user = q.from_user
    uid = str(user.id)
    data = load_datakey()
    ensure_user(data, user)
    u = data["users"][uid]

    if data_tag == "check_3box_ok":
        ok, missing_box, reason, checked_count = await check_3box_membership(context.bot, user.id)
        if not ok:
            detail = reason or f"Chưa vào box: {missing_box}"
            await q.answer(detail[:200], show_alert=True)
            return await send_3box_gate(q, edit=True, reason=reason)
        u["verified_3box"] = True
        save_datakey(data)
        await q.answer(f"Xác nhận thành công ({checked_count}/3 box)!", show_alert=False)
        return await safe_edit_or_send(
            q, build_main_header(user, u, data), reply_markup=get_main_inline_keyboard(user.id, data),
        )

    await q.answer()
    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=True)
    if blocked:
        return

    if data_tag.startswith("stop_auto:"):
        target_api = data_tag.split(":", 1)[1]
        stop_auto_session(user.id, target_api)
        g_name = GAME_MAP_NAME.get(target_api, target_api.upper())
        w50, l50, t50 = get_50_window_stats(target_api, data)
        return await safe_edit_or_send(
            q,
            f"{E_CROSS} <b>ĐÃ TẮT AUTO BÀN {g_name}</b> {E_GAME}\n"
            f"{E_MON} Thống kê ({t50}/50 phiên): {E_WIN} <b>{w50} THẮNG</b> | {E_LOSE} <b>{l50} THUA</b>",
            reply_markup=get_main_inline_keyboard(user.id, data),
        )

    if data_tag.startswith("fk_"):
        parts = data_tag.split(":")
        if len(parts) == 2:
            action, req_id = parts
            if action == "fk_ok":
                return await handle_admin_freekey_callback(update, context, "ok", req_id)
            if action == "fk_no":
                return await handle_admin_freekey_callback(update, context, "no", req_id)
        return

    if data_tag == "fb_send_photo_only":
        photo_ids = context.user_data.pop("feedback_photo_ids", [])
        context.user_data.pop("waiting_feedback", None)
        if not photo_ids:
            return await safe_edit_or_send(
                q, f"{E_CROSS} Không tìm thấy ảnh feedback.", reply_markup=get_main_inline_keyboard(user.id, data),
            )
        admin_caption = (
            f"{E_BELL} <b>FEEDBACK {len(photo_ids)} ẢNH TỪ KHÁCH</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PARTY} Tên: <b>{user.first_name}</b> (@{user.username or 'no_username'})\n"
            f"{E_PIN} ID: <code>{uid}</code>\n"
            f"{E_CLIP} Nội dung: <i>(Chỉ gửi {len(photo_ids)} ảnh)</i>"
        )
        await send_photos_to_admins(context.bot, data, photo_ids, admin_caption)
        return await safe_edit_or_send(
            q, f"{E_PARTY} <b>Đã gửi {len(photo_ids)} ảnh feedback tới Admin</b> {E_CHECK}",
            reply_markup=get_main_inline_keyboard(user.id, data),
        )

    for state_key in [
        "waiting_for_giftcode", "awaiting_key", "waiting_giftcode_input",
        "waiting_create_key", "waiting_broadcast", "waiting_feedback",
        "feedback_photo_ids", "waiting_freekey_photo", "waiting_sub_admin",
        "waiting_deposit_amount",
    ]:
        context.user_data.pop(state_key, None)

    if data_tag.startswith("dep_"):
        parts = data_tag.split(":")
        if len(parts) != 2:
            return
        action, req_id = parts
        if action == "dep_done":
            return await handle_deposit_callback(update, context, "done", req_id)
        if action == "dep_ok":
            return await handle_admin_deposit_callback(update, context, "ok", req_id)
        if action == "dep_no":
            return await handle_admin_deposit_callback(update, context, "no", req_id)
        return

    if data_tag == "user_checkgame":
        await safe_edit_or_send(q, f"{E_SPIN} <b>ĐANG QUÉT DỮ LIỆU 50 PHIÊN TOÀN BỘ GAME...</b> {E_FIRE}")
        report_text = await build_check_game_report()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Làm Mới Check Game", callback_data="user_checkgame", api_kwargs=btn_icon("fire"))],
            [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
        ])
        return await safe_edit_or_send(q, report_text, reply_markup=kb)

    if data_tag == "menu_freekey":
        allowed, next_dt = can_claim_free_key(uid, data)
        if not allowed:
            return await safe_edit_or_send(
                q,
                f"{E_CROSS} <b>ĐÃ NHẬN KEY FREE 30P HÔM NAY</b> {E_ALERT}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_BELL} Lượt kế: <code>{next_dt.strftime('%d/%m/%Y %H:%M')}</code>",
                reply_markup=get_back_keyboard(),
            )
        context.user_data["waiting_freekey_photo"] = True
        return await safe_edit_or_send(
            q,
            f"{E_GIFT} <b>GET KEY FREE 30 PHÚT</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_FIRE} 1. Rải nội dung có <code>{FREE_KEY_BOT}</code> vào tối thiểu <b>3 box</b>.\n"
            f"{E_CLIP} 2. Gửi ảnh chứng minh ngay tại đây.\n"
            f"{E_CHECK} 3. Admin duyệt xong bot gửi thẳng <b>Key 30p</b> cho bạn.\n"
            f"{E_PIN} Mẫu: <code>Tool soi cầu real-time miễn phí tại {FREE_KEY_BOT}</code>",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "menu_back":
        stop_auto_session(user.id)
        return await safe_edit_or_send(
            q, build_main_header(user, u, data), reply_markup=get_main_inline_keyboard(user.id, data),
        )

    if data_tag == "menu_games":
        stop_auto_session(user.id)
        return await safe_edit_or_send(
            q,
            f"{E_GAME} <b>CHỌN GAME ĐỂ SOI CẦU</b> {E_FIRE}\n"
            f"{E_BELL} <i>Chọn cổng game có API real-time bên dưới.</i>",
            reply_markup=get_game_inline_keyboard(),
        )

    if data_tag.startswith("game_"):
        game = data_tag.split("_")[1]
        game_icons = {
            "SUNWIN": E_SUNWIN, "HITCLUB": E_HITCLUB, "B52": E_B52, "BETVIP": E_BETVIP,
            "LC79": E_LC79, "XD88": E_XD88, "GAME68": E_GAME68, "MAX789": E_MAX789,
        }
        g_icon = game_icons.get(game, E_GAME)
        return await safe_edit_or_send(
            q,
            f"{g_icon} <b>CHỌN BÀN CHƠI {game}</b> {E_TABLE_TX}\n"
            f"{E_GAME} <i>Chọn bàn để tự động chạy soi cầu từng phiên.</i>",
            reply_markup=get_sub_inline_keyboard(game),
        )

    if data_tag == "menu_profile":
        exp_line = f"{E_SPIN} <b>KEY VIP:</b> Chưa kích hoạt"
        if is_key_active(u, user.id, data):
            if is_admin(user.id, data) and not u.get("key_expires"):
                role_label = "CHỦ BOT / ADMIN CHÍNH" if int(user.id) == int(ADMIN_ID) else "ADMIN PHỤ"
                exp_line = f"{E_CROWN} <b>KEY VIP:</b> {role_label} VĨNH VIỄN"
            else:
                exp = parse_hanoi_time(u["key_expires"])
                exp_line = f"{E_CROWN} <b>KEY VIP:</b> Tới <code>{exp.strftime('%d/%m/%Y %H:%M')}</code>"
        elif u.get("key_expires"):
            exp_line = f"{E_CROSS} <b>KEY VIP:</b> Đã hết hạn"

        jd = parse_hanoi_time(u.get("join_date"))
        join_str = jd.strftime("%d/%m/%Y") if jd else "—"
        msg = (
            f"{E_CROWN} <b>HỒ SƠ CÁ NHÂN</b> {E_FIRE}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PARTY} <b>Tên:</b> <b>{user.first_name or 'Vô Danh'}</b>\n"
            f"{E_PIN} <b>ID:</b> <code>{uid}</code>\n"
            f"{E_CLIP} <b>Nick:</b> @{user.username if user.username else 'Không có'}\n"
            f"{E_CAL} <b>Tham gia:</b> <code>{join_str}</code>\n"
            f"{E_MONEY} <b>Số dư ví:</b> <code>{u.get('balance', 0):,}đ</code> {E_CASH}\n"
            f"{exp_line}"
        )
        return await safe_edit_or_send(q, msg, reply_markup=get_back_keyboard())

    if data_tag == "menu_buykey":
        kb = [
            [InlineKeyboardButton("Gói 1 Ngày — 30,000đ", callback_data="buy_1d", api_kwargs=btn_icon("money"))],
            [InlineKeyboardButton("Gói 3 Ngày — 70,000đ", callback_data="buy_3d", api_kwargs=btn_icon("fire"))],
            [InlineKeyboardButton("Gói 7 Ngày — 90,000đ", callback_data="buy_7d", api_kwargs=btn_icon("bag"))],
            [InlineKeyboardButton("Gói 1 Tháng — 130,000đ", callback_data="buy_30d", api_kwargs=btn_icon("crown"))],
            [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
        ]
        return await safe_edit_or_send(
            q,
            f"{E_BAG} <b>BẢNG GIÁ GÓI KEY VIP</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_MONEY} Số dư ví: <code>{u.get('balance', 0):,}đ</code> {E_CASH}\n"
            f"{E_CAL} <b>1 Ngày:</b> <code>30,000đ</code>\n"
            f"{E_FIRE} <b>3 Ngày:</b> <code>70,000đ</code>\n"
            f"{E_BAG} <b>7 Ngày:</b> <code>90,000đ</code>\n"
            f"{E_CROWN} <b>1 Tháng:</b> <code>130,000đ</code>",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    if data_tag.startswith("buy_"):
        p = KEY_PACKAGES.get(data_tag)
        if not p:
            return
        async with DATA_LOCK:
            data_fresh = load_datakey()
            u_fresh = data_fresh["users"][uid]
            balance = u_fresh.get("balance", 0)
            if balance < p["price"]:
                return await q.answer(f"Số dư không đủ! Cần {p['price']:,}đ (Hiện có {balance:,}đ)", show_alert=True)
            u_fresh["balance"] = balance - p["price"]
            key = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
            now = get_hanoi_time()
            data_fresh.setdefault("keys", {})[key] = {
                "days": p["days"], "hours": 0, "minutes": 0,
                "used": False, "created_at": now.isoformat(), "used_by": None,
                "bought_by": uid, "max_devices": 1, "devices": [],
            }
            data_fresh.setdefault("history", []).append({
                "user_id": uid, "package": p["name"], "price": p["price"],
                "key": key, "time": now.isoformat(),
            })
            save_datakey(data_fresh)

        acc_name = f"@{user.username}" if user.username else (user.first_name or uid)
        masked_key = _mask_key_for_bill(key)
        masked_uid = _mask_uid_for_bill(uid)
        await notify_checkbill_bot(
            f"{E_CART} <b>MUA KEY VIP THÀNH CÔNG</b> {E_BOLT}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_MAIL} Tài khoản: <code>{acc_name}</code> (<code>{masked_uid}</code>)\n"
            f"{E_BANK} Gói & giá: <b>{p['name']}</b> — <code>{p['price']:,}đ</code>\n"
            f"{E_BELL} Mã key: <tg-spoiler>{masked_key}</tg-spoiler>\n"
            f"{E_CLOVER} Thời gian: <code>{now.strftime('%d/%m/%Y %H:%M:%S')}</code>\n"
            f"{E_BOLT} Trạng thái: <b>Đã thanh toán</b>",
            button_text="Mở Bot", icon_key="cart",
        )

        kb = [
            [InlineKeyboardButton("Kích Hoạt Key Ngay", callback_data="menu_activate", api_kwargs=btn_icon("crown"))],
            [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
        ]
        return await safe_edit_or_send(
            q,
            f"{E_PARTY} <b>MUA KEY VIP THÀNH CÔNG</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_BAG} Gói: <b>{p['name']}</b> — <code>{p['price']:,}đ</code>\n"
            f"{E_PIN} Mã KEY: <code>{key}</code>\n"
            f"{E_MONEY} Số dư còn lại: <code>{u_fresh['balance']:,}đ</code> {E_CASH}\n"
            f"{E_FIRE} Chúc bạn chơi tốt và thắng lớn, vui vẻ cùng tool.",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    if data_tag == "menu_activate":
        context.user_data["awaiting_key"] = True
        return await safe_edit_or_send(
            q,
            f"{E_CROWN} <b>KÍCH HOẠT KEY VIP</b> {E_FIRE}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_GIFT} Nhập hoặc dán <b>MÃ KEY (15 ký tự)</b> vào khung chat:",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "menu_deposit":
        context.user_data["waiting_deposit_amount"] = True
        return await safe_edit_or_send(
            q,
            f"{E_MONEY} <b>NẠP TIỀN VÍ QUA VIETQR</b> {E_CASH}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PIN} Nhập <b>số tiền</b> bạn muốn nạp (VD: <code>30000</code>):\n"
            f"{E_CHECK} Bot sẽ tạo mã QR đúng STK, số tiền & nội dung cho bạn quét.",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "menu_giftcode":
        context.user_data["waiting_giftcode_input"] = True
        return await safe_edit_or_send(
            q,
            f"{E_GIFT} <b>NHẬP GIFTCODE NHẬN TIỀN</b> {E_PARTY}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PIN} Dán mã giftcode vào khung chat bên dưới:",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "menu_history":
        history = data.get("history", [])
        my_history = [h for h in history if str(h.get("user_id")) == uid]
        if not my_history:
            return await safe_edit_or_send(
                q,
                f"{E_CAL} <b>LỊCH SỬ MUA KEY</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_SPIN} Bạn chưa mua gói key nào.",
                reply_markup=get_back_keyboard(),
            )
        lines = [f"{E_CAL} <b>LỊCH SỬ MUA KEY (10 gần nhất)</b>", "━━━━━━━━━━━━━━━━━━━━"]
        for h in reversed(my_history[-10:]):
            t = parse_hanoi_time(h.get("time"))
            t_str = t.strftime("%d/%m/%Y %H:%M") if t else "—"
            lines.append(
                f"{E_CHECK} <b>{h.get('package', '?')}</b> — <code>{h.get('price', 0):,}đ</code>\n"
                f"   {E_PIN} <code>{h.get('key', '?')}</code> | {t_str}"
            )
        return await safe_edit_or_send(q, "\n".join(lines), reply_markup=get_back_keyboard())

    if data_tag == "menu_support":
        return await safe_edit_or_send(
            q,
            f"{E_NET} <b>HỖ TRỢ KHÁCH HÀNG</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_BELL} Kênh thông báo: {CHANNEL_THONG_BAO}\n"
            f"{E_MEGA} Nhóm chat: {CHANNEL_CHAT}\n"
            f"{E_CASH} Kênh check bill: {CHANNEL_BILL}\n"
            f"{E_CROWN} Admin hỗ trợ: {ADMIN_HANDLE}",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "menu_feedback":
        context.user_data["waiting_feedback"] = True
        context.user_data["feedback_photo_ids"] = []
        return await safe_edit_or_send(
            q,
            f"{E_BELL} <b>GỬI FEEDBACK CHO ADMIN</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_CLIP} Gửi ảnh và/hoặc nhập nội dung mô tả vấn đề.\n"
            f"{E_CHECK} Xong bấm nút gửi để chuyển tới Admin.",
            reply_markup=get_back_keyboard(),
        )

    if data_tag == "admin_tools":
        if not is_admin(user.id, data):
            return
        return await safe_edit_or_send(
            q,
            f"{E_GEAR} <b>ADMIN TOOLS QUẢN TRỊ</b> {E_CROWN}\n"
            f"{E_BELL} <i>Chọn chức năng bên dưới.</i>",
            reply_markup=get_admin_inline_keyboard(),
        )

    if data_tag == "admin_checkgame":
        if not is_admin(user.id, data):
            return
        await safe_edit_or_send(q, f"{E_SPIN} <b>ĐANG QUÉT DỮ LIỆU 50 PHIÊN TOÀN BỘ GAME...</b> {E_FIRE}")
        report_text = await build_check_game_report()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Làm Mới Check Game", callback_data="admin_checkgame", api_kwargs=btn_icon("fire"))],
            [InlineKeyboardButton("Quay Lại Admin", callback_data="admin_tools", api_kwargs=btn_icon("down"))],
        ])
        return await safe_edit_or_send(q, report_text, reply_markup=kb)

    if data_tag == "admin_giftcode":
        if not is_admin(user.id, data):
            return
        context.user_data["waiting_for_giftcode"] = True
        return await safe_edit_or_send(
            q,
            f"{E_GIFT} <b>TẠO GIFTCODE</b> {E_CROWN}\n"
            f"{E_PIN} Nhập số tiền giftcode vào khung chat:",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_createkey":
        if not is_admin(user.id, data):
            return
        context.user_data["waiting_create_key"] = True
        return await safe_edit_or_send(
            q,
            f"{E_CROWN} <b>TẠO KEY VIP</b> {E_FIRE}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PIN} Nhập theo cú pháp: <code>&lt;số&gt; &lt;m|h|d&gt; [số_thiết_bị]</code>\n"
            f"{E_CAL} VD: <code>30 m</code> (30 phút, 1 thiết bị)\n"
            f"        <code>1 h 3</code> (1 giờ, 3 thiết bị)\n"
            f"        <code>3 d 2</code> (3 ngày, 2 thiết bị)",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_stats":
        if not is_admin(user.id, data):
            return
        return await safe_edit_or_send(
            q, build_stats_text(data), reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_broadcast":
        if not is_admin(user.id, data):
            return
        context.user_data["waiting_broadcast"] = True
        return await safe_edit_or_send(
            q,
            f"{E_MEGA} <b>BROADCAST TOÀN BỘ USER</b> {E_FIRE}\n"
            f"{E_PIN} Nhập nội dung tin nhắn vào khung chat:",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_manage_sub":
        if not is_admin(user.id, data):
            return
        context.user_data["waiting_sub_admin"] = True
        return await safe_edit_or_send(
            q,
            f"{E_GEAR} <b>THÊM / XÓA ADMIN PHỤ</b> {E_CROWN}\n"
            f"{E_PIN} Nhập ID Telegram cần thêm hoặc xóa:",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_users":
        if not is_admin(user.id, data):
            return
        users = data.get("users", {})
        lines = [f"{E_CLIP} <b>DANH SÁCH USER ({len(users)})</b>", "━━━━━━━━━━━━━━━━━━━━"]
        for i, (k, v) in enumerate(list(users.items())[-30:], 1):
            if v.get("is_owner"):
                continue
            active = "✅" if is_key_active(v, None, data) else "❌"
            lines.append(f"{i}. {active} <code>{k}</code> — {v.get('first_name', 'N/A')}")
        return await safe_edit_or_send(
            q, "\n".join(lines), reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag == "admin_deposits":
        if not is_admin(user.id, data):
            return
        pending = [
            (k, r) for k, r in data.get("deposit_requests", {}).items()
            if r.get("status") in ("pending", "awaiting_admin")
        ]
        if not pending:
            return await safe_edit_or_send(
                q, f"{E_CHECK} <b>Không có đơn nạp chờ duyệt</b>",
                reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
            )
        lines = [f"{E_MONEY} <b>ĐƠN NẠP CHỜ DUYỆT ({len(pending)})</b>", "━━━━━━━━━━━━━━━━━━━━"]
        for k, r in pending[-20:]:
            lines.append(f"#{k} — <code>{r['user_id']}</code> ({r.get('status')})")
        return await safe_edit_or_send(
            q, "\n".join(lines), reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin"),
        )

    if data_tag.startswith("run_"):
        api_key = data_tag.split("run_", 1)[1]
        if api_key not in API_URLS:
            return
        if not is_key_active(u, user.id, data):
            return await safe_edit_or_send(
                q,
                f"{E_CROSS} <b>BẠN CHƯA CÓ KEY VIP HOẶC ĐÃ HẾT HẠN</b>\n"
                f"{E_BAG} Mua gói key để dùng tính năng soi cầu auto.",
                reply_markup=get_back_keyboard("menu_buykey", "Mua Key VIP"),
            )

        stop_auto_session(user.id, api_key)
        s_key = _session_key(user.id, api_key)
        w50, l50, t50 = get_50_window_stats(api_key, data)
        placeholder = await safe_edit_or_send(
            q,
            f"{E_SPIN} <b>ĐANG KHỞI TẠO AUTO...</b> {E_GAME}\n"
            f"{E_BELL} Bàn: <b>{GAME_MAP_NAME.get(api_key, api_key.upper())}</b>",
        )
        if not placeholder:
            return
        AUTO_SESSIONS[s_key] = {
            "task": None, "win": w50, "lose": l50, "total_50": t50,
            "active_session": None, "active_pred": None,
            "baseline_kq_for_active": None, "last_pred_sig": None, "last_status_text": None,
        }
        task = asyncio.create_task(
            _auto_loop_worker(context.bot, placeholder.chat_id, placeholder.message_id, user.id, api_key)
        )
        AUTO_SESSIONS[s_key]["task"] = task
        return


async def post_init(app):
    app.bot_data["bank_poller_task"] = asyncio.create_task(apibank_auto_verify_worker(app.bot))


async def post_shutdown(app):
    task = app.bot_data.get("bank_poller_task")
    if task and not task.done():
        task.cancel()


def main():
    init_datakey_file()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("key", handle_key_command))
    app.add_handler(CommandHandler("approve", handle_approve_command))
    app.add_handler(CommandHandler("broadcast", handle_broadcast_command))
    app.add_handler(CommandHandler("stats", handle_stats_command))

    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
