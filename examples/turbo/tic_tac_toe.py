def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != 0:
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != 0:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
        return board[0][2]
    return 0


def main():
    board = [[0, 0, 0] for _ in range(3)]
    player = 1
    moves = 0

    while True:
        try:
            x, y = map(int, input(f'Player {player}, enter your move (x,y): ').split(','))
            if 0 <= x < 3 and 0 <= y < 3 and board[x][y] == 0:
                board[x][y] = player
                moves += 1
                winner = check_winner(board)
                if winner != 0:
                    print(f'Player {winner} won!')
                    break
                elif moves == 9:
                    print('Draw')
                    break
                else:
                    player = 3 - player
        except ValueError:
            pass


if __name__ == '__main__':
    main()