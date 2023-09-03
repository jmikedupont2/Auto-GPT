def initialize_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def display_board(board):
    for row in board:
        print('|'.join(row))
        print('-' * 5)

def is_valid_input(user_input, board):
    if user_input.isdigit() and 1 <= int(user_input) <= 9:
        row, col = divmod(int(user_input) - 1, 3)
        if board[row][col] == ' ':
            return True
    return False

def update_board(board, user_input, player):
    row, col = divmod(int(user_input) - 1, 3)
    board[row][col] = player

def check_win_draw(board):
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    for row in board:
        for cell in row:
            if cell == ' ':
                return None
    return 'Draw'

def main():
    board = initialize_board()
    player = 'X'
    while True:
        display_board(board)
        user_input = input(f'Player {player}, enter a position (1-9): ')
        if is_valid_input(user_input, board):
            update_board(board, user_input, player)
            result = check_win_draw(board)
            if result:
                display_board(board)
                if result == 'Draw':
                    print('Draw!')
                else:
                    print(f'Player {player} won!')
                break
            player = 'O' if player == 'X' else 'X'

if __name__ == '__main__':
    main()