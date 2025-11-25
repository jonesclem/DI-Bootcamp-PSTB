###### WEEK - DAY 5 - MINI PROJECT - TIC TAC TOE

# Instructions

# The game is played on a grid that’s 3 squares by 3 squares.
# Players take turns putting their marks (O or X) in empty squares.
# The first player to get 3 of their marks in a row (up, down, across, or diagonally) is the winner.
# When all 9 squares are full, the game is over. If no player has 3 marks in a row, the game ends in a tie.

# Hint
# To do this project, you basically need to create four functions:
# display_board() – To display the Tic Tac Toe board (GUI).
# player_input(player) – To get the position from the player.
# check_win() – To check whether there is a winner or not.
# play() – The main function, which calls all the functions created above.
# Note: The 4 functions above are just an example. You can implement many more helper functions or choose
#  a completely different appoach if you want.

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # A list to hold the board state
        self.current_winner = None  # Keep track of the winner!

    def display_board(self):
        """Displaying the table."""
        rows = [self.board[i:i+3] for i in range(0, 9, 3)]
        print("\n")
        print("┌───┬───┬───┐")
        for r, row in enumerate(rows):
            print(f"│ {row[0]} │ {row[1]} │ {row[2]} │")
            if r < 2:
                print("├───┼───┼───┤")
        print("└───┴───┴───┘")

    def player_input(self, player):
        """
        Ask a position (1-9) to the player.
        
        Return the index (0-8), validate and place the move
        """
        while True:
            raw = input(f"Player {player}, choose a box (1-9) : ").strip()
            if not raw.isdigit():
                print("Invalid input. Input a number between 1 and 9.")
                continue
            pos = int(raw)
            if not (1 <= pos <= 9):
                print("Out of range. Please choose between 1 and 9.")
                continue
            idx = pos - 1
            if self.board[idx] != ' ':
                print("Box already taken. Please choose another one.")
                continue
            self.board[idx] = player
            return idx  # useful to exploit the index

    def check_win(self):
        """
        Check if there is a winner.
        Update self.current_winner and return True/False.
        """
        b = self.board
        lignes = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),        # lignes
            (0, 3, 6), (1, 4, 7), (2, 5, 8),        # colonnes
            (0, 4, 8), (2, 4, 6)                    # diagonales
        ]
        for a, c, d in lignes:
            if b[a] != ' ' and b[a] == b[c] == b[d]:
                self.current_winner = b[a]
                return True
        return False

    def play(self):
        """
        Main game loop.
        Alternate user X and 0, display, check win/draw.
        """
        print("Positions (references) :")
        print("┌───┬───┬───┐")
        print("│ 1 │ 2 │ 3 │")
        print("├───┼───┼───┤")
        print("│ 4 │ 5 │ 6 │")
        print("├───┼───┼───┤")
        print("│ 7 │ 8 │ 9 │")
        print("└───┴───┴───┘")

        player = 'X'
        for turn in range(9):  # max 9 moves
            self.display_board()
            self.player_input(player)
            if self.check_win():
                self.display_board()
                print(f"Victoire de {player} !")
                return
            player = 'O' if player == 'X' else 'X'

        self.display_board()
        print("Match nul.")


if __name__ == "__main__":
    game = TicTacToe()
    game.play()


