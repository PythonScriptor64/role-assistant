import discord
import logging

logger = logging.getLogger(__name__)

async def give_role(interaction: discord.Interaction, role_id: int | None):
    if role_id is None:
        await interaction.response.send_message(
            "Select a role first.",
            ephemeral=True
        )
        return False

    role = interaction.user.guild.get_role(role_id)
    if role is None:
        await interaction.response.send_message(
            "Role does not exist; contact an administrator.",
            ephemeral=True
        )
        return False
    
    if role in interaction.user.roles:
        await interaction.response.send_message(
            "You already have this role.",
            ephemeral=True
        )
        return False
    
    await interaction.user.add_roles(role, reason="Added self selected role")
    await interaction.response.send_message(
        f"Added role <@&{role_id}> to <@{interaction.user.id}>",
        allowed_mentions=discord.AllowedMentions.none(),
        ephemeral=True
    )
    return True

async def take_role(interaction: discord.Interaction, role_id: int | None):
    if role_id is None:
        await interaction.response.send_message(
            "Select a role first.",
            ephemeral=True
        )
        return False
    
    role = interaction.user.guild.get_role(role_id)
    if role is None:
        await interaction.response.send_message(
            "Role does not exist; contact an administrator.",
            ephemeral=True
        )
        return False
    
    if role not in interaction.user.roles:
        await interaction.response.send_message(
            "You don't have this role.",
            ephemeral=True
        )
        return False
    
    await interaction.user.remove_roles(role, reason="Removed self selected role")
    await interaction.response.send_message(
        f"Removed role <@&{role_id}> from <@{interaction.user.id}>",
        allowed_mentions=discord.AllowedMentions.none(),
        ephemeral=True
    )
    return True