import numpy as np
from datetime import datetime
import sqlite3

class Game:
    def __init__(self):
        self.curr_state = np.zeros((4,4),dtype=np.int32)
        empty_cells = np.where(self.curr_state==0)
        two_random_cell_ids = np.random.choice(list(range(len(empty_cells[0]))),2,replace=False)
        self.curr_state[empty_cells[0][two_random_cell_ids[0]]][empty_cells[1][two_random_cell_ids[0]]] = 2
        self.curr_state[empty_cells[0][two_random_cell_ids[1]]][empty_cells[1][two_random_cell_ids[1]]] = 2
        self.score = 0
        self.start_time = datetime.now()
        self.moves = 0
        self.game_over = False

    def show_curr_state(self):
        for i in range(4):
            print('\t'.join([str(j) for j in self.curr_state[i]]))

    def find_empty_cells(self):
        return np.where(self.curr_state == 0)

    def fill_new_cell(self):
        empty_cells = self.find_empty_cells()
        random_cell_id = np.random.randint(0, len(empty_cells[0]))
        self.curr_state[empty_cells[0][random_cell_id]][empty_cells[1][random_cell_id]] = np.random.choice([2,4])

    def aggregate_row_or_col(self,row,action):
        row = row[row!=0]

        if action in ['up','left']:
            for i in range(len(row)-1):
                if row[i] == row[i+1]:
                    row[i] = 2*row[i]
                    row[i+1] = 0
                    self.score += row[i]
            row = list(row[row != 0])
            row = row + [0]*(4-len(row))
        else:
            for i in range(len(row)-1,0,-1):
                if row[i] == row[i-1]:
                    row[i] = 2*row[i]
                    row[i-1] = 0
                    self.score += row[i]
            row = list(row[row != 0])
            row = [0]*(4-len(row)) + row
        return np.array(row)

    def check_if_game_over(self):
        chk = True
        if len(np.where(self.curr_state==0)[0]) > 0:
            chk = False
        else:
            for i in range(4):
                for j in range(3):
                    if self.curr_state[i][j] == self.curr_state[i][j+1]:
                        chk = False
                        break
            for i in range(3):
                for j in range(4):
                    if self.curr_state[i][j] == self.curr_state[i+1][j]:
                        chk = False
                        break
        if chk:
            self.game_over = True

    def add_score_in_db(self):
        conn = sqlite3.connect('stats_2048.db')
        curs = conn.cursor()
        insert_values = (str(self.start_time),str(self.score),str(self.moves),str(np.max(self.curr_state)))
        curs.execute("INSERT INTO leaderbooard(DateCreated, Score, Moves, HighestTile) VALUES (?,?,?,?)", insert_values)
        conn.commit()
        conn.close()

    def update_curr_state(self,action):
        bef_upd_state = self.curr_state.copy()
        if action in ['up','down']:
            for i in range(4):
                self.curr_state[:,i] = self.aggregate_row_or_col(self.curr_state[:,i],action)
        elif action in ['left','right']:
            for i in range(4):
                self.curr_state[i,:] = self.aggregate_row_or_col(self.curr_state[i,:],action)
        if not np.all(bef_upd_state == self.curr_state):
            self.fill_new_cell()
        self.moves += 1
        self.check_if_game_over()

if __name__ == '__main__':
    new_game= Game()
    # new_game.show_curr_state()

    while not new_game.game_over:
        action = np.random.choice(['up','down','left','right'],p=[0.25,0.25,0.25,0.25])
        # print("------{}------".format(action))
        new_game.update_curr_state(action)
        # new_game.show_curr_state()
    print(new_game.score,new_game.moves)
    # new_game.show_curr_state()
