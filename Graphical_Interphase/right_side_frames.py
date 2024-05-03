from tkinter import *
from tkinter.ttk import Combobox
from tkinter.ttk import *
from tkinter import messagebox
import requests
import threading
import time


class ConfigureTableColumnsFrame(LabelFrame):

    def __init__(self, right_side_frame, parent):
        super().__init__(right_side_frame,
                        text='Configure Table Columns')
        self.parent = parent 

        
        #------#--------Add Widgets----------------------
        self.label_columns_to_show = Label(self,
                                           text='Columns to show:',
                                           )
        
        self.columns_to_show_combobox = Combobox(self,
                                                 values=self.parent.original_database_all_headers,
                                                 state='readonly',
                                                 )
        
        self.listbos_frame = Frame(self,)

        self.list_columns = Listbox(self.listbos_frame,
                                    height=len(self.parent.original_database_headers_to_show),
                                    )
        
        self.scroll_bar = Scrollbar(self.listbos_frame,
                                    command=self.list_columns.yview,
                                    )
        
        self.list_columns.config(yscrollcommand=self.scroll_bar.set)

        self.list_columns.pack(side=LEFT, fill=BOTH)
        self.scroll_bar.pack(side=RIGHT, fill=BOTH)

        # initalizy the columns in the list to the defauld displayed columns

        for i, col in enumerate(self.parent.original_database_headers_to_show):
            self.list_columns.insert(i, f'{i+1}. ' + col) 
        
        self.add_column_button = Button(self,
                                        text='Add Column',
                                        command=self.add_column_tolist,
                                        )
        
        self.remove_column_button = Button(self,
                                           text='Remove Column',
                                           command=self.remove_column_fromlist,
                                           )
        
        self.move_up_button = Button(self,
                                     text='move up',
                                     command=self.move_col_up,
                                     )
        
        self.move_down_button = Button(self,
                                     text='move down',
                                     command=self.move_col_down,
                                     )
        
        self.reset_col_button = Button(self,
                                       text='reset',
                                       command=self.reset_columns,
                                       )
        
        self.clear_col_button = Button(self,
                                       text='clear',
                                       command=self.clear_columns,
                                       )
        
        self.apply_columns_to_show_button = Button(self,
                                                   text='Apply Columns',
                                                   command=self.apply_columns_to_show,
                                                   )
        

        self.team_col_toshow = Combobox(self,
                                        values=['Players Database'] + list(self.parent.created_teams_dic.keys()),
                                        state='readonly',
                                        )
        self.team_col_toshow.current(0)

        self.label_columns_to_show.grid(row=0,
                                        column=0,
                                        padx=5,
                                        pady=5,
                                        )
        
        self.columns_to_show_combobox.grid(row=0,
                                        column=1,
                                        padx=5,
                                        pady=5,
                                        )
        
        self.add_column_button.grid(row=1,
                                    column=0,
                                    padx=5,
                                    pady=5,
                                    )
        
        self.remove_column_button.grid(row=1,
                                    column=1,
                                    padx=5,
                                    pady=5,
                                    )
        
        self.move_up_button.grid(row=2,
                                column=0,
                                padx=5,
                                pady=5,
                                )
        
        self.move_down_button.grid(row=2,
                                column=1,
                                padx=5,
                                pady=5,
                                )
        
        self.reset_col_button.grid(row=3,
                                column=0,
                                padx=5,
                                pady=5,
                                )
        
        self.clear_col_button.grid(row=3,
                                column=1,
                                padx=5,
                                pady=5,
                                )
        
        self.listbos_frame.grid(row=4,
                                column=0,
                                columnspan=2,
                                padx=5,
                                pady=5,
                                )
        
        self.apply_columns_to_show_button.grid(row=5,
                                               column=0,
                                               padx=5,
                                               pady=5,
                                               )
        
        self.team_col_toshow.grid(row=5,
                                   column=1,
                                   padx=5,
                                   pady=5,
                                  )

    def add_column_tolist(self):
        column_to_add = self.columns_to_show_combobox.get()
        list_values = [value.split('.', 1)[1].strip() for value in self.list_columns.get(0,END)]
        
        if len(column_to_add)>0 and column_to_add not in list_values:
            self.list_columns.insert(END, f'{self.list_columns.size()+1}. '+column_to_add)
        
        return

    def remove_column_fromlist(self):
        index_remove = self.list_columns.curselection()
        if index_remove:
            self.list_columns.delete(index_remove)
            self.update_numbers()
        
        return


    def move_col_up(self):
        selected_index = self.list_columns.curselection()
        if selected_index:
            index = selected_index[0]
            if index > 0:
                text = self.list_columns.get(index)
                self.list_columns.delete(index)
                self.list_columns.insert(index - 1, text)
                self.update_numbers()
                self.list_columns.selection_set(index - 1)

    def move_col_down(self):
        selected_index = self.list_columns.curselection()
        if selected_index:
            index = selected_index[0]
            if index < self.list_columns.size() - 1:
                text = self.list_columns.get(index)
                self.list_columns.delete(index)
                self.list_columns.insert(index + 1, text)
                self.update_numbers()
                self.list_columns.selection_set(index + 1)

    def reset_columns(self):
        self.clear_columns()
        for i, col in enumerate(self.parent.original_database_headers_to_show):
            self.list_columns.insert(i, f'{i+1}. ' + col)

    def clear_columns(self):
        self.list_columns.delete(0, END)

    def update_numbers(self):
        items = list(self.list_columns.get(0, END))
        self.list_columns.delete(0, END)
        for i, item in enumerate(items, start=1):
            self.list_columns.insert(END, f"{i}. {item.split('. ', 1)[1]}")
        
    def apply_columns_to_show(self):
        frame = self.team_col_toshow.get()
        if frame =='':
            return
        
        columns = [value.split('.', 1)[1].strip() for value in self.list_columns.get(0,END)]
        if frame == 'Players Database':
            self.parent.table_to_show_frame.columns_to_show = columns
            self.parent.table_to_show_frame.modify_display_columns()

        else:
            self.parent.created_teams_dic[frame].columns_to_show = columns
            self.parent.teams_selection_notebook.select(self.parent.created_teams_dic[frame])
            self.parent.update()
            self.parent.created_teams_dic[frame].modify_display_columns()


        return


#-----------------------------------------------------------------------------------------

class SelectPlayersToTeamsFrame(LabelFrame):

    def __init__(self, right_side_frame, parent):
        super().__init__(right_side_frame, 
                         text='Fill Teams with selected players')
        self.parent = parent
        
        #-----#---------Add Widgets---------------------------------------
        self.select_team_label = Label(self,
                                       text='Select Team:',
                                       )

        # create a selection button
        self.select_button = Button(self,
                                    text= 'Move Players to Team',
                                    command= self.get_selected_items,
                                    )
        
        # create a combobox with the created teams names as values
        self.created_teams_box = Combobox(self,
                                      values=list(self.parent.created_teams_dic.keys()),
                                      state='readonly',
                                      )
        
        self.select_team_label.grid(row=0,
                                    column=0,
                                    padx=5,
                                    pady=5,
                                    )

        self.created_teams_box.grid(row=0,
                                    column=1,
                                    padx=5,
                                    pady=5,
                                    )
        
        self.select_button.grid(row=1,
                                column=0,
                                columnspan=2,
                                padx=5,
                                pady=5,
                                )
        
    def get_selected_items(self):
        ''' returns a dataframe with the selected players
        '''
        # find the indices of the selected rows in the tree viw the 'text' key 
        indices = [int(self.parent.table_to_show_frame.tree.item(s_item)['text'])  for s_item in self.parent.table_to_show_frame.tree.selection()]
       
        # create a dataframe with the selected players
        selected_players_df = self.parent.table_to_show_frame.dataframe.iloc[indices]
        selected_players_df = selected_players_df.reset_index(drop=True)
        selected_players_df['index'] = selected_players_df.index+1

        # get the name of the team to place the players in 
        team_name = self.created_teams_box.get()

        # update the database in the selected team frame
        if team_name not in self.parent.created_teams_dic.keys():
            messagebox.showinfo('Select Team', 'Please select/create a team first!')
        else:
            self.parent.created_teams_dic[team_name].update_team_database(selected_players_df)

        return 
    

# -------------------------------------------------------------------------------------------------------------------------

class SideFrame3(LabelFrame):
    
    def __init__(self, side_frame,parent):
        super().__init__(side_frame)
        self.parent = parent

        self.update_database_button = Button(self,
                                        text='Create/Update Database',
                                        command= self.ask_question_update_database,
                                        )
        
        self.label_clubs_url = Label(self,
                                text="Enter Club's URL:")
        
        self.clubs_url = StringVar()
        self.entry_clubs_url = Combobox(self,
                                textvariable=self.clubs_url,
                                values= [self.parent.clubs_eso_players_url],
                                width=30,
                                )
        
        self.progress_bar = Progressbar(self,
                                       orient='horizontal',
                                       length=200,
                                       mode='determinate',
                                       )
        
        self.label_clubs_url.grid(row=0,
                             column=0,
                             padx=10,
                             pady=10,
                             )
        
        self.entry_clubs_url.grid(row=1,
                             column=0,
                             padx=10,
                             pady=10,
                             )
        
        self.update_database_button.grid(row=2, 
                                    column=0 , 
                                    padx= 10, 
                                    pady= 10,
                                    )
        
        self.progress_bar.grid(row=3,
                               column=0,
                               padx=10,
                               pady=10,
                               )
        
    def ask_question_update_database(self):
        users_club_url = self.clubs_url.get()

        if len(users_club_url)>0:
            try:
                responce = requests.get(users_club_url)
                print('connection established')
                # new_club = FetchPlayersDatabase(users_club_url)
                # new_club.fetch_eso_players
                self.parent.clubs_eso_players_url = users_club_url
                print("Club's url is valid and ready for fetching")
            except:
                print('New Url not correct, will procceed with the default URL')

        answer_update_datavase = messagebox.askquestion(title='Update Database', 
                                                        message=f'All current teams will be arased, page will automatically reload after finishing. Update Database?',
                                                        detail = '(requires internet connection, may take a few seconds)',
                                                        )

        if answer_update_datavase == 'yes':
            # start moving the progressive bar on a seperate thread until database is updated
            threading.Thread(target=self.waiting_logo).start()

            # # update the database on a seperate thread
            threading.Thread(target=self.parent.update_database).start()

        return
    
    def waiting_logo(self):
        # update the whole in 20 sec, run it twice for 40 sec; updating database last roughly 15 sec
        for i in range(0,200, 5):
            self.progress_bar['value'] = i %100
            self.parent.update_idletasks()
            time.sleep(1)
        
        self.progress_bar['value'] = 0
        self.parent.update_idletasks()