import discord
from discord.ext import commands
from dotenv import load_dotenv

import io
import os
import calltolocalsdapi_discord
import calltochatgptapi_discord
import openai_realtime_api_discord  # Import the OpenAI Realtime API script
import comfyui_api_websocket_discord

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')  # Token stored in .env
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Call bot with !image (insert prompt)
@bot.command()
async def image(ctx, *, prompt: str):
    try:
        image_data = calltolocalsdapi_discord.generate_image(prompt)
        if image_data:
            # Send image to Discord
            with io.BytesIO(image_data) as image_file:
                await ctx.send("Here's the Image!:", file=discord.File(image_file, 'image.png'))
        else:
            await ctx.send("Failed to generate image.")
    except Exception as e:
        print(str(e))
        await ctx.send("Image Generator Offline")  # Typically means that the Stable Diffusion model is not running or API calls are not enabled

# Call bot with !chat (insert prompt)
@bot.command()
async def chat(ctx, *, prompt: str):
    try:
        gpt_response = calltochatgptapi_discord.call_chatgpt(prompt)
        if gpt_response:
            await ctx.send(gpt_response)
        else:
            await ctx.send("Failed to connect with GPT.")
    except Exception as e:
        print(str(e))
        await ctx.send("GPT Offline")  # Occurs when ChatGPT is down, or if token limit was reached

# Call bot with !realtimechat (insert prompt)
@bot.command()
async def realtimechat(ctx, *, prompt: str):
    try:
        # Modify the function to pass the user prompt to the realtime API script
        result = await openai_realtime_api_discord.connect_to_openai(prompt)

        # If the result is successful, send it back to Discord
        if result:
            await ctx.send(result)
        else:
            await ctx.send("Failed to connect to OpenAI Realtime API.")
    except Exception as e:
        print(str(e))
        await ctx.send("Realtime API Offline")

# Run the bot
bot.run(discord_token)
