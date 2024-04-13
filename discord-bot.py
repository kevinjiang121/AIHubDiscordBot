import discord
from discord.ext import commands
from dotenv import load_dotenv
import io
import os

# Assume generate_image is imported from the module where it's defined
import calltolocalsdapi_discord

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)

@bot.command()
async def image(ctx, *, prompt: str):
    image_data = calltolocalsdapi_discord.generate_image(prompt);
    if image_data:
        # Send image to Discord
        with io.BytesIO(image_data) as image_file:
            await ctx.send("Here's the Image!:", file=discord.File(image_file, 'image.png'))
    else:
        await ctx.send("Failed to generate image.")

bot.run(discord_token)
