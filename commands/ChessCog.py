import discord
from discord.ext import commands
import chess
import chess.svg
import cairosvg
import time

class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_game = None
        self.current_players = None
        self.board_images = []
        print("ChessCog loaded!")

    def board_to_image(self, board: chess.Board, white_player: str, black_player: str, move_number: int):
        """Generate an image of the current chess board as a PNG."""
        svg_data = chess.svg.board(board=board)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_path = f"/tmp/chess_board_{timestamp}_{white_player}_vs_{black_player}_move_{move_number}.png"
        cairosvg.svg2png(bytestring=svg_data, write_to=image_path)
        self.board_images.append(image_path)
        return image_path

    @commands.command(name="start_chess")
    async def start_chess(self, ctx, opponent: discord.Member):
        if self.current_game is not None:
            await ctx.send("A game is already in progress. Finish it first or wait.")
            return
        if opponent.bot:
            await ctx.send("You cannot play against a bot in two-player mode.")
            return
        self.current_game = chess.Board()
        self.current_players = (ctx.author, opponent)
        await ctx.send(
            f"New chess game started between {ctx.author.mention} (White) and {opponent.mention} (Black)! Use `!move e2e4` to move."
        )
        image_path = self.board_to_image(
            self.current_game,
            ctx.author.display_name,
            opponent.display_name,
            0
        )
        await ctx.send(file=discord.File(image_path))

    @commands.command(name="move")
    async def move(self, ctx, move: str):
        if self.current_game is None:
            await ctx.send("No game in progress. Use `!start_chess @user` to begin.")
            return
        if self.current_players is None or ctx.author.id not in (self.current_players[0].id, self.current_players[1].id):
            await ctx.send("You are not a player in the current chess game.")
            return
        current_turn_player = self.current_players[0] if self.current_game.turn else self.current_players[1]
        if ctx.author.id != current_turn_player.id:
            await ctx.send("It's not your turn.")
            return
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.current_game.legal_moves:
                self.current_game.push(chess_move)
                move_number = self.current_game.fullmove_number
                image_path = self.board_to_image(
                    self.current_game,
                    self.current_players[0].display_name,
                    self.current_players[1].display_name,
                    move_number
                )
                await ctx.send(f"Move made: {move}", file=discord.File(image_path))
                if self.current_game.is_game_over():
                    await ctx.send(f"Game over! Result: {self.current_game.result()}")
                    self.current_game = None
                    self.current_players = None
            else:
                await ctx.send("Illegal move. Try again.")
        except ValueError:
            await ctx.send("Invalid move format. Use standard UCI (e.g., e2e4).")

async def setup(bot):
    await bot.add_cog(ChessCog(bot))
