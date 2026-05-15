import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio

# --- التوكن الخاص بك ---
TOKEN = 'MTUwNDY5MDEwMjkyMjkwNzczOA.Gciy8C.1ZjQnJ-OLipqi5Ta5Gf9U6Gw7YCxUEuufzjQs0'

class MyBot(commands.Bot):
    def __init__(self):
        # تفعيل كل الصلاحيات لضمان عمل كل الأنظمة
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # تسجيل الأزرار لتعمل بشكل دائم
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        # مزامنة أوامر السلاش (Slash Commands)
        await self.tree.sync()
        print(f"✅ تم تشغيل البوت بنجاح: {self.user.name}")

bot = MyBot()

# --- نظام التذاكر المتطور ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة | Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_v1")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
        }
        
        channel = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ تم إنشاء تذكرتك: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(
            title="🎫 تذكرة جديدة",
            description=f"مرحباً {user.mention}، يرجى كتابة مشكلتك هنا وسيقوم فريق الدعم بالرد عليك.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=CloseTicketView())

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق | Close", style=discord.ButtonStyle.red, custom_id="close_ticket_v1")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ سيتم حذف هذه التذكرة خلال 5 ثوانٍ...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- أمر إعداد لوحة التذاكر ---
@bot.tree.command(name="setup", description="إرسال لوحة نظام التذاكر")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="مركز الدعم الفني",
        description="إذا كنت بحاجة إلى مساعدة، اضغط على الزر أدناه لفتح تذكرة.",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ تم إرسال لوحة التذاكر بنجاح.", ephemeral=True)

# --- نظام الحماية والترحيب ---
@bot.event
async def on_member_join(member):
    print(f"{member.name} انضم للسيرفر.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # حماية من الروابط لغير الإداريين
    if "http" in message.content and not message.author.guild_permissions.administrator:
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}، يمنع إرسال الروابط هنا.", delete_after=3)
    
    await bot.process_commands(message)

bot.run(TOKEN)
