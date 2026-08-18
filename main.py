import os
import base64
import aiohttp
import asyncio

from rubka.asynco import Robot
from rubka.context import Message


# =========================
# تنظیمات VEXREN
# =========================

RUBIKA_TOKEN = os.getenv("RUBIKA_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not RUBIKA_TOKEN:
    raise RuntimeError("RUBIKA_TOKEN پیدا نشد!")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY پیدا نشد!")


bot = Robot(token=RUBIKA_TOKEN)


# =========================
# ساخت تصویر
# =========================

async def generate_image(prompt):

    url = "https://api.openai.com/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024"
    }

    timeout = aiohttp.ClientTimeout(total=180)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        async with session.post(
            url,
            headers=headers,
            json=data
        ) as response:

            result = await response.json()

            if response.status != 200:
                error = result.get("error", {})
                raise Exception(
                    error.get("message", "خطای نامشخص")
                )

            image_data = result["data"][0].get("b64_json")

            if not image_data:
                raise Exception("تصویر دریافت نشد!")

            return base64.b64decode(image_data)


# =========================
# شروع ربات
# =========================

@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):

    await message.reply(
        "🎨 سلام!\n\n"
        "من وِکسرِن (VEXREN) هستم 🤖\n"
        "ربات ساخت تصویر!\n\n"
        "🖼️ فقط توضیح تصویری که می‌خوای رو بفرست.\n\n"
        "مثال:\n"
        "یک گربه فضانورد روی ماه، "
        "سبک سینمایی و بسیار باکیفیت 🌙🐱"
    )


# =========================
# دریافت درخواست تصویر
# =========================

@bot.on_message()
async def create_image(bot: Robot, message: Message):

    prompt = (message.text or "").strip()

    if not prompt:
        return

    if prompt.startswith("/"):
        return

    await message.reply(
        "🎨 وِکسرِن داره تصویرت رو می‌سازه...\n"
        "⏳ یکم صبر کن!"
    )

    try:

        image_bytes = await generate_image(prompt)

        filename = f"/tmp/vexren_{message.message_id}.png"

        with open(filename, "wb") as file:
            file.write(image_bytes)

        await message.reply_image(
            path=filename,
            text="🎨 ساخته شد توسط VEXREN"
        )

        try:
            os.remove(filename)
        except Exception:
            pass

    except Exception as error:

        print("IMAGE ERROR:", error)

        await message.reply(
            "❌ متأسفانه ساخت تصویر انجام نشد.\n\n"
            "ممکنه سرویس تصویر یا API Key مشکل داشته باشه."
        )


# =========================
# اجرای ربات
# =========================

async def main():

    print("================================")
    print("🎨 VEXREN Image Bot")
    print("🤖 ربات آماده است!")
    print("================================")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
