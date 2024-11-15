import discord
from discord.ext import commands
from connect4 import Connect4
from dotenv import load_dotenv
import os

load_dotenv()

# Get the bot token from the environment variables
DISCORD_TOKEN = "Keygoeshere"

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True  # Enable reading messages
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def start(ctx, player2: discord.Member):
    """Starts a game of Connect 4 with the first player being the command sender and the second player being passed as an argument"""
    
    player1 = ctx.author  # The command sender is Player 1
    players = (player1, player2)
    
    # Ensure there are two players
    if len(players) != 2:
        await ctx.send("Please specify 1 other player to start the game.")
        return

    game = Connect4(players=players)
    
    # Let Player 1 know the game has started and ping Player 2 for their turn
    await ctx.send(f"Game has started between {player1.mention} and {player2.mention}! {player1.mention} will go first!")
    
    # Run the game
    winner = await game.run(ctx)

    # Send the result of the game
    if winner:
        await ctx.send(f"{winner.mention} wins!")
    else:
        await ctx.send("The game was canceled or no moves were made.")

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f"We have logged in as {bot.user}")

# Run the bot with your token
bot.run("Discord_Token")
