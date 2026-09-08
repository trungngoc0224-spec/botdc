import discord
from discord import app_commands
from discord.ext import commands
import openai
import asyncio
import os

# --- CẤU HÌNH ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
APINEX_API_KEY = os.environ.get("APIINDEX_API_KEY")
APINEX_BASE_URL = "https://api.apinex.bond/v1"  # Base URL của APInex

# Cấu hình OpenAI client để dùng APInex
client = openai.AsyncOpenAI(
    api_key=APINEX_API_KEY,
    base_url=APINEX_BASE_URL,
)

# --- TẠO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SỰ KIỆN KHI BOT SẴN SÀNG ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng!")
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} lệnh slash.")
    except Exception as e:
        print(e)

# --- LỆNH SLASH: /ask ---
@bot.tree.command(name="ask", description="Hỏi GPT-5.6 Luna bất cứ điều gì")
@app_commands.describe(prompt="Câu hỏi của bạn")
async def ask(interaction: discord.Interaction, prompt: str):
    # Trả lời tạm để tránh timeout (Discord yêu cầu phản hồi trong 3 giây) [citation:15]
    await interaction.response.defer()

    try:
        # Gọi API của APInex với model GPT-5.6 Luna
        response = await client.chat.completions.create(
            model="free/gpt-5.6-luna",  # hoặc "gpt/5.6-luna"
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý AI hữu ích."},
                {"role": "user", "content": prompt}
            ],
            # Có thể thêm các tham số khác như temperature, max_tokens
            # temperature=0.7,
        )
        reply = response.choices[0].message.content
        await interaction.followup.send(reply)

    except Exception as e:
        await interaction.followup.send(f"Đã xảy ra lỗi: {str(e)}")

# --- TRẢ LỜI TIN NHẮN THÔNG THƯỜNG (KHÔNG BẮT BUỘC) ---
# Nếu muốn bot trả lời mọi tin nhắn, bỏ comment phần này

# --- CHẠY BOT ---
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
