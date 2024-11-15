from itertools import cycle
import numpy
import discord
from discord.ext import menus


class Connect4(menus.Menu):
    filler = "\N{BLACK LARGE SQUARE}"
    red = "\N{LARGE RED CIRCLE}"
    blue = "\N{LARGE BLUE CIRCLE}"
    numbers = [str(i) + "\N{VARIATION SELECTOR-16}\u20e3" for i in range(1, 8)]

    def __init__(self, players: tuple[discord.Member, ...], **kwargs):
        super().__init__(**kwargs)
        self.players = players
        self.player_cycle = cycle(self.players)
        self.current_player = next(self.player_cycle)
        self.last_move = None
        self.winner = None
        self.board = numpy.full((6, 7), self.filler)
        # Add number buttons and the down arrow button
        for button in (
            menus.Button(num, self.do_number_button) for num in self.numbers
        ):
            self.add_button(button)
        # Add the down arrow button back
        self.add_button(menus.Button("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}", self.do_resend))

    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False

        if payload.user_id != self.current_player.id:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(self.discord_message)

    async def do_number_button(self, payload):
        move_column = self.numbers.index(payload.emoji.name)
        move_row = self.free(move_column)

        # self.free returns None if the column was full
        if move_row is not None:
            self.make_move(move_row, move_column)

            # timeouts count as wins
            self.winner = self.current_player

            if self.check_wins():
                self.winner = self.current_player
                self.stop()

            # Tie
            if self.filler not in self.board:
                self.winner = self.players
                self.stop()

            self.current_player = next(self.player_cycle)
            await self.message.edit(
                content=self.discord_message, allowed_mentions=self.bot.allowed_mentions  # type: ignore
            )

    @menus.button("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}", position=menus.Last())
    async def do_resend(self, _):
        """Resend the current game message to refresh the game state."""
        await self.message.delete()
        self.message = msg = await self.send_initial_message(self.ctx, self.ctx.channel)  # type: ignore
        for emoji in self.buttons:
            await msg.add_reaction(emoji)

    @property
    def current_piece(self):
        """Determine the current player's piece (red or blue)."""
        if self.current_player == self.players[0]:
            return self.red  # Player 1 gets red
        else:
            return self.blue  # Player 2 gets blue

    @property
    def board_message(self):
        """Generate the board string for display."""
        msg = "\n".join(["".join(i) for i in self.board])
        msg += "\n"
        msg += "".join(self.numbers)
        return msg

    @property
    def discord_message(self):
        """Generate the full game message for Discord."""
        final = ""

        if self.last_move is not None:
            final += "Last move:\n"
            final += self.last_move
            final += "\n"

        if self._running:
            final += f"Current turn: {self.current_piece} {self.current_player.mention}\n"

        final += self.board_message
        return final

    def free(self, num: int):
        """Find the first available row in the given column."""
        for i in range(5, -1, -1):
            if self.board[i][num] == self.filler:
                return i

    def make_move(self, row: int, column: int):
        """Place the current player's piece on the board."""
        self.board[row][column] = self.current_piece
        self.last_move = f"{self.current_piece} {self.current_player.mention} ({column + 1})"

    def check_wins(self):
        """Check if the current player has won the game."""
        def check(array: list):
            array = list(array)
            for i in range(len(array) - 3):
                if array[i:i + 4].count(self.current_piece) == 4:
                    return True

        # Check rows, columns, and diagonals for a winning condition
        for row in self.board:
            if check(row):
                return True

        for column in self.board.T:
            if check(column):
                return True

        def get_diagonals(matrix: numpy.ndarray):
            dias = []
            for offset in range(-2, 4):
                dias.append(list(matrix.diagonal(offset)))
            return dias

        for diagonal in [
            *get_diagonals(self.board),
            *get_diagonals(numpy.fliplr(self.board)),
        ]:
            if check(diagonal):
                return True

    async def run(
        self, ctx
    ) -> discord.Member | tuple[discord.Member, ...] | None:
        """
        Run the game and return the winner(s)
        returns None if the first player never made a move
        """
        await self.start(ctx, wait=True)
        return self.winner
