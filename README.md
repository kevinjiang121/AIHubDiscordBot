# ABOUT
Discord bot that is used to host a bunch of calls to local/remote transformers. Production bot with functionality can be ask to join servers via this link https://discord.com/oauth2/authorize?client_id=1228454324720500746&permissions=274877941760&scope=bot

An .env file is required with the following
API Key to ChatGPT,
Assistant id,
Thread id,
Discord Token.

### INSTALLATION
install requirements.txt

### RUN
python discord-bot.py

### COMMANDS
!image = calls a stable diffusion model to generate image. Example: !image blue dog
!video = calls a stable diffusion model to generate videos. Image is sent through to a multimodal LLM to extrapolate a full video scenario. Example: !video red dog on a blue grass field