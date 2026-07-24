import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from dotenv import load_dotenv
import os
import config
import role_choice

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s; %(filename)s; %(funcName)s(); %(levelname)s: %(message)s"    
)
logger = logging.getLogger(__name__)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        logger.debug("Bot initializing")
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        logger.debug("Running setup hook")
        if config.SYNC_COMMANDS_ON_STARTUP:
            logger.debug("Creating task to sync slash commands")
            asyncio.create_task(self.sync_commands())
        else:
            logger.debug("Sync commands on startup is disabled; will not sync slash commands.")

    async def on_ready(self):
        logger.info(f"Logged in as '{self.user}'")

    async def sync_commands(self):
        try:
            commands = await self.tree.sync()
            logger.info(f"Finished syncing slash commands; Synced {len(commands)} command(s)")
            return commands
        except Exception:
            logger.exception(f"Slash commands failed to sync;")
            return None
    
intents = discord.Intents.default()
client = Bot(intents=intents, command_prefix=[]) # NEVER USE @bot.command, THE COMMAND PREFIX SHOULD REMAIN UNUSED UNLESS FOR TESTING


@client.tree.error
async def on_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        logger.info(f"Check failed for command /{interaction.command.name} ran by {interaction.user.name}")
        return
    logger.exception("Unhandled app command error", exc_info=error)

def admin_only_command():
    async def predicate(interaction: discord.Interaction):
        if interaction.guild is None:
            logger.info(f"User {interaction.user.name} tried to run /{interaction.command.name} outside of a guild")
            return False
        if interaction.user.guild_permissions.administrator:
            logger.info(f"User {interaction.user.name} has permission to run /{interaction.command.name}")
            return True
        else:
            logger.info(f"User {interaction.user.name} lacks permission to run /{interaction.command.name}")
            await interaction.response.send_message(
                "This command may only be run by administrators.",
                ephemeral=True
            )
            return False
    return app_commands.check(predicate)

async def disable_interactions(interaction: discord.Interaction):
    return False

async def guild_check(interaction: discord.Interaction):
    if interaction.guild is None:
        logger.info(f"User {interaction.user.name} tried to run /{interaction.command.name} outside of a guild")
        await interaction.response.send_message("Commands may only be used in a guild.", ephemeral=True)
        return False
    elif interaction.guild_id != config.ALLOWED_GUILD:
        logger.info(f"User {interaction.user.name} tried to run /{interaction.command.name} outside of the allowed guild")
        await interaction.response.send_message("Commands may not be used outside of the allowed guild.", ephemeral=True)
        return False
    else:
        return True
client.tree.interaction_check = guild_check

@client.tree.command(description="Syncs commands from bot; development use only")
@admin_only_command()
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    sync_result = await client.sync_commands()
    if sync_result is None:
        await interaction.followup.send("Syncing commands failed!")
    else:
        await interaction.followup.send(f"Finished syncing slash commands; Synced {len(sync_result)} command(s)")

@client.tree.command(description="Claim a role")
async def selectroles(interaction: discord.Interaction):
    await interaction.response.send_message(
        view=role_choice.RoleChoiceView(interaction),
        ephemeral=True
    )


client.run(BOT_TOKEN)