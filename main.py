from tkinter import messagebox, Tk, PhotoImage
from tkinter.ttk import Notebook, Frame, Style
from tkinter import Menu, Toplevel

import webbrowser
import pandas as pd
import os
from datetime import datetime
import time
import asyncio
import sys
from pathlib import Path

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

        # make the window not resisable
        # self.resizable(False, False)

        # set size and min-size
        self.minsize(400,200)

        # set the logo
        logo_path = self.resource_path('Additional_files/logo.png')
        photo = PhotoImage(file=logo_path)
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

    def resource_path(self, relative_path):
        """ Get the absolute path to the resource for PyInstaller executables and scripts. 
        """
        
        if hasattr(sys, '_MEIPASS'):
            # Running from the PyInstaller bundle
            return Path(sys._MEIPASS) / relative_path
        else:
            # Running directly from the script
            return Path(__file__).parent / relative_path    

    def initialize_database(self,):
        '''Search in the cwd for pkl files and upload the most recent one as the original database.
        It also retrieves the corresponding .json file with the team's additional info.
        If no database exists at the moment it sets the original database to an empty DataFrame.
        Sets the attributes: self.original_database, self.number_of_players, self.database_date_modified,
        self.clubs_eso_players_url from the info in the json file

        Example 1: so_aigaleo.pkl , so_aigaleo.json is the most recent
        Action: self.original_database = pd.read_pickle('so_aigaleo.pkl')
                self.database_date_modified = '2024-05-04'
                self.database_time_modified = '20:58'
                self.number_of_players = 458
                self.team_name = 'so_aigaleo'
        
        Example 2: no database
        Action: self.original_database = pd.DataFrame({})
                self.team_name = 'No Database at the moment'
                self.database_date_modified = '2024-05-04'
                self.database_time_modified = '20:58'
                self.number_of_players = 0
        '''
        
        # find all databases in the current directory and choose the latest modified
        databases = [file for file in os.listdir() if file.endswith('.pkl') ]
        
        # if there is no database set the attributes to specific Null values
        if len(databases) == 0:
            self.original_database = pd.DataFrame({})
            self.team_name = 'No Database at the moment'
            self.number_of_players = 0
            self.database_date_modified = datetime.today().date()
            self.database_time_modified = datetime.today().time().isoformat('minutes')
            return
        
        # create a dictionary with datestamp : database_name pairs 
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
        '''Create the main frames of the application.
        '''

        # create an index column that starts at 1
        self.original_database = self.original_database.reset_index()
        self.original_database['index'] = self.original_database['index']+1

        # set all the headers that exist in the database and a default headers list to present to the user
        self.original_database_all_headers = list(self.original_database.columns)
        self.original_database_headers_to_show = ['index',
                                                  'National Name',
                                                  'National Elo',
                                                  'std',
                                                  'Age',
                                                  'Gender',
                                                  'National ID',
                                                  ]
        
        # create a dictionare that will hold the frames of the created teams as pairs 'team_name' : Frame
        self.created_teams_dic = {}
        
        # make the root window udaptive
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        #---------------------Style----------------------------------------------------------------
        
        # define background color of the main window
        self.configure(bg='lightgray')

        # define the style of the left and right frames
        self.style_left_right = Style()
        backgrond_colour = "#34495E"
        
        # self.style.configure('TLabelFrame',
        #                      background='red',
        #                      font = ('Helvetica', 14, 'bold'),
        #                      )
        
        self.style_left_right.configure("TLabel", 
                        background=backgrond_colour, 
                        foreground="white", 
                        font=('Helvetica', 10, 'bold')
                        )
        
        self.style_left_right.configure("TFrame", 
                        background=backgrond_colour,
                        )
        
        #-----------------------------Left Side Frame-------------------------------------------------------
        self.left_side_frame = Frame(self,
                                     )
        
        # left side frame 1: Search the Players Database
        self.left_side_frame_1 = SideFrame1(self.left_side_frame, self)
        
        self.left_side_frame_1.grid(row=0, 
                               column=0 , 
                               padx= 10, 
                               pady= 10, 
                               )

        # side frame 2: Create new teams
        self.left_side_frame_2 = SideFrame2(self.left_side_frame, self)
        self.left_side_frame_2.grid(row=1, 
                               column=0 , 
                               padx= 10, 
                               pady= 10, 
                            #    sticky='wn',
                               )
        
        # add the whole left frame, make stick to the left, top, bottom
        self.left_side_frame.grid(row=0,
                             column=0,
                             rowspan=2,
                             sticky='wns',
                             )
        
        # make the left frame adaptive
        self.left_side_frame.columnconfigure(0, weight=1)
        self.left_side_frame.rowconfigure([0, 1], weight=1)
        
        #---------------Right Side Frame----------------------------------------
        self.right_side_frame = Frame(self,)

        # right top frame
        self.configure_table_columns_frame = ConfigureTableColumnsFrame(self.right_side_frame, self)
        self.configure_table_columns_frame.grid(row=0,
                                                column=0,
                                                padx=10,
                                                pady=10,
                                                # sticky='n',
                                                )
        
        # right middle frame
        self.select_player_to_teams_frame = SelectPlayersToTeamsFrame(self.right_side_frame, self)
        self.select_player_to_teams_frame.grid(row=1, 
                                               column=0,
                                               padx = 10,
                                               pady=10,
                                            #    sticky='n',
                                               )
        
        # right  bottom frame: Update the datbase
        self.side_frame_3 = SideFrame3(self.right_side_frame, self)
        
        self.side_frame_3.grid(row=2, 
                               column=0 , 
                               padx= 10, 
                               pady= 10, 
                            #    sticky='n',
                               )
        
        # add the whole right frame, make it stick to the right, top, bottom
        self.right_side_frame.grid(row=0,
                                   column=2,
                                   rowspan=2,
                                   sticky = 'ens'
                                   )       
        
        # make the right frame adjustable
        self.right_side_frame.columnconfigure(0, weight=1)
        self.right_side_frame.rowconfigure([0, 1, 2], weight=1)
        
        #-----------------------------------Middle Up Database Frame-----------------------
        
        # Determine Width of the Treeview Database as follows: 
        # get actual screen width of the left and right frames to their contents
        # allocate the remaining avaliable width to the Treeview Database
        
        # update tasks to get the actual screen width of the left and right frame. 
        self.update_idletasks()

        # Get the width of the left and right frames and the total screen width
        left_frame_width = self.left_side_frame.winfo_reqwidth()
        right_frame_width = self.right_side_frame.winfo_reqwidth()
        screen_height, screen_width = self.winfo_screenheight(), self.winfo_screenwidth()
        
        # print(f'left frame {left_frame_width}, right frame {right_frame_width}')
        # print(f'height of screen {screen_height}, width of screen {screen_width}')
        
        # allocate the remaining avaliable width to the Treevies Database, minus some number fro padding etc.
        self.tree_width = screen_width - left_frame_width - right_frame_width - 50

        # print(f'width of the Treeview Database {self.tree_width}')
        
        # create the middle-top LabelFrame
        self.table_to_show_frame = RestrictedPlayersDatabaseFrame(self)
        self.table_to_show_frame.grid(row=0, 
                                      column=1, 
                                      padx= 10, 
                                      pady= 10, 
                                      sticky='n',
                                      )
        
        # try to make the tree responsive
        # self.table_to_show_frame.rowconfigure()
        
        # update the root to fix the tree width 
        self.update()
        
        # add the displayed columns to the tree without changing its width
        self.table_to_show_frame.modify_display_columns()
        

        #-------------------------Middle down teams notebook- created teams frames---------
        self.teams_selection_notebook = Notebook(self, ) 
                   
        self.teams_selection_notebook.grid(row=1,
                                         column=1,
                                         padx=10,
                                         pady=5,
                                         sticky='n',
                                         )
        
        #-------------------- Add Menu --------------------------------------------------
        
        # create a menu bar and help
        html_file_path = self.resource_path('Additional_files/documentation.html')
        self.menu_bar = Menu(self)
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Documentation", command=lambda: self.open_html_in_browser(html_file_path))
        self.menu_bar.add_cascade(label="Menu", menu=self.help_menu)
        self.config(menu=self.menu_bar)
    
        #-----------------Auto destroy---------------------------------------------------
        self.after(2000, self.auto_destroy)
    
    def open_html_in_browser(self, file_path):
        '''Takes a string with the name of an html documantation file and opens it in the default browser.
        '''
        # Ensure the file path is absolute
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)

        try:
            # Try opening the HTML file in the default web browser
            success = webbrowser.open(f'file:///{file_path}')
            if not success:
                raise Exception("Failed to open in the browser")
        except Exception as e:
            # If opening in the browser fails, fallback to displaying the HTML in a new window
            messagebox.showerror("Error", f"Failed to open the HTML file in the browser. Maybe open as an internal window.\n{str(e)}")
            # self.open_html_in_window(file_path)                 
        
    def create_new_team(self,):
        '''Creates a new team's frame in the notebook with the info of the entries in the left_side_frame2.
        and adds the team's frame to the created_teams_dic with key the team's name.
        We identify each team's frame by the teams name.
        If the name of the team exist in the dictionary then it updates the information of the match
        for that team to the current entries.
        '''
        # get the new team's info
        new_team_info_dic = self.left_side_frame_2.get_teams_info()

        # 14/5/23 maybe do not allow a team with no name
        # if new_team_info_dic["Team's Name:"] == '':
        #     return

        # check if the same name's team is already created
        if new_team_info_dic["Team's Name:"] not in self.created_teams_dic.keys(): 
            # creat the new team frame inside the notepad
            new_team_frame = TeamsCreation(self, self.teams_selection_notebook, new_team_info_dic)

            self.created_teams_dic[new_team_info_dic["Team's Name:"]] = new_team_frame

            # added to the notebook 
            self.teams_selection_notebook.add(new_team_frame,
                                            text= new_team_info_dic["Team's Name:"],
                                            )
            # update the root to fix the width of the team's tree
            self.update()

            # add the displayed columns to the team's tree without changing the tree width
            # to do that we need to update every team's frame in the notebook
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
        '''Update the original database and all the info of the team.
        '''
        club = FetchPlayersDatabase(self, self.clubs_eso_players_url)

        # async database update
        asyncio.run(club.main_fetch_built_database())

        # forget and redraw all frames in the main window 
        for frame in self.winfo_children():
            frame.grid_forget()

        self.initialize_database()
        self.initialize_root()
        
    def auto_destroy(self,):
        '''function to autodestroy the window after some time or conditions.
        Used as a safety net when wanting to distribut the software for limiting amond of time.
        '''

        # auto-destroy is the day is not a specific one; could do other restrictions
        # if datetime.today().day != 5:
        #     messagebox.showwarning(title='Time is Out', message='Your time is out, Contact the Ponny to renew!')
        #     time.sleep(1)
        #     self.destroy()
        

if __name__ == '__main__':

    main_window = root()
    
    main_window.mainloop()