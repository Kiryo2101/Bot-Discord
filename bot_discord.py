import discord
import os
from discord import app_commands
from discord.ext import commands
import lyricsgenius
from youtubesearchpython import VideosSearch
from datetime import datetime
from myserver import server_on

GENIUS_API_TOKEN = os.getenv("GENIUS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_API_TOKEN)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
intents.guilds = True
intents.members = True
channel_id = 978652027456462898

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.tree.sync()

@client.tree.command(name="lyrics", description="Get lyrics for a song")
@app_commands.describe(song_title="The title of the song", artist_name="The name of the artist")
async def lyrics(interaction: discord.Interaction, song_title: str, artist_name: str):
    await interaction.response.defer()
    
    try:
        song = genius.search_song(song_title, artist_name)
        
        search_query = f"{song_title} {artist_name}"
        videos_search = VideosSearch(search_query, limit=1)
        result = videos_search.result()
        
        if song and result and result['result']:
            video_info = result['result'][0]
            lyrics_text = song.lyrics[:2000]
            
            channel = await client.fetch_channel(channel_id)
            
            embed = discord.Embed(
                title=f"Lyrics for {video_info['title']}",
                description=f"```{lyrics_text}```",
                color=0xfa0000
            )
            embed.set_author(
                name=video_info['title'],
                url=f"https://www.youtube.com/watch?v={video_info['id']}",
                icon_url=video_info['thumbnails'][0]['url'] if video_info['thumbnails'] else None
            )
                
            
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name}",
                icon_url=interaction.user.avatar.url if interaction.user.avatar else discord.Embed.Empty
            )
            embed.timestamp = datetime.now()
            
            
            await channel.send(f"Requested by <@{interaction.user.id}> searching for {video_info['title']}\nhttps://www.youtube.com/watch?v={video_info['id']}")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send('Lyrics not found.')
    except Exception as e:
        await interaction.followup.send(f'An error occurred: {str(e)}')
@client.tree.command(name="verify", description="Get role")
async def verify(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name="Verify User")
        channel = await client.fetch_channel(channel_id)

        if role:
            await interaction.user.add_roles(role)
            print(f"Assigned role to {interaction.user.display_name}")

            embed = discord.Embed(
                title="Verification",
                description="Successfully assigned the role.",
                color=0x00ff00
            )
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name}",
                icon_url=interaction.user.avatar.url if interaction.user.avatar else discord.Embed.Empty
            )
            embed.timestamp = datetime.now()
            
            await channel.send(f"Verify requested by <@{interaction.user.id}> verify")
            await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f'An error occurred: {str(e)}')
server_on()
client.run(os.getenv("TOKEN"))