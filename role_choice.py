import discord
import logging
import uuid
import json
import role_manager

logger = logging.getLogger(__name__)
ROLES_FILENAME = "roles.json"

try:
    logger.debug(f"Reading {ROLES_FILENAME}")
    with open(ROLES_FILENAME, "r") as roles_json_f:
        roles_json_s = roles_json_f.read()
        roles_json = json.loads(roles_json_s)
except FileNotFoundError:
    logger.error(f"{ROLES_FILENAME} is missing")
    roles_json = [
        {
            "name": f"{ROLES_FILENAME} not found",
            "description": f"{ROLES_FILENAME} is missing, contact an administrator",
            "role_id": 0
        }
    ]
except json.JSONDecodeError:
    logger.error(f"Failed to decode {ROLES_FILENAME}")
    roles_json = [
        {
            "name": f"{ROLES_FILENAME} failed to decode",
            "description": f"{ROLES_FILENAME} is malformed, contact an administrator",
            "role_id": 0
        }
    ]
except:
    logger.exception(f"Unhandled exception while reading or decoding {ROLES_FILENAME}")

role_options = []
role_uuid_lookup = dict()
try:
    for role in roles_json:
        role_uuid = str(uuid.uuid4())
        role_uuid_lookup[role_uuid] = role.get("role_id", 0)
        role_options.append(
            discord.SelectOption(
                label=role.get("name", "MISSING_ROLE_NAME"),
                description=role.get("description"),
                value=role_uuid
            )
        )
except Exception as err:
    logger.exception("Unhandled exception when parsing roles JSON")
    role_options = [
        discord.SelectOption(
            label=f"Error parsing {ROLES_FILENAME}",
            description=f"{type(err).__name__}: {err}",
            value="None"
        )
    ]

class RoleChoiceView(discord.ui.LayoutView):
    def __init__(self, command_interaction: discord.Interaction):
        logger.debug("RoleChoiceView object created")
        super().__init__()
        container = discord.ui.Container(accent_color=discord.Color.blurple())
        self.selected_role: int | None = None

        container.add_item(
            discord.ui.TextDisplay(
                content="## Claim roles\n-# Select the role you affiliate with"
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                RoleDropdown(self)
            )
        )
        container.add_item(
            discord.ui.ActionRow(
                ClaimButton(self),
                UnclaimButton(self)
            )
        )

        self.add_item(container)

class RoleDropdown(discord.ui.Select):
    def __init__(self, parent_view: RoleChoiceView):
        logger.debug("RoleDropdown object created")
        self.parent_view = parent_view
        super().__init__(
            options=role_options,
            placeholder="Select a role"
        )
        
    async def callback(self, interaction: discord.Interaction):
        logger.debug("RoleDropdown callback called")
        role_uuid = self.values[0]
        selected_option = role_uuid_lookup.get(role_uuid)

        if selected_option is None:
            await interaction.response.send_message(
                "Role UUID lookup returned None; contact an administrator.",
                ephemeral=True
            )
            logger.error(f"Role UUID({role_uuid}) lookup failed; Role UUID dict: {role_uuid_lookup}")
            return
        
        self.parent_view.selected_role = selected_option
        await interaction.response.defer()

class ClaimButton(discord.ui.Button):
    def __init__(self, parent_view: RoleChoiceView):
        logger.debug("ClaimButton object created")
        self.parent_view = parent_view
        super().__init__(
            label="Claim",
            style=discord.ButtonStyle.success
        )

    async def callback(self, interaction: discord.Interaction):
        logger.debug(f"ClaimButton callback called; Target role ID {self.parent_view.selected_role}")
        await role_manager.give_role(
            interaction=interaction,
            role_id=self.parent_view.selected_role
        )

class UnclaimButton(discord.ui.Button):
    def __init__(self, parent_view: RoleChoiceView):
        logger.debug("UnclaimButton object created")
        self.parent_view = parent_view
        super().__init__(
            label="Unclaim",
            style=discord.ButtonStyle.danger
        )

    async def callback(self, interaction: discord.Interaction):
        logger.debug(f"UnclaimButton callback called; Target role ID {self.parent_view.selected_role}")
        await role_manager.take_role(
            interaction=interaction,
            role_id=self.parent_view.selected_role
        )