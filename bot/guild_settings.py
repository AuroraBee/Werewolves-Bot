# This class contains the global settings per guild

import discord


class GuildSettings:
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.category = None

        self.settings = {
            'rolelist': 'default',
            'roles': {
                'alive': None,
                'dead': None,
                'revealed mayor': None,
                'player': None,
                'spectator': None,
                'game master': None
            },
            'cycles': {
                'day': 60,
                'night': 40,
                'voting': 40,
                'judging': 15
            },
            'game': {
                'updateTimer': 1,
                'participants': []
            },
            'channels': {
                'day': None,
                'dead': None,
                'mafia': None,
                'vampire': None,
                'spectator': None
            },
            'playerChannels': {},
            # players dict, key: player id, value: normalized name
            'players': {},
        }

    async def setup(self):
        self.category = discord.utils.get(self.guild.categories, name='Mitesi')
        if not self.category:
            self.category = await self.guild.create_category('Mitesi')

        for role in ['alive', 'dead', 'revealed mayor', 'player', 'spectator', 'game master']:
            if not self.settings['roles'][role]:
                # Check if the role exists
                self.settings['roles'][role] = discord.utils.get(
                    self.guild.roles, name=role.title())
                if not self.settings['roles'][role]:
                    # Create the role if it doesn't exist
                    self.settings['roles'][role] = await self.guild.create_role(name=role.title())
                    print(
                        f'Created role {role.title()} for guild {self.guild.name}.')
                else:
                    print(
                        f'Found role {role.title()} for guild {self.guild.name}.')
            else:
                print(
                    f'Role {role.title()} already exists for guild {self.guild.name}.')
        print(f'Guild settings setup for guild {self.guild.name}.')
    
    def add_participant(self, player: discord.Member):
        # Normalize the name, removing special characters, keeping spaces
        name = player.display_name.replace('-', ' ').replace('_', ' ').replace('.', ' ')
        normalized_name = ''.join(e for e in name if e.isalnum() or e == ' ')
        normalized_name = normalized_name.strip()
        # Check if the player is already in self.settings['players']
        if player.id in self.settings['players']:
            # If the normalized name is different, update it
            if self.settings['players'][player.id] != normalized_name:
                self.settings['players'][player.id] = normalized_name
                print(
                    f'Updated player {player.display_name} ({player.id}) to {normalized_name} for game in guild {self.guild.name}.')
        else:
            # Add the player to the dict
            self.settings['players'][player.id] = normalized_name
            print(
                f'Added player {player.display_name} ({player.id}) to {normalized_name} for game in guild {self.guild.name}.')
    
    def remove_participant(self, player: discord.Member):
        # Check if the player is in self.settings['players']
        if player.id in self.settings['players']:
            # Remove the player from the dict
            self.settings['players'].pop(player.id)
            print(
                f'Removed player {player.display_name} ({player.id}) from game in guild {self.guild.name}.')
        else:
            print(
                f'Player {player.display_name} ({player.id}) not found in game in guild {self.guild.name}.')

    def get_participants(self):
        return self.settings['players']