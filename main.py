from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

import pandas as pd
import os
from datetime import datetime
import time
import asyncio

from Players_Database_Fetch_Explore.fetch_and_built_database_async import *
from Graphical_Interphase.left_side_frames import SideFrame1 , SideFrame2
from  Graphical_Interphase.table_frame import RestrictedPlayersDatabaseFrame
from Graphical_Interphase.teams_frame import TeamsCreation
from Graphical_Interphase.right_side_frames import ConfigureTableColumnsFrame, SelectPlayersToTeamsFrame, SideFrame3


class root(Tk):

    def __init__(self):
        
        super().__init__()

        self.clubs_eso_players_url = ''

        # set the title of the root window
        self.title('Chess Team Manager')

        # set the window to full screen
        self.state('zoomed')

        # set size and min-size
        self.minsize(400,200)

        # set the logo
        photo = PhotoImage(file='Pictures/logo.png')
        self.iconphoto(True, photo)
        
        # initialize the current database
        self.initialize_database()

        # initialize the root
        self.initialize_root()

        # note the user to update the database if the current month is changed
        today = datetime.today().date()
        if today.month != self.database_date_modified.month:
            time.sleep(1)
            messagebox.showinfo('Update Database', 'Please update database to get the latest elo!')

    def initialize_database(self,):
        
        # find all databases in the current directory and choose the latest modified
        databases = [file for file in os.listdir() if file.endswith('.pkl') ]
        
        if len(databases) == 0:
            self.original_database = pd.DataFrame({})
            self.team_name = 'No Database at the moment'
            self.number_of_players = 0
            self.database_date_modified = datetime.today().date()
            return
        
        dates = {}
        for dat in databases:
            timestamp = os.path.getmtime(dat)
            datestamp = datetime.fromtimestamp(timestamp)
            dates[datestamp] = dat
        
        # find the latest updated database, date is the date of the database file
        database_date, database_name = max(dates.items(), key=lambda x: x[0])
        
        # read and create a pandas dataframe for the latest database
        self.original_database = pd.read_pickle(database_name)

        # keep the date and the time seperately
        self.database_date_modified = database_date.date()
        self.database_time_modified = database_date.time().isoformat('minutes')

        # take the teams name from the name of the database if not changed thouhg   
        self.team_name = database_name.split('.')[0]

        # find the clubs URL
        if os.path.exists(f'{self.team_name}.json'):
            with open(f'{self.team_name}.json', 'r', encoding='utf-8') as file:
                teams_info_dic = json.load(file)
                if self.team_name in teams_info_dic:
                    self.clubs_eso_players_url = teams_info_dic[self.team_name]
                
                if 'Number of Players' in teams_info_dic:
                    self.number_of_players = teams_info_dic['Number of Players']

    def initialize_root(self):

        # self.original_database = database
        self.original_database = self.original_database.reset_index()
        self.original_database['index'] = self.original_database['index']+1

        self.original_database_all_headers = list(self.original_database.columns)
        self.original_database_headers_to_show = ['index',
                                                  'National Name',
                                                  'National Elo',
                                                  'std',
                                                  'Age',
                                                  'Gender',
                                                  'National ID',
                                                  ]

        self.created_teams_dic = {}

        #-----------------------------Left Side Frame-------------------------------------------
        self.left_side_frame = Frame(self, )
     
        # side frame 1: Search the Players Database
        self.side_frame_1 = SideFrame1(self.left_side_frame, self)
        
        self.side_frame_1.grid(row=0, 
                               column=0 , 
                               padx= 10, 
                               pady= 10, 
                               )

        # side frame 2: Create new teams
        self.side_frame_2 = SideFrame2(self.left_side_frame, self)
        self.side_frame_2.grid(row=1, 
                               column=0 , 
                               padx= 10, 
                               pady= 10, 
                            #    sticky='wn',
                               )
              
        self.left_side_frame.grid(row=0,
                             column=0,
                             rowspan=2,
                             sticky='wn'
                             )
        
        #-----------------------------------Middle Up Database Frame-----------------------
        # Players Database Frame
        self.tree_width = 765
        self.table_to_show_frame = RestrictedPlayersDatabaseFrame(self)
        self.table_to_show_frame.grid(row=0, 
                                      column=1, 
                                      padx= 10, 
                                      pady= 10, 
                                      sticky='n',
                                      )
        # update the root to fix the tree width 
        self.update()
        # add the displayed columns to the tree without changing its width
        self.table_to_show_frame.modify_display_columns()

        # Middle down teams notebook-frames
        self.teams_selection_notebook = Notebook(self, )    
        
        self.teams_selection_notebook.grid(row=1,
                                         column=1,
                                         padx=10,
                                         pady=5,
                                         sticky='n',
                                         )
        # self.teams_selection_notebook.grid_propagate(False)
        
        
        
        #---------------Right Side Frame----------------------------------------
        self.right_side_frame = Frame(self,)

        self.configure_table_columns_frame = ConfigureTableColumnsFrame(self.right_side_frame, self)

        self.configure_table_columns_frame.grid(row=0,
                                                column=0,
                                                padx=10,
                                                pady=20,
                                                # sticky='N',
                                                )
        
        self.select_player_to_teams_frame = SelectPlayersToTeamsFrame(self.right_side_frame, self)

        self.select_player_to_teams_frame.grid(row=1, 
                                               column=0,
                                               padx = 10,
                                               pady=20
                                            #    sticky='N',
                                               )
        
         # side frame 3: Update the datbase
        self.side_frame_3 = SideFrame3(self.right_side_frame, self)
        self.side_frame_3.config(text= 'Update Database')
        
        self.side_frame_3.grid(row=2, 
                               column=0 , 
                               padx= 10, 
                               pady= 20, 
                            #    sticky='wn',
                               )
        
        # add the whole right frame
        self.right_side_frame.grid(row=0,
                                   column=2,
                                   rowspan=2,
                                   sticky = 'en'
                                   )                           
        
    def create_new_team(self,):
        # get the new team's info
        new_team_info_dic = self.side_frame_2.get_teams_info()

        # check if the same name's team is already created
        if new_team_info_dic["Team's Name:"] not in self.created_teams_dic.keys(): 
            # creat the new team frame inside the notepad
            new_team_frame = TeamsCreation(self, self.teams_selection_notebook,new_team_info_dic)

            self.created_teams_dic[new_team_info_dic["Team's Name:"]] = new_team_frame

            # added to the notebook 
            self.teams_selection_notebook.add(new_team_frame,
                                            text= new_team_info_dic["Team's Name:"],
                                            )
            # update the root to fix the width of the team's tree
            self.update()

            # add the displayed columns to the team's tree without changing the tree width
            for frame in self.created_teams_dic.values():
                self.teams_selection_notebook.select(frame)
                self.update()
                frame.modify_display_columns()

            # update also the table's frame columns; otherwise the tree gets the width of the columns
            self.table_to_show_frame.modify_display_columns()
            
            # update the values in the combobox team selection to move players
            self.select_player_to_teams_frame.created_teams_box['values'] = list(self.created_teams_dic.keys())
            # and the values in the comobox in columns to select frame
            self.configure_table_columns_frame.team_col_toshow['values'] = ['Players Database'] + list(self.created_teams_dic.keys())

        else:
            # update the match info and labels
            self.created_teams_dic[new_team_info_dic["Team's Name:"]].update_match_info(new_team_info_dic)



    def update_database(self,):
        club = FetchPlayersDatabase(self, self.clubs_eso_players_url)

        # async database update
        asyncio.run(club.main_fetch_built_database())

        # forget and redraw all frames in the main window 
        for frame in self.winfo_children():
            frame.grid_forget()

        self.initialize_database()
        self.initialize_root()


if __name__ == '__main__':

    main_window = root()
    
    main_window.mainloop()