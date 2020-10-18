from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3

from game import Game

#Create if not existing and connect to DB
conn = sqlite3.connect('stats_2048.db')
curs = conn.cursor()
curs.execute("SELECT name FROM sqlite_master WHERE type='table' and name='leaderbooard' ORDER BY name")
table_in_db = curs.fetchall()
if len(table_in_db) == 0:
    curs.execute('''CREATE TABLE leaderbooard
    (Id INTEGER PRIMARY KEY, DateCreated TIMESTAMP, Score INTEGER, Moves INTEGER, HighestTile INTEGER)''')
conn.close()

#colors to display for each number - 0:white,2:yellow,...,2048:red,...
col_map = {0: '#fff', 2: '#ffe500', 4: '#fc0', 8: '#ffb200', 16: '#f90', 32: '#ff7f00', 64: '#f60', 128: '#ff4c00',\
           256: '#f30', 512: '#ff1900', 1024: '#f00', 2048: '#ff7f4c', 4096: '#ff7f99', 8192: '#f0f', 16384: '#0ff'}

# Initialize new game
new_game = Game()

#GUI
root = Tk()
root.wm_state('zoomed')
root.wm_title("2048")
root.minsize(500, 600)
root.maxsize(500, 600)

def render_cells(curr_state):
    c.delete('cell_rect')
    c.delete('cell_text')
    for i in range(4):
        for j in range(4):
            cell_color = col_map[curr_state[i][j]]
            cell_txt = ' ' if curr_state[i][j]==0 else str(curr_state[i][j])
            c.create_rectangle(100 * j+1, 100 * i+1, 100 * (j + 1), 100 * (i + 1), fill=cell_color, width=0, tags=('cell_rect'))
            c.create_text(int(100 * (j + 0.5)), int(100 * (i + 0.5)), fill='black', font="Times 25", text=cell_txt, tags=('cell_text'))

def reset_game():
    global new_game
    new_game = Game()
    score_label.configure(fg='blue')
    score_var.set(str(new_game.score))
    render_cells(new_game.curr_state)

def show_leaderboard():
    conn = sqlite3.connect('stats_2048.db')
    curs = conn.cursor()
    qry = 'select * from leaderbooard order by score desc limit 10'
    curs.execute(qry)
    q_result = curs.fetchall()
    conn.close()

    lb_window = Toplevel(root)
    lb_window.wm_title("Leaderboard")
    lb_window.minsize(850, 300)
    lb_window.maxsize(850, 300)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=(None, 12))
    cols = ('Date', 'Score', 'Moves','Highest Tile')
    lb_box = ttk.Treeview(lb_window, columns=cols, show='headings')
    for col in cols:
        lb_box.heading(col, text=col)
        lb_box.column(col, anchor="c")
    lb_box.pack(side=TOP,padx=10,pady=10,anchor='c',fill=BOTH,expand=True)

    for i, (_,lb_date, lb_score, lb_moves, lb_highest) in enumerate(q_result, start=1):
        lb_box.insert("", "end", values=(lb_date.split(' ')[0], lb_score, lb_moves, lb_highest))

def left_key(event):
    global action
    action = 'left'
    take_action(action)
def right_key(event):
    global action
    action = 'right'
    take_action(action)
def up_key(event):
    global action
    action = 'up'
    take_action(action)
def down_key(event):
    global action
    action = 'down'
    take_action(action)

def take_action(action):
    if new_game.game_over:
        messagebox.showinfo("Game Over", "You scored {} in {} moves !!!".format(new_game.score,new_game.moves))
        score_label.configure(fg='red')
        # Do DB update for game stats
        new_game.add_score_in_db()
    else:
        new_game.update_curr_state(action)
        render_cells(new_game.curr_state)
        score_var.set(str(new_game.score))

#Container for full visible area
container = Frame(root)
container.pack(side="top", fill="both", expand=True)

#Top frame for displaying score and reset and stats buttons
top_frame = Frame(container,height=100,width=500)
top_frame.pack(side=TOP,fill=X,expand=True)
top_frame.pack_propagate(0)

#Reset button at left and Stats button at right
reset_btn = Button(top_frame,text="RESET",bg='black',relief=FLAT,fg='white',height=2,width=10,command=reset_game)
reset_btn.pack(side=LEFT,padx=10,pady=30,anchor='c')
stats_btn = Button(top_frame,text="STATS",bg='black',relief=FLAT,fg='white',height=2,width=10,command=show_leaderboard)
stats_btn.pack(side=RIGHT,padx=10,pady=30,anchor='c')

#Label in center to show score, initially = 0
score_var = StringVar()
score_var.set(str(new_game.score))
score_label = Label(top_frame, textvariable=score_var,bg='lightblue',fg='blue',width=25,height=2,font=("Times", "14", "bold"))
score_label.pack(side=LEFT,padx=80,pady=30,anchor='c')

#Bottom frame for Canvas
bottom_frame = Frame(container,height=500,width=500)
bottom_frame.pack(side=TOP,fill=BOTH,expand=True)
bottom_frame.pack_propagate(0)

#Canvas to draw the 4x4 grid inside
c = Canvas(bottom_frame,relief=GROOVE,bg='white',bd=2)
c.pack(side=TOP,fill=BOTH,expand=True,padx=50,pady=50)

#Draw the horizontal and vertical lines to make the grid
line_marker_points = [100,200,300]
for lmp in line_marker_points:
    c.create_line(0, lmp, 400, lmp, fill='lightgrey')
    c.create_line(lmp, 0, lmp, 400, fill='lightgrey')

render_cells(new_game.curr_state)

c.bind('<Left>', left_key)
c.bind('<Right>', right_key)
c.bind('<Up>', up_key)
c.bind('<Down>', down_key)
c.focus_set()

root.mainloop()
