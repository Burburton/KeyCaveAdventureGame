import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog


GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP, *DIRECTIONS.keys()]

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."


class Display:
    """Display of the dungeon."""

    def __init__(self, game_information, dungeon_size):
        """Construct a view of the dungeon.

        Parameters:
            game_information (dict<tuple<int, int>: Entity): Dictionary
                containing the position and the corresponding Entity
            dungeon_size (int): the width of the dungeon.
        """
        self._game_information = game_information
        self._dungeon_size = dungeon_size

    def display_game(self, player_pos):
        """Displays the dungeon.

        Parameters:
            player_pos (tuple<int, int>): The position of the Player
        """
        dungeon = ""

        for i in range(self._dungeon_size):
            rows = ""
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = self._game_information.get(position)

                if entity is not None:
                    char = entity.get_id()
                elif position == player_pos:
                    char = PLAYER
                else:
                    char = SPACE
                rows += char
            if i < self._dungeon_size - 1:
                rows += "\n"
            dungeon += rows


    def display_moves(self, moves):
        """Displays the number of moves the Player has left.

        Parameters:
            moves (int): THe number of moves the Player can preform.
        """
        print(f"Moves left: {moves}\n")


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.

    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    if len(dungeon_layout) != len(dungeon_layout[0]):
        level = dungeon_layout[-2]
        s = ''
        for l in level:
            s += l
        level = int(s)
        dungeon_layout = dungeon_layout[:-2]
    else:
        level = 0

    return dungeon_layout, level

class Entity:
    """ """

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = WALL

    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """ """

    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = KEY

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """ """

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = DOOR

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                return
        messagebox.showinfo('Notice', "You don't have the key!")


class Player(Entity):
    """ """

    _id = PLAYER

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def add_item(self, item):
        """Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory


class GameLogic:
    """ """

    def __init__(self, dungeon_name="game2.txt"):
        """ """
        self._dungeon, self.level = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        if dungeon_name in GAME_LEVELS:
            self._player = Player(GAME_LEVELS[dungeon_name])
        else:
            self._player = Player(self.level)
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions(PLAYER)[0]

        key_position = self.get_positions(KEY)

        door_position = self.get_positions(DOOR)
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)

        self._player.set_position(player_pos)

        information = {}
        if len(key_position):
            information[key_position[0]] = Key()
        else:
            self._player.add_item(Key())

        if len(door_position):
            information[door_position[0]]= Door()

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True

        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win


TILES = {"WALL":'#', "PLAYER":'O', "DOOR": 'D', "KEY":'K', "BANANA":'M', "Null": 0}
# the following parameters stand for the level of game
TASK_ONE = 1
TASK_TWO = 2
MASTERS = 3


class AbstractGrid(tk.Canvas):
    '''
    the class is a abstract class to draw a grid map
    '''
    def __init__(self, master, rows, cols, width, height, *args, **kwargs):
        '''
        To initialize the class, including the size of the grid
        '''
        super().__init__(master, *args, **kwargs)
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.annotate_dict = {}

    def annotate_position(self, position: tuple, text: str):
        '''

        :param position: a position on the grid
        :param text: the contain on the grid
        '''
        self.annotate_dict[position] = text


class DungeonMap(AbstractGrid):
    '''
    a Concrete class to describe the board of the game
    '''
    def __init__(self, master, board, size=5, width=600, *args, **kwargs):
        '''

        :param master: parent frame
        :param board: the matrix of the game
        :param size: the size of the board
        :param width: the width of the canvas
        :param args:
        :param kwargs:
        '''
        super().__init__(master, size, size, width, 800, *args, **kwargs)

        self.board_matrix = board
        self.board_grid = self.load_board_grid()
        self.redraw_board_grid(self.board_matrix)

    def load_board_grid(self):
        '''
        to initialize the grid board and store the tiles of the board
        :return: the collection of the tiles
        '''
        labels = []

        for y, row in enumerate(self.board_matrix):
            board_row = []
            for x, tile in enumerate(row):
                placement = tk.Label(self.master, text='  ', bg='green')
                placement.grid(column=x, row=y, ipadx=20, ipady=20, padx=0, pady=0)
                board_row.append(placement)
            labels.append(board_row)

        return labels

    def redraw_board_grid(self, board):
        '''
        to update the disappearing of the board of game
        :param board: the matrix of board of game
        :return:
        '''

        self.board_matrix = board

        for y, row in enumerate(self.board_matrix):
            for x, tile in enumerate(row):
                text, background = self._text_and_background(tile)
                placement = self.board_grid[y][x]
                if tile != 0:
                    placement.config(text=text, bg=background, borderwidth=0.5, relief="solid")
                else:
                    placement.config(text=text, bg=background, borderwidth=0)

    def _text_and_background(self, tile):
        '''
        get the contain of tiles and the background color, different tiles have different contain and bg
        :param tile: the char of the matrix of board
        :return: the corresponding contain and background color
        '''

        try:
            if tile == TILES["WALL"]:
                text = '   '
                background = 'Gray'
            elif tile == TILES["PLAYER"]:
                text = 'P'
                background = 'Medium spring green'
            elif tile == TILES["KEY"]:
                text = 'K'
                background = 'Yellow'
            elif tile == TILES["DOOR"]:
                text = 'D'
                background = 'Red'
            elif tile == TILES["BANANA"]:
                text = 'B'
                background = 'Orange'
            elif tile == TILES["Null"]:
                text = '   '
                background = 'DarkGray'
            else:
                text = '   '
                background = 'DarkGray'

        except AttributeError:
            text = ''
            background = 'ForestGreen'

        return text, background


class KeyPad(AbstractGrid):
    '''
    a Concrete class to describe the controller pad on the game
    '''
    def __init__(self, master, width=200, height=100, **kwargs):
        '''

        :param master: draw on the master frame
        :param width: the width of the class
        :param height: the height of the class
        '''
        super().__init__(master, 3, 2, width, height, **kwargs)
        self.isCommand = False
        self.command = None
        self.initialize_annotation()
        self.pad_label = self.load_pad()

    def initialize_annotation(self):
        '''
        to initialize the contain of the controller buttons
        :return:
        '''
        self.annotate_position((0, 1), 'W')
        self.annotate_position((1, 0), 'A')
        self.annotate_position((1, 1), 'S')
        self.annotate_position((1, 2), 'D')

    def load_pad(self):
        '''
        to distribute the pad buttons and store the button
        :return: the pad buttons list
        '''
        labels = []
        for key, value in self.annotate_dict.items():
            x, y = key
            placement = tk.Label(self.master, text=value, bg='Gray')
            placement.grid(column=y, row=x, ipadx=30, ipady=20, padx=0.1, pady=1)
            placement.config(borderwidth=1, relief="solid")
            self.bind_click(placement, key)
            labels.append(placement)

        return labels

    def bind_click(self, label, position):
        '''
        to place a click and key detector on the label
        :param label: the button
        :param position: the position of label button
        :return:
        '''
        label.bind("<Button-1>", lambda e: self.left_click(position))
        label.bind_all("<Key>", lambda e: self.key_down(e))

    def left_click(self, position):
        '''
        after left click the pad controller, it would command
        :param position: the position mouse clicked
        :return:
        '''
        self.isCommand = True
        self.command = self.annotate_dict[position]

    def key_down(self, event):
        '''
        when key down, it would command
        :param event: the key press event
        :return:
        '''
        self.isCommand = True
        self.command = event.char.upper()

    def pad_command(self):
        '''
        determine if command
        :return: if command return the contain of command, if not return None
        '''
        if self.isCommand:
            return self.command
        else:
            return None

    def set_command_false(self):
        '''
        after executive command, close the command
        :return:
        '''
        self.isCommand = False


class StatusBar(tk.Frame):
    '''
    a class to describe the status of game, it is a panel for the game
    '''
    def __init__(self, master, timer=0, *args, **kwargs):
        '''

        :param master: the class draw on the master frame
        :param timer: a timer to record the running time
        '''

        super().__init__(master, *args, **kwargs)
        self.timer = timer
        self.timer_label = None
        self.state = True # to determine game is running
        self.is_reset = False
        self.button_frame, self.timer_frame, self.step_frame = None, None, None
        self.left_move = None

        self.initialize_button_frame()
        self.initialize_timer_frame()
        self.initialize_step_frame()

    def initialize_button_frame(self):
        '''
        a specific area to draw buttons including new game and quit
        :return:
        '''
        self.button_frame = tk.Frame(self.master)
        quit_button = tk.Button(self.button_frame, text="Quit", command=self.quit)
        newgame_button = tk.Button(self.button_frame, text="New Game", command=self._new_game)
        quit_button.pack(side=tk.BOTTOM)
        newgame_button.pack(side=tk.BOTTOM)
        self.button_frame.pack(side=tk.LEFT)

    def initialize_timer_frame(self):
        '''
        a specific area to draw timer including a icon and the time number
        :return:
        '''
        self.timer_frame = tk.Frame(self.master)
        self.timer_frame.pack(side=tk.LEFT)

        image = get_image("clock", 50)

        timer = tk.Label(self.timer_frame, image=image)
        timer.image = image
        timer.pack(side=tk.LEFT)

        text = 'Time elapsed:\n%s m %s s' % (self.timer//60, self.timer % 60)
        self.timer_label = tk.Label(self.timer_frame, text=text)
        self.timer_label.pack(side=tk.RIGHT)

        self.timepiece(self.timer_label)

    def initialize_step_frame(self, left_step=12):
        '''
        a specific area to show the left moves of player including a icon and the information
        :param left_step: the left moves of player
        :return:
        '''
        self.step_frame = tk.Frame(self.master)
        self.step_frame.pack(side=tk.LEFT)

        image = get_image("lightning", 50)
        lightning = tk.Label(self.step_frame, image=image)
        lightning.image = image
        lightning.pack(side=tk.LEFT)

        text = "Moves Left\n %s moves remaining"%left_step
        self.left_move = tk.Label(self.step_frame, text=text)
        self.left_move.pack(side=tk.RIGHT)

    def update_step_frame(self, left_step):
        '''
        to update the number of left moves after every move
        :param left_step: the left moves of player
        :return:
        '''
        text = "Moves Left\n %s moves remaining" % left_step
        self.left_move.config(text=text)

    def quit(self):
        '''
        to quit the game
        :return:
        '''
        self.master.master.destroy()

    def _new_game(self):
        '''
        to open a new game
        :return:
        '''
        self.is_reset = True

    def new_game_signal(self):
        '''
        to launch a signal to gameapp that it needs to open a new game
        :return:
        '''
        return self.is_reset

    def timepiece(self, label):
        '''
        it is a timer to record time
        :param label: the label that show the number of time
        :return:
        '''
        try:
            if self.state:
                text = 'Time elapsed:\n%s m %s s' % (self.timer // 60, self.timer % 60)
                label.config(text=text)
                self.timer += 1
                self.master.after(1000, self.timepiece, label)
            else:
                self.state = False
        except Exception as e:
            print(e)


class LifeBar(StatusBar):
    '''
    the class was designed for the master mode, player would have 3 times chances to undo the step
    '''
    def __init__(self, master, game, *args, **kwargs):
        '''

        :param master: the class draw on the master frame
        :param game: a GameLogic class, it is the logic of the game
        '''
        super().__init__(master)
        self.life_frame = None
        self.left_life = 3
        self.gameapp = game
        self.player_positions = []
        self.info_status = []
        self.moves_status = []
        self.timer_status = []
        self.initialize_life_frame()

    def initialize_life_frame(self):
        '''
        to generate the life bar frame on the class, including a icon and information of life
        :return:
        '''
        self.life_frame = tk.Frame(self.master)
        self.life_frame.pack(side=tk.RIGHT)

        image = get_image("lives", 50)
        lives = tk.Label(self.life_frame, image=image)
        lives.image = image
        lives.pack(side=tk.LEFT)

        text_frame = tk.Frame(self.life_frame)
        text_frame.pack(side=tk.RIGHT)

        text = "Lives remaining: %s" % self.left_life
        self.life_label = tk.Label(text_frame, text=text)
        self.life_label.pack(side=tk.TOP)

        button = tk.Button(text_frame, text='Use', command=self.use_life)
        button.pack(side=tk.BOTTOM)

    def update_life(self):
        '''
        to update the data of the life bar
        :return:
        '''
        text = "Lives remaining: %s" % self.left_life
        self.life_label.config(text=text)

    def restore_status(self, player_position, infos, moves, timer):
        '''
        several lists to store the information the after player handled
        :param player_position: the player's position
        :param infos: the information of the board
        :param moves: the left moves of the player
        :param timer: the time when the player did
        :return:
        '''
        self.player_positions.append(player_position)
        self.info_status.append(infos)
        self.moves_status.append(moves)
        self.timer_status.append(timer)

    def use_life(self):
        '''
        to lauch the function to undo the operation of player. the game would go back to the last status of game
        :return:
        '''
        if self.left_life and self.player_positions:
            self.left_life -= 1
            text = "Lives remaining: %s" % self.left_life
            self.life_label.config(text=text)
            if self.player_positions:
                self.gameapp.game.get_player().set_position(self.player_positions.pop())
                self.gameapp.game._game_information = self.info_status.pop()

                for i in self.gameapp.game.get_player().get_inventory():
                    if i in self.gameapp.game.get_game_information().values():
                        self.gameapp.game.get_player().get_inventory().pop()

                self.gameapp.game.get_player().change_move_count(- self.gameapp.game.get_player().moves_remaining() +
                                                                 self.moves_status.pop())
                self.gameapp.update_board()
                self.gameapp.map.redraw_board_grid(self.gameapp.board)

                self.gameapp.statusbar.timer = self.timer_status.pop()
        else:
            messagebox.showinfo('Error', 'Your do not have any life or you did not do any operations after switching to'
                                         ' MASTER mode.')


class MenuBar(tk.Menu):
    '''
    a frame to draw the menu bar. it includes two part: game and task
    '''
    def __init__(self, master, game_app, *args, **kwargs):
        '''

        :param master: the menu bar would be draw on the master frame
        :param gameapp: the GameApp class
        '''
        super().__init__(master, *args, **kwargs)
        self.gameApp = game_app
        self.game_frame = None
        self.task_frame = None

        self.initialize_menu()

    def initialize_menu(self):
        '''
        to initialize the menu buttons including Task and Game
        :return:
        '''
        self.game_frame = tk.Menu(self, tearoff=0)
        self.game_frame.add_command(label ="Save Game", command=self._save_game)
        self.game_frame.add_command(label ="Load Game", command=self._load_game)
        self.game_frame.add_command(label="New Game", command=self._new_game)
        self.game_frame.add_command(label="High Scores", command=self._high_score)
        self.game_frame.add_separator()
        self.game_frame.add_command(label='Quit', command=self._quit)

        self.add_cascade(label="File", menu=self.game_frame)

        self.task_frame = tk.Menu(self, tearoff=0)
        self.task_frame.add_command(label="TASK ONE", command=self._task_one)
        self.task_frame.add_command(label="TASK TWO", command=self._task_two)
        self.task_frame.add_command(label="MASTERS", command=self._task_master)

        self.add_cascade(label="Task", menu=self.task_frame)

    def _high_score(self):
        '''
        to read the rank file and show the information of the rank
        :return:
        '''
        try:
            file_path = 'high_scores.txt'
            with open(file_path, 'r') as load_file:
                content = load_file.readlines()

            rank = {}
            for i in content:
                rank[i.split(':')[0]] = i.split(':')[1]

            rank = sorted(rank.items(), key=lambda item: int(item[1]))
            rank_message = ''

            for key, value in enumerate(rank):
                temp = int(value[1])
                if key < 3:
                    rank_message += '%s: %s m %s s\n'%(value[0],  temp // 60, temp % 60)

            messagebox.showinfo('High Scores', rank_message)
        except Exception as e:
            messagebox.showinfo('Top 3', 'Load failed. It will go to new default game')

    def _save_game(self):
        '''
        to save the detail of the game. it can be gone back to current state of the game
        :return:
        '''
        if self.gameApp.stop:
            messagebox.showinfo('Error', 'The Game Was End, You Cannot Save It!')
            return

        map_to_matrix = ''
        for row in self.gameApp.board:
            for i in row:
                if i != 0:
                    map_to_matrix += i
                else:
                    map_to_matrix += ' '
            map_to_matrix += '\n'

        file_content = "%s\n%s\n%s" % (map_to_matrix[:-1], self.gameApp.game.get_player().moves_remaining(),
                                       self.gameApp.statusbar.timer)

        file_path = filedialog.asksaveasfilename(title=u'Save Game', defaultextension='.txt',
                                                 initialfile='untitled_game',
                                                 filetypes=[('text file', '.txt'), ('all file', '.*')])

        if file_content is not None:
            try:
                with open(file=file_path, mode='w', encoding='utf-8') as file:
                    file.write(file_content)
                file.close()
                messagebox.showinfo('Save Game', 'Done')
            except:
                pass

    def _load_game(self):
        '''
        to read the saved file to go back to the state of saved game
        :return:
        '''
        try:
            file_path = filedialog.askopenfilename(title=u'Load File',
                                                   filetypes=[('text file', '.txt'), ('all file', '.*')])
            with open(file_path, 'r') as load_file:
                content = load_file.readlines()

            file_path = file_path.split('/')[-1]

            if file_path in GAME_LEVELS.keys():
                self.gameApp.statusbar.timer = 0
            else:
                timer = int(content[-1])
                self.gameApp.statusbar.timer = timer
            self.gameApp.game = GameLogic(file_path)
            self.gameApp.redraw()

        except Exception as e:
            messagebox.showinfo('Load Game', 'Sorry, load Failed. There are some unknown errors')

    def _new_game(self):
        '''
        to open a new game
        :return:
        '''
        self.gameApp.new_game()

    def _task_one(self):
        '''
        to switch to task one mode
        :return:
        '''
        if self.gameApp.task != TASK_ONE:
            self.gameApp.task = TASK_ONE
            self.gameApp.redraw()

    def _task_two(self):
        '''
        to switch to task two mode
        :return:
        '''
        if self.gameApp.task != TASK_TWO:
            self.gameApp.task = TASK_TWO
            self.gameApp.redraw()

    def _task_master(self):
        '''
        to switch to Master mode
        :return:
        '''
        if self.gameApp.task != MASTERS:
            self.gameApp.task = MASTERS
            self.gameApp.redraw()

    def _quit(self):
        '''
        to quit the game
        :return:
        '''
        self.gameApp.master.destroy()


class AdvancedDungeoMap(DungeonMap):
    '''
    a advanced map class to show the map of the game. it would use the images to show the game
    '''
    def __init__(self, master, board, size=5, width=600, *args, **kwargs):
        '''

        :param master: the class would draw on the master
        :param board: the board matrix of the game
        :param size: the size of the map board
        :param width: the width of the map board
        '''
        super().__init__(master, board, size, width, *args, **kwargs)
        self.board_grid = self.load_board_grid()
        self.redraw_board_grid(self.board_matrix)

    def load_board_grid(self):
        '''
        to generate the board grid. it would be store in self.board_grid
        :return:
        '''
        labels = []

        for y, row in enumerate(self.board_matrix):
            board_row = []
            for x, tile in enumerate(row):
                placement = tk.Label(self.master, bg='green')

                placement.grid(column=x, row=y, sticky='nsew')
                board_row.append(placement)
            labels.append(board_row)

        return labels

    def redraw_board_grid(self, board):
        '''
        rewrite to parent function. it would update the map board
        :param board: the board matric of the game
        :return:
        '''
        self.board_matrix = board
        for y, row in enumerate(self.board_matrix):
            for x, tile in enumerate(row):
                placement = self.board_grid[y][x]
                image = self.load_image(tile)
                placement.config(image=image)
                placement.image=image

    def load_image(self, tile):
        '''
        to return a corresponding image for a tile
        :param tile: the sign on the matrix board
        :return: the image of the corresponding tile
        '''
        if tile == TILES["Null"]:
            image = get_image('empty')
        elif tile == TILES["WALL"]:
            image = get_image('wall')
        elif tile == TILES["KEY"]:
            image = get_image('key')
        elif tile == TILES["DOOR"]:
            image = get_image('door')
        elif tile == TILES["BANANA"]:
            image = get_image('moveIncrease')
        elif tile == TILES["PLAYER"]:
            image = get_image('player')
        else:
            image = get_image('empty')

        return image


class GameApp:
    '''
    a class to dispath the game running
    '''
    def __init__(self, master):
        '''
        to initialize all elements a game need
        :param master: draw the game on the master frame
        '''
        self.master = master

        # frames provided to put instance objects
        self.board_frame = None
        self.title_frame = None
        self.pad_frame = None
        self.statusbar_frame = None
        self.menu_frame = None
        self.middle_frame = None

        # several instance objects
        self.map = None
        self.pad = None
        self.statusbar = None
        self.game = GameLogic('game2.txt')
        self.board = self.transfer_board()

        # state of game
        self.stop = False
        self.task = TASK_TWO

        # running game
        self.draw()
        self.gaming()
        self.update_status_bar()
        self.check_reset()

    def transfer_board(self):
        '''
        to transfer the information of GameLogic class to a two-dimension matrix
        :return: the two-dimension matrix
        '''
        info = self.game.get_game_information()
        board = [[0 for i in range(self.game.get_dungeon_size())] for j in range(self.game.get_dungeon_size())]

        for keys, values in info.items():
            x, y = keys

            board[x][y] = values.get_id()
        px, py = self.game.get_player().get_position()
        board[px][py] = 'O'
        return board

    def update_board(self):
        '''
        to update the matrix board after a operation of player
        :return:
        '''
        self.board = self.transfer_board()

    def draw(self):
        '''
        to draw the game
        :return:
        '''
        self.draw_title()
        self.draw_middle()
        self.draw_board()
        self.draw_pad()
        self.draw_status_bar()
        self.draw_menu()

    def draw_middle(self):
        '''
        to draw the map board and pad controller on the middle area
        :return:
        '''
        self.middle_frame = tk.Frame(self.master)
        self.middle_frame.pack(side=tk.TOP)

    def draw_title(self):
        '''
        to draw the title on the top area of the window
        :return:
        '''
        # title frame
        self.title_frame = tk.Frame(self.master)
        self.title_frame.pack(side=tk.TOP)
        title_label = tk.Label(self.title_frame, text='Key Cave Adventure Game', font='Roman -20 bold', bg='red',
                               fg='white', width=100)
        title_label.pack(side=tk.TOP)

    def draw_board(self):
        '''
        to draw the map board on the left of middle area
        :return:
        '''
        # board frame
        self.board_frame = tk.Frame(self.middle_frame)
        # self.board_frame.config(bg='green')

        if self.task == TASK_ONE:
            self.map = DungeonMap(self.board_frame, self.board)
        elif self.task == TASK_TWO or self.task == MASTERS:
            self.map = AdvancedDungeoMap(self.board_frame, self.board)
        self.board_frame.pack(side=tk.LEFT)

    def draw_pad(self):
        '''
        to draw the map board on the right of middle area
        :return:
        '''
        # pad frame
        self.pad_frame = tk.Frame(self.middle_frame)
        self.pad = KeyPad(self.pad_frame)
        self.pad_frame.pack(side=tk.RIGHT)

    def draw_status_bar(self, timer=0):
        '''
        to draw the status bar on the bottom of the window
        :param timer: the start time of the timer
        :return:
        '''
        # status bar frame
        self.statusbar_frame = tk.Frame(self.master, width=600, height=200)
        if self.task == MASTERS:
            self.statusbar = LifeBar(self.statusbar_frame, self, timer)
        else:
            self.statusbar = StatusBar(self.statusbar_frame, timer)
        self.statusbar_frame.pack(side=tk.TOP)

    def draw_menu(self):
        '''
        to draw the menu
        :return:
        '''
        self.menu_frame = MenuBar(self.master, self)
        self.master.config(menu=self.menu_frame)

    def gaming(self):
        '''
        to run the game. the operation of player would be run in the function
        Also, it would update the status on the window of the game
        :return:
        '''
        # to check if the game is running
        if not self.stop:
            direction = self.pad.pad_command()
            if direction in DIRECTIONS:
                if not self.game.collision_check(direction):
                    # for MASTERs mode to store information before the operation
                    if self.task == MASTERS:
                        self.statusbar.restore_status(self.game.get_player().get_position(),
                                                      self.game.get_game_information().copy(),
                                                      self.game.get_player().moves_remaining(),
                                                      self.statusbar.timer)

                    # control the game based on the
                    self.game.move_player(direction)
                    self.game.get_player().change_move_count(-1)
                    entity = self.game.get_entity(self.game.get_player().get_position())


                    self.pad.set_command_false()
                    self.update_board()
                    self.map.redraw_board_grid(self.board)
                    if entity is not None:
                        entity.on_hit(self.game)
                    if self.game.won():
                        self.win()

                self.pad.set_command_false()
            self.master.after(100, self.gaming)

            if self.game.check_game_over():
                self.game_over()

    def game_over(self):
        '''
        run after game over. show some information and open a new game
        :return:
        '''
        self.stop_game()
        player_again = messagebox.askokcancel("You Lost!", "You lost the game.\n Would you like to play again")
        if player_again:
            self.new_game()

    def stop_game(self):
        '''
        to stop the game
        :return:
        '''
        self.stop = True
        self.statusbar.state = False

    def win(self):
        '''
        run after win the game. it would record the scores of the winner. and the winners have to write their name
        :return:
        '''
        self.stop_game()
        player_again = messagebox.askokcancel("You Won!", "You have finished the level with a score of 6."
                                                          "\n Would you like to play again")
        self.record()
        if player_again:
            self.new_game()

    def record(self):
        '''
        to record the score and name of the winners. it would be record into a file
        :return:
        '''
        try:
            record_file = 'high_scores.txt'
            score_name = simpledialog.askstring("Input",
                                                f"You won in {self.statusbar.timer // 60}m "
                                                f"{self.statusbar.timer % 60}s！ Enter your name:",parent=self.master)

            while score_name == None or score_name == '':
                score_name = simpledialog.askstring("Input",
                                                    f"You won in {self.statusbar.timer // 60}m "
                                                    f"{self.statusbar.timer % 60}s！ Enter your name:",
                                                    parent=self.master)

            clip = "%s:%s\n"%(score_name, self.statusbar.timer)

            with open(record_file, 'a+') as file:
                file.write(clip)
        except Exception as e:
            messagebox.showinfo('Error', 'Sorry, record Failed. There are some unknown errors')

    def new_game(self):
        '''
        to open a new game
        :return:
        '''
        self.game = GameLogic()
        self.stop = False

        self.statusbar.timer = 0
        self.redraw()

        self.gaming()

    def update_status_bar(self):
        '''
        to update the data of status bar including moves and timer
        :return:
        '''
        self.statusbar.update_step_frame(self.game.get_player().moves_remaining())
        self.master.after(100, self.update_status_bar)

    def check_reset(self):
        '''
        to check if open a new game
        :return:
        '''
        if self.statusbar.new_game_signal():
            self.stop_game()
            self.new_game()
        self.master.after(100, self.check_reset)

    def redraw(self):
        '''
        to redraw the whole window
        :return:
        '''
        tempTime = self.statusbar.timer
        self.statusbar_frame.destroy()
        self.board_frame.destroy()
        self.pad_frame.destroy()

        self.update_board()
        self.draw_board()
        self.draw_pad()
        self.draw_status_bar(tempTime)


def get_image(image_name, size=50):
    '''
    to reading the used image
    :param image_name: the name of the image file
    :param size: the size showing on the window
    :return: an image format could be used
    '''
    try:
        try:
            image = Image.open("images/" + image_name + ".png")
        except:
            image = Image.open("images/" + image_name + ".gif")
        image = image.resize((size, size), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        return image
    except:
        messagebox.showinfo('Error', 'You may miss some images')


def main():
    '''
    to run the instantiated game
    :return:
    '''
    root = tk.Tk()
    root.title('Key Cave Adventure Game')
    root.geometry("1000x800")

    GameApp(root)

    root.update()
    root.mainloop()


if __name__ == '__main__':
    main()
