# CARILLO, SANTOS R, PALACIOS
# BET-COET-2A
# CPET 5L PRELIM
# SUPERTICTACTOE NI REY


import sys
import pygame
import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QMovie, QPainterPath, QRegion
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout ,QWidget
from PyQt5.QtCore import QRectF, Qt, QPoint

# FUNCTION CLASS
pygame.init()
pygame.mixer.init()

CLICK_SOUND = pygame.mixer.Sound(r"click.mp3")
BG_MUSIC = r"bgmusic.mp3"

class UIUtils:
    @staticmethod
    def apply_rounded_corners(widget: QWidget, radius: int = 15):
        path = QPainterPath()
        rect = QRectF(0, 0, widget.width(), widget.height())
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        widget.setMask(region)

    @staticmethod
    def remove_window_header(window):
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.setAttribute(Qt.WA_TranslucentBackground)

    def setup_window_drag(window):
        window.oldPos = None

        def mousePressEvent(event):
            window.oldPos = event.globalPos()

        def mouseMoveEvent(event):
            if window.oldPos:
                delta = QPoint(event.globalPos() - window.oldPos)
                window.move(window.x() + delta.x(), window.y() + delta.y())
                window.oldPos = event.globalPos()

        window.mousePressEvent = mousePressEvent
        window.mouseMoveEvent = mouseMoveEvent

class BaseWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_file):
        super().__init__()
        uic.loadUi(ui_file, self)

    def switch_window(self, new_window_class, *args):
        CLICK_SOUND.play()
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__('.ui/main.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.set_background_music()
        self.howtoplay.clicked.connect(lambda: self.switch_window(HTPTurns))
        self.exit.clicked.connect(lambda: self.switch_window(ExitWindow))
        self.volume.clicked.connect(self.toggle_volume)
        self.startgame.clicked.connect(lambda: self.switch_window(GameModes))

    def set_background_music(self):
        pygame.mixer.music.load(BG_MUSIC)
        pygame.mixer.music.play(-1)

    def toggle_volume(self):
        CLICK_SOUND.play()
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0 if current_volume > 0 else 1)


class ExitWindow(BaseWindow):
    def __init__(self):
        super().__init__('.ui/exit.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.yes_btn.clicked.connect(self.exit_application)
        self.no_btn.clicked.connect(lambda: self.switch_window(MainWindow))

    def exit_application(self):
        pygame.quit()
        sys.exit()

class HTPTurns(BaseWindow):
    def __init__(self):
        super().__init__('.ui/htpturns.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.setup_video(r"C:\Users\maeve\Desktop\supertictactoe\reso\turnsvideo.gif")
        self.next.clicked.connect(lambda: self.switch_window(HTPWinning))
        self.back.clicked.connect(lambda: self.switch_window(MainWindow))

    def setup_video(self, path):
        self.movie = QMovie(path)
        self.vid_label = self.findChild(QtWidgets.QLabel, 'vid_label')
        self.vid_label.setMovie(self.movie)
        self.vid_label.setScaledContents(True)
        self.movie.start()

class HTPWinning(BaseWindow):
    def __init__(self):
        super().__init__('.ui/htpwinning.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.setup_video(r"C:\Users\maeve\Desktop\supertictactoe\reso\winningvideo.gif")
        self.next_2.clicked.connect(lambda: self.switch_window(HTPTurns))
        self.back.clicked.connect(lambda: self.switch_window(MainWindow))

    def setup_video(self, path):
        self.movie = QMovie(path)
        self.vid_label = self.findChild(QtWidgets.QLabel, 'vid_label')
        self.vid_label.setMovie(self.movie)
        self.vid_label.setScaledContents(True)
        self.movie.start()

class GameModes(BaseWindow):
    def __init__(self):
        super().__init__('.ui/gamemodes.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.vsplayer.clicked.connect(lambda: self.switch_window(EnterNameVsPlayer))
        self.vsai.clicked.connect(lambda : self.switch_window(EnterNameVsAI))
        self.back.clicked.connect(lambda: self.switch_window(MainWindow))

class EnterNameVsPlayer(BaseWindow):
    def __init__(self):
        super().__init__('.ui/enternamevsplayer.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.start.clicked.connect(self.start_player_vs_player)
        self.back.clicked.connect(lambda: self.switch_window(GameModes))
        self.xname = self.findChild(QtWidgets.QLineEdit, 'xname')
        self.oname = self.findChild(QtWidgets.QLineEdit, 'oname')

    def start_player_vs_player(self):
        CLICK_SOUND.play()
        x_name = self.xname.text()
        o_name = self.oname.text()
        self.switch_window(SuperTicTacToeGame, x_name, o_name)

class EnterNameVsAI(BaseWindow):
    def __init__(self):
        super().__init__('.ui/enternamevsai.ui')
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)
        self.start.clicked.connect(self.start_player_vs_ai)
        self.back.clicked.connect(lambda: self.switch_window(GameModes))
        self.namex = self.findChild(QtWidgets.QLineEdit, 'namex')

    def start_player_vs_ai(self):
        CLICK_SOUND.play()
        x_name = self.namex.text()
        self.switch_window(SuperTicTacToe_AI, x_name)











# LOGIC GAME CLASS

class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.winner = None

    def play_move(self, row, col, player):
        if self.board[row][col] == ' ' and not self.winner:
            self.board[row][col] = player
            if self.check_winner(player):
                self.winner = player
        else:
            return False
        return True

    def check_winner(self, player):
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
            if all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def is_full(self):
        return all(self.board[row][col] != ' ' for row in range(3) for col in range(3))


class SuperTicTacToeGame(QtWidgets.QMainWindow):
    def __init__(self, x_name, o_name):
        super(SuperTicTacToeGame, self).__init__()
        uic.loadUi('.ui/playervsplayer.ui', self)
        UIUtils.remove_window_header(self) 
        UIUtils.apply_rounded_corners(self)   
        UIUtils.setup_window_drag(self) 
        self.super_board = [[TicTacToe() for _ in range(3)] for _ in range(3)]
        self.main_winner = None
        self.current_game = None
        self.scorex = 0  
        self.scoreo = 0 
        self.player = 'X'
        self.buttons = [[[None for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.setup_ui()
        
        # Set player names
        self.x_name = x_name
        self.o_name = o_name
        
        # Find and set the name labels
        self.namex_label = self.findChild(QtWidgets.QLabel, 'namex')
        self.nameo_label = self.findChild(QtWidgets.QLabel, 'nameo')
        self.namex_label.setText(self.x_name)
        self.nameo_label.setText(self.o_name)

        self.volume_button = self.findChild(QtWidgets.QPushButton, 'volume')
        if self.volume_button:
            self.volume_button.clicked.connect(self.toggle_volume)

    def toggle_volume(self):
        CLICK_SOUND.play()
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0 if current_volume > 0 else 1)

    def setup_ui(self):
        self.nameturn = self.findChild(QtWidgets.QLabel, 'nameturn')
        self.update_turn_label()  
        game_layout = QtWidgets.QGridLayout(self.game_frame)
        game_layout.setSpacing(10)
        game_layout.setContentsMargins(5, 5, 5, 5)
        
        self.findChild(QtWidgets.QPushButton, 'settings').clicked.connect(self.launch_settings_ui)

        for game_row in range(3):
            for game_col in range(3):
                inner_grid = QtWidgets.QGridLayout()
                inner_grid.setSpacing(10)
                inner_grid.setContentsMargins(10, 10, 10, 10)
                for row in range(3):
                    for col in range(3):
                        btn = QtWidgets.QPushButton(' ')
                        btn.setFixedSize(46, 48)
                        btn.setStyleSheet(
                            "border: 2px solid #FFA500; " 
                            "font-size: 20px; "
                            "color: #000000; "
                            "background-color: #FFFFFF;"
                        )
                        btn.clicked.connect(lambda _, r=game_row, c=game_col, sr=row, sc=col: self.play_move(r, c, sr, sc))
                        inner_grid.addWidget(btn, row, col)
                        self.buttons[game_row * 3 + game_col][row][col] = btn
                game_layout.addLayout(inner_grid, game_row, game_col)

    def launch_settings_ui(self):
        CLICK_SOUND.play()
        self.settings_window = QtWidgets.QMainWindow()
        uic.loadUi('.ui/settings.ui', self.settings_window)
        UIUtils.remove_window_header(self.settings_window)
        UIUtils.apply_rounded_corners(self.settings_window)
        UIUtils.setup_window_drag(self.settings_window)
        self.settings_window.backmain.clicked.connect(self.back_to_main_menu)
        self.settings_window.restartgame.clicked.connect(self.restart_game)
        self.settings_window.continuegame.clicked.connect(self.continue_game)
        self.settings_window.show() 

    def back_to_main_menu(self):
        CLICK_SOUND.play()
        self.settings_window.close()
        self.close()  
        self.main_window = MainWindow()  
        self.main_window.show()

    def restart_game(self):
        CLICK_SOUND.play()
        if hasattr(self, 'settings_window') and self.settings_window:
            self.settings_window.close()
        
        self.scorex = 0
        self.scoreo = 0
        self.main_winner = None
        self.player = 'X'
        self.current_game = None
        self.super_board = [[TicTacToe() for _ in range(3)] for _ in range(3)]

        for i in range(9):
            for j in range(3):
                for k in range(3):
                    self.buttons[i][j][k].setText(' ')
                    self.buttons[i][j][k].setStyleSheet(
                        "border: 2px solid #FFA500; "
                        "font-size: 20px; "
                        "color: #000000; "
                        "background-color: #FFFFFF;"
                    )
        
        self.update_score_label('X')
        self.update_score_label('O')
        

    def continue_game(self):
        CLICK_SOUND.play()
        self.settings_window.close() 

    def play_move(self, game_row, game_col, row, col):
        if self.main_winner:
            QMessageBox.information(self, "Game Over", f"{self.main_winner} has already won the game!")
            return
        if self.current_game and self.current_game != (game_row, game_col):
            QMessageBox.critical(self, "Invalid Move", f"You must play in the game at {self.current_game}.")
            return
        if not self.super_board[game_row][game_col].play_move(row, col, self.player):
            QMessageBox.critical(self, "Invalid Move", "This move is not allowed. Try again!")
            return
        
        CLICK_SOUND.play()

        button = self.buttons[game_row * 3 + game_col][row][col]
        button.setText(self.player)

        if self.player == 'X':
            button.setStyleSheet(
                            "border: 2px solid #FFA500; "  
                            "font-family: 'Comic Sans MS';"
                            "font-size: 12pt;"
                            "color: #b7e3fe;"
                            "background-color: #FFFFFF;"  
                        )  
        else:
            button.setStyleSheet(
                            "border: 2px solid #FFA500; "
                            "font-family: 'Comic Sans MS';"
                            "font-size: 12pt;"
                            "color: #fd8755;; "
                            "background-color: #FFFFFF;" 
                        ) 

        if self.super_board[game_row][game_col].winner:
            self.highlight_winner(game_row, game_col)
            
            if self.player == 'X':
                self.scorex += 1  
                self.update_score_label('X')  
            else:
                self.scoreo += 1 
                self.update_score_label('O')  

        if self.check_main_winner(self.player):
            self.main_winner = self.player
            self.launch_winner_ui(self.player) 
            return

        if self.is_draw():
            self.launch_draw_ui() 
            return

        self.current_game = (row, col)
        if self.super_board[row][col].is_full() or self.super_board[row][col].winner:
            self.current_game = None
        self.player = 'O' if self.player == 'X' else 'X'
        self.update_turn_label()  

    def update_score_label(self, player):
        if player == 'X':
            scorex_lbl = self.findChild(QtWidgets.QLabel, 'scorex')  
            scorex_lbl.setText(f"{self.scorex}")
        elif player == 'O':
            scoreo_lbl = self.findChild(QtWidgets.QLabel, 'scoreo') 
            scoreo_lbl.setText(f"{self.scoreo}")

    def launch_winner_ui(self, winner):
        self.winner_window = QtWidgets.QMainWindow()
        uic.loadUi('.ui/playerwins.ui', self.winner_window)
        player_label = self.winner_window.findChild(QtWidgets.QLabel, 'playername')
        if winner == 'X':
            player_label.setText("PLAYER X")
            player_label.setStyleSheet("color: #b7e3fe;")
        else:
            player_label.setText("PLAYER O")
            player_label.setStyleSheet("color: #fd8755;")

        rematch_button = self.winner_window.findChild(QtWidgets.QPushButton, 'rematch')
        back_button = self.winner_window.findChild(QtWidgets.QPushButton, 'back')
        rematch_button.clicked.connect(self.rematch_game)
        back_button.clicked.connect(self.back_to_main)

        self.winner_window.show()

    def launch_draw_ui(self):
        draw_window = QtWidgets.QMainWindow()
        uic.loadUi('.ui/playerdraw.ui', draw_window)
        wins_label = draw_window.findChild(QtWidgets.QLabel, 'wins_lbl')  # Find QLabel by the name 'wins_lbl'

        if self.scorex > self.scoreo:
            wins_label.setText(f"DRAW BUT X WINS THE MOST! ({self.scorex} to {self.scoreo})")
        elif self.scoreo > self.scorex:
            wins_label.setText(f"DRAW BUT O WINS THE MOST! ({self.scoreo} to {self.scorex})")
        else:
            wins_label.setText("DRAW! BOTH PLAYERS ARE EQUAL!")
        draw_window.show()

    def rematch_game(self):
        CLICK_SOUND.play()
        self.winner_window.close() if hasattr(self, 'winner_window') else None
        self.draw_window.close() if hasattr(self, 'draw_window') else None
        self.restart_game()

    def back_to_main(self):
        CLICK_SOUND.play()
        self.winner_window.close() if hasattr(self, 'winner_window') else None
        self.draw_window.close() if hasattr(self, 'draw_window') else None
        self.close()

    def is_draw(self):
        return all(board.is_full() for row in self.super_board for board in row) and not self.main_winner

    def check_main_winner(self, player):
        for i in range(3):
            if all(self.super_board[i][j].winner == player for j in range(3)):
                return True
            if all(self.super_board[j][i].winner == player for j in range(3)):
                return True
        if all(self.super_board[i][i].winner == player for i in range(3)):
            return True
        if all(self.super_board[i][2 - i].winner == player for i in range(3)):
            return True
        return False

    def update_turn_label(self):
        if self.player == 'X':
            self.nameturn.setText("PLAYER X")
            self.nameturn.setStyleSheet("color: #b7e3fe;")
        else:
            self.nameturn.setText("PLAYER O")
            self.nameturn.setStyleSheet("color: #fd8755;")

    def highlight_winner(self, game_row, game_col):
        if self.super_board[game_row][game_col].winner == 'X':
            highlight_color = '#b7e3fe'
        elif self.super_board[game_row][game_col].winner == 'O':
            highlight_color = '#fd8755'
        else:
            return

        for row in range(3):
            for col in range(3):
                self.buttons[game_row * 3 + game_col][row][col].setStyleSheet(
                    f"background-color: {highlight_color}; "
                    "border: 2px solid #FFA500; "
                    "font-size: 20px; "
                    "color: #000000;"
                )


class SuperTicTacToe_AI(QtWidgets.QMainWindow):
    def __init__(self, x_name):
        super(SuperTicTacToe_AI, self).__init__()
        uic.loadUi('.ui/playervsai.ui', self)
        UIUtils.remove_window_header(self) 
        UIUtils.apply_rounded_corners(self)   
        UIUtils.setup_window_drag(self) 
        self.super_board = [[TicTacToe() for _ in range(3)] for _ in range(3)]
        self.main_winner = None
        self.current_game = None
        self.scorex = 0  
        self.scoreo = 0 
        self.player = 'X'
        self.buttons = [[[None for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.setup_ui()
        self.x_name = x_name

        self.namex_label = self.findChild(QtWidgets.QLabel, 'namex')
        self.namex_label.setText(self.x_name)

        self.volume_button = self.findChild(QtWidgets.QPushButton, 'volume')
        if self.volume_button:
            self.volume_button.clicked.connect(self.toggle_volume)

    def toggle_volume(self):
        CLICK_SOUND.play()
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0 if current_volume > 0 else 1)
        
    def setup_ui(self):
        self.nameturn = self.findChild(QtWidgets.QLabel, 'nameturn')
        self.update_turn_label()  
        game_layout = QtWidgets.QGridLayout(self.game_frame)
        game_layout.setSpacing(10)
        game_layout.setContentsMargins(5, 5, 5, 5)
        
        self.findChild(QtWidgets.QPushButton, 'settings').clicked.connect(self.launch_settings_ui)

        for game_row in range(3):
            for game_col in range(3):
                inner_grid = QtWidgets.QGridLayout()
                inner_grid.setSpacing(10)
                inner_grid.setContentsMargins(10, 10, 10, 10)
                for row in range(3):
                    for col in range(3):
                        btn = QtWidgets.QPushButton(' ')
                        btn.setFixedSize(46, 48)
                        btn.setStyleSheet(
                            "border: 2px solid #FFA500; " 
                            "font-size: 20px; "
                            "color: #000000; "
                            "background-color: #FFFFFF;"
                        )
                        btn.clicked.connect(lambda _, r=game_row, c=game_col, sr=row, sc=col: self.play_move(r, c, sr, sc))
                        inner_grid.addWidget(btn, row, col)
                        self.buttons[game_row * 3 + game_col][row][col] = btn
                game_layout.addLayout(inner_grid, game_row, game_col)

    def launch_settings_ui(self):
        CLICK_SOUND.play()
        self.settings_window = QtWidgets.QMainWindow() 
        uic.loadUi('.ui/settings.ui', self.settings_window)
        UIUtils.remove_window_header(self.settings_window)
        UIUtils.apply_rounded_corners(self.settings_window)
        UIUtils.setup_window_drag(self.settings_window)
        self.settings_window.backmain.clicked.connect(self.back_to_main_menu)
        self.settings_window.restartgame.clicked.connect(self.restart_game)
        self.settings_window.continuegame.clicked.connect(self.continue_game)
        self.settings_window.show() 

    def back_to_main_menu(self):
        CLICK_SOUND.play()
        self.settings_window.close()
        self.close()  
        self.main_window = MainWindow()  
        self.main_window.show()

    def restart_game(self):
        CLICK_SOUND.play()
        if hasattr(self, 'settings_window') and self.settings_window:
            self.settings_window.close()
        
        self.scorex = 0
        self.scoreo = 0
        self.main_winner = None
        self.player = 'X'
        self.current_game = None
        self.super_board = [[TicTacToe() for _ in range(3)] for _ in range(3)]

        for i in range(9):
            for j in range(3):
                for k in range(3):
                    self.buttons[i][j][k].setText(' ')
                    self.buttons[i][j][k].setStyleSheet(
                        "border: 2px solid #FFA500; "
                        "font-size: 20px; "
                        "color: #000000; "
                        "background-color: #FFFFFF;"
                    )
        
        self.update_score_label('X')
        self.update_score_label('O')
        

    def continue_game(self):
        self.settings_window.close() 

    def play_move(self, game_row, game_col, row, col):
        if self.main_winner:
            QMessageBox.information(self, "Game Over", f"{self.main_winner} has already won the game!")
            return
        if self.current_game and self.current_game != (game_row, game_col):
            QMessageBox.critical(self, "Invalid Move", f"You must play in the game at {self.current_game}.")
            return
        if not self.super_board[game_row][game_col].play_move(row, col, self.player):
            QMessageBox.critical(self, "Invalid Move", "This move is not allowed. Try again!")
            return

        CLICK_SOUND.play()
        self.update_button(game_row, game_col, row, col)

        if self.super_board[game_row][game_col].winner:
            self.highlight_winner(game_row, game_col)
            self.update_score(self.player)

        if self.check_main_winner(self.player):
            self.main_winner = self.player
            self.launch_winner_ui(self.player)
            return

        if self.is_draw():
            self.launch_draw_ui()
            return

        self.current_game = (row, col)
        if self.super_board[row][col].is_full() or self.super_board[row][col].winner:
            self.current_game = None

        self.player = 'O'
        self.update_turn_label()

        # Computer's turn
        QtWidgets.QApplication.processEvents()
        self.computer_move()

    def computer_move(self):
        if self.main_winner or self.is_draw():
            return

        if self.current_game:
            game_row, game_col = self.current_game
        else:
            game_row, game_col = self.choose_best_game()

        row, col = self.choose_best_move(game_row, game_col)
        
        self.super_board[game_row][game_col].play_move(row, col, 'O')
        self.update_button(game_row, game_col, row, col)

        if self.super_board[game_row][game_col].winner:
            self.highlight_winner(game_row, game_col)
            self.update_score('O')

        if self.check_main_winner('O'):
            self.main_winner = 'O'
            self.launch_winner_ui('O')
            return

        if self.is_draw():
            self.launch_draw_ui()
            return

        self.current_game = (row, col)
        if self.super_board[row][col].is_full() or self.super_board[row][col].winner:
            self.current_game = None

        self.player = 'X'
        self.update_turn_label()

    def choose_best_game(self):
        valid_games = [(r, c) for r in range(3) for c in range(3) 
                    if not self.super_board[r][c].winner and not self.super_board[r][c].is_full()]
        
        for r, c in valid_games:
            if self.can_win_game(r, c, 'O'):
                return r, c
        
        for r, c in valid_games:
            if self.can_win_game(r, c, 'X'):
                return r, c
        
        preferred_order = [(1,1), (0,0), (0,2), (2,0), (2,2), (0,1), (1,0), (1,2), (2,1)]
        for r, c in preferred_order:
            if (r, c) in valid_games:
                return r, c
        
        return random.choice(valid_games)

    def choose_best_move(self, game_row, game_col):
        board = self.super_board[game_row][game_col]
        valid_moves = [(r, c) for r in range(3) for c in range(3) if board.board[r][c] == ' ']

        for r, c in valid_moves:
            if self.is_winning_move(board, r, c, 'O'):
                return r, c
        
        for r, c in valid_moves:
            if self.is_winning_move(board, r, c, 'X'):
                return r, c
        
        preferred_order = [(1,1), (0,0), (0,2), (2,0), (2,2), (0,1), (1,0), (1,2), (2,1)]
        for r, c in preferred_order:
            if (r, c) in valid_moves:
                return r, c
        
        return random.choice(valid_moves)

    def can_win_game(self, game_row, game_col, player):
        board = self.super_board[game_row][game_col]
        return any(self.is_winning_move(board, r, c, player) 
                for r in range(3) for c in range(3) if board.board[r][c] == ' ')

    def is_winning_move(self, board, row, col, player):
        board.board[row][col] = player
        result = board.check_winner(player)
        board.board[row][col] = ' '
        return result

    def update_button(self, game_row, game_col, row, col):
        button = self.buttons[game_row * 3 + game_col][row][col]
        button.setText(self.player)

        if self.player == 'X':
            button.setStyleSheet(
                "border: 2px solid #FFA500; "  
                "font-family: 'Comic Sans MS';"
                "font-size: 12pt;"
                "color: #b7e3fe;"
                "background-color: #FFFFFF;"  
            )  
        else:
            button.setStyleSheet(
                "border: 2px solid #FFA500; "
                "font-family: 'Comic Sans MS';"
                "font-size: 12pt;"
                "color: #fd8755;; "
                "background-color: #FFFFFF;" 
            ) 

    def update_score(self, player):
        if player == 'X':
            self.scorex += 1
            self.update_score_label('X')
        else:
            self.scoreo += 1
            self.update_score_label('O') 

    def update_score_label(self, player):
        if player == 'X':
            scorex_lbl = self.findChild(QtWidgets.QLabel, 'scorex')  
            scorex_lbl.setText(f"{self.scorex}")
        elif player == 'O':
            scoreo_lbl = self.findChild(QtWidgets.QLabel, 'scoreo') 
            scoreo_lbl.setText(f"{self.scoreo}")

    def launch_winner_ui(self, winner):
        self.winner_window = QtWidgets.QMainWindow()
        uic.loadUi('.ui/playerwins.ui', self.winner_window)
        player_label = self.winner_window.findChild(QtWidgets.QLabel, 'playername')
        if winner == 'X':
            player_label.setText("PLAYER X")
            player_label.setStyleSheet("color: #b7e3fe;")
        else:
            player_label.setText("PLAYER O")
            player_label.setStyleSheet("color: #fd8755;")

        rematch_button = self.winner_window.findChild(QtWidgets.QPushButton, 'rematch')
        back_button = self.winner_window.findChild(QtWidgets.QPushButton, 'back')
        rematch_button.clicked.connect(self.rematch_game)
        back_button.clicked.connect(self.back_to_main)

        self.winner_window.show()

    def launch_draw_ui(self):
        draw_window = QtWidgets.QMainWindow()
        uic.loadUi('.ui/playerdraw.ui', draw_window)
        wins_label = draw_window.findChild(QtWidgets.QLabel, 'wins_lbl') 

        if self.scorex > self.scoreo:
            wins_label.setText(f"DRAW BUT X WINS THE MOST! ({self.scorex} to {self.scoreo})")
        elif self.scoreo > self.scorex:
            wins_label.setText(f"DRAW BUT O WINS THE MOST! ({self.scoreo} to {self.scorex})")
        else:
            wins_label.setText("DRAW! BOTH PLAYERS ARE EQUAL!")
        draw_window.show()

    def rematch_game(self):
        self.winner_window.close() if hasattr(self, 'winner_window') else None
        self.draw_window.close() if hasattr(self, 'draw_window') else None
        self.restart_game()

    def back_to_main(self):
        self.winner_window.close() if hasattr(self, 'winner_window') else None
        self.draw_window.close() if hasattr(self, 'draw_window') else None
        self.close()

    def is_draw(self):
        return all(board.is_full() for row in self.super_board for board in row) and not self.main_winner

    def check_main_winner(self, player):
        for i in range(3):
            if all(self.super_board[i][j].winner == player for j in range(3)):
                return True
            if all(self.super_board[j][i].winner == player for j in range(3)):
                return True
        if all(self.super_board[i][i].winner == player for i in range(3)):
            return True
        if all(self.super_board[i][2 - i].winner == player for i in range(3)):
            return True
        return False

    def update_turn_label(self):
        if self.player == 'X':
            self.nameturn.setText("PLAYER X")
            self.nameturn.setStyleSheet("color: #b7e3fe;")
        else:
            self.nameturn.setText("PLAYER O")
            self.nameturn.setStyleSheet("color: #fd8755;")

    def highlight_winner(self, game_row, game_col):
        if self.super_board[game_row][game_col].winner == 'X':
            highlight_color = '#b7e3fe'
        elif self.super_board[game_row][game_col].winner == 'O':
            highlight_color = '#fd8755'
        else:
            return

        for row in range(3):
            for col in range(3):
                self.buttons[game_row * 3 + game_col][row][col].setStyleSheet(
                    f"background-color: {highlight_color}; "
                    "border: 2px solid #FFA500; "
                    "font-size: 20px; "
                    "color: #000000;"
                )

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()