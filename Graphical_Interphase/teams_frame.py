from tkinter.ttk import Treeview, Button, Entry, Label, Frame, Style, Scrollbar, Style
from tkinter.font import Font
from tkinter import messagebox

import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import threading

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TeamsCreation(Frame):

    def __init__(self, parent, notebook, new_team_info_dic):
        super().__init__(notebook)
        self.parent = parent
               
        # 
        self.all_headers = self.parent.original_database_all_headers
        self.columns_to_show = self.parent.original_database_headers_to_show.copy()

        # create this team's dataframe to add players to it
        empty_dic = {col:[] for col in list(self.all_headers)}
        self.team_dataframe = pd.DataFrame(empty_dic)
        
        # set two attributes to control when a column is clicked to sort it 
        self.sort_column = None
        self.sort_direction = None

        # ---------------------------------set the labels for the match -------------------------------- 
        self.game_label = Label(self, 
                    #   text=self.game_title,
                      font=('Arial', 14),
                      )

        self.tournmanet_label = Label(self,
                                    #   text=f'Tournament: {self.tournmanet}' ,
                                    #   font=('Arial', 12),
                                      )
        
        self.boards_label = Label(self,
                                #   text=f'Boards: {self.number_boards}',
                                  )
        
        self.round_label = Label(self,
                                #  text=f'Round: {self.round}',
                                #  font=('Arial', 12),
                                 )
        

        self.date_label = Label(self,
                                # text=f'Date: {self.match_date}',
                                # font=('Arial', 12),
                                )  
        
        self.adrress_label = Label(self,
                                #    text=f'Address: {self.adrress}'
                                )
        
        self.additional_info_label = Label(self,
                                    #  text='Additional info:',
                                     )
        self.additional_info_entry = Entry(self,
                                           width=40,
                                           )
        
        # update the content of the labels
        self.update_match_info(new_team_info_dic)
        
        self.game_label.grid(row=0,
                               column=0,
                               columnspan=5,
                               padx=2,
                               pady=2,
                               )

        self.tournmanet_label.grid(row=1,
                                   column=0,
                                   padx=2,
                                   pady=2,
                                   sticky = 'w'
                                   )
        
        self.boards_label.grid(row=1,
                               column=1,
                               padx=2,
                               pady=2,
                            #    sticky = 'w'
                               )

        self.round_label.grid(row=1,
                              column=2,
                              padx=2,
                              pady=2,
                              sticky = 'w'
                              )
        
        self.date_label.grid(row=1,
                             column=3,
                             padx=2,
                             pady=2,
                             sticky = 'w'
                             )
        
        self.adrress_label.grid(row=2,
                                column=0,
                                columnspan=2,
                                padx=2,
                                pady=2,
                                sticky = 'w'
                                )
        
        self.additional_info_label.grid(row=2,
                                        column=2,
                                        padx=2,
                                        pady=2,
                                        sticky = 'w'
                                        )
        
        self.additional_info_entry.grid(row=2,
                                        column=3,
                                        columnspan=2,
                                        padx=2,
                                        pady=2,
                                        sticky = 'w'
                                        )
        
        # --------------------------------Configure the Tree initially ------------------------------------
        self.tree = Treeview(self,
                            columns= self.all_headers,
                            show="headings",
                            # displaycolumns= self.columns_to_show, # choose which columns to display
                            height= 10, # number of rows to display at a time
                            )

         # set the total default width of the tree
        self.tree_width = self.parent.tree_width
        
        # set all the headers and columns for the tree
        n = len(self.all_headers)
        for col in self.all_headers:

            self.tree.column(col,
                             anchor= 'center',
                             stretch=False,
                             width=self.tree_width//n
                            )

            self.tree.heading(col, 
                              text=col,
                              anchor='center',
                              command= lambda c=col: self.sort_by_column(c), # command to call when the haeding is clicked
                              )
        
        self.style = Style()
        self.style.configure('Treeview.Heading',
                            font=('Arial', 10, 'bold'),
                            background = 'green',
                            )
        
        self.tree.bind(f'<Double-1>', lambda event: self.open_url(event))
        self.tree.bind('<Motion>', lambda event: self.enter_fide_id_col(event))
        
        # Add vertical scrollbar 
        self.v_scrollbar = Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand = self.v_scrollbar.set)

        # Add horizontal scrollbar
        self.h_scrollbar = Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
        
        # add the tree and the scrollbars to the frame
        self.tree.grid(row=3,
                  column=0,
                  columnspan=5,
                #   sticky='we',
                #   padx=5,
                #   pady=5,
                  )
        self.v_scrollbar.grid(row=3,
                              column=5,
                              sticky='ns'
                              )
        self.h_scrollbar.grid(row=4,
                              column=0,
                              columnspan=5,
                              sticky='ew',
                              )

        #----------------------------------Add Buttons to take actions on the tree and the team-frame----------------
        self.remove_team_button= Button(self,
                                   text='Remove Team',
                                   command= self.remove_team,
                                   )
        
        self.remove_team_button.grid(row=5,
                                column=0,
                                padx=5,
                                pady=5,
                                sticky='w',
                                )
        
        self.remove_player_button = Button(self,
                                           text='Remove Selected Players',
                                           command=self.remove_player
                                          )
        self.remove_player_button.grid(row=5,
                                       column=1,
                                       padx=5,
                                       pady=5,
                                       sticky='w',
                                       )
        
        self.move_player_up_button = Button(self,
                                              text='Move Player Up',
                                              command=self.move_player_up
                                              )
        
        self.move_player_up_button.grid(row=5,
                                       column=2,
                                       padx=5,
                                       pady=5,
                                       sticky='w',
                                       )
        
        self.move_player_down_button = Button(self,
                                              text='Move Player Down',
                                              command= self.move_player_down,
                                              )
        
        self.move_player_down_button.grid(row=5,
                                       column=3,
                                       padx=5,
                                       pady=5,
                                       sticky='w',
                                       )
        
        self.export_to_pdf_button = Button(self,
                                           text = 'export to pdf',
                                           command= lambda x=self.export_to_pdf : threading.Thread(target=x).start()
                                           )
        
        self.export_to_pdf_button.grid(row=5,
                                       column=4,
                                       padx=5,
                                       pady=5,
                                       sticky='w')
    
    #-----------------------------------------------------------------------------------------------------
    def update_match_info(self, new_team_info_dic):
        '''Update the content of the info labels for the match to those in the team's info dictionary.
        '''
        
        self.team_name = new_team_info_dic["Team's Name:"]
        self.opponent_team_name = new_team_info_dic["Opp. Team's Name:"]
        self.tournmanet = new_team_info_dic['Tournament:']
        self.match_date = new_team_info_dic['Match Date:']
        self.adrress = new_team_info_dic['Address:']
        self.round = new_team_info_dic['Round:']
        self.home_court = new_team_info_dic['Home Court:']
        self.number_boards = int(new_team_info_dic['Number of Boards:'])

        if self.home_court == 'Yes':
            self.game_title = self.team_name +' - '+ self.opponent_team_name
        else:
            self.game_title = self.opponent_team_name +' - ' + self.team_name

        self.game_label.configure(
                      text=self.game_title,
                      font=('Arial', 14),
                      )

        self.tournmanet_label.configure(text=f'Tournament: {self.tournmanet}')
        
        self.boards_label.configure(text=f'Boards: {self.number_boards}')
        
        self.round_label.configure(text=f'Round: {self.round}')

        self.date_label.configure(text=f'Date: {self.match_date}')  
        
        self.adrress_label.configure(text=f'Address: {self.adrress}')
        
        self.additional_info_label.configure(text='Additional info:')
        
        # check if the teams_database has more players than the newly set number of boards 
        difference = len(self.team_dataframe) - self.number_boards
        if difference>0:
            # check if the difference is one or more players to adjust the message
            if difference == 1:
                mes = f'You set the number of boards to {self.number_boards}. Please remove {difference} player'
            else:
                mes = f'You set the number of boards to {self.number_boards}. Please remove {difference} players'
            messagebox.showwarning(title='Number of Boards',
                                   message= mes,
                                   )
            
    def modify_display_columns(self):
        ''' Change the columns that are presents in the Treeview, without changing the tree width.
        '''
        # check if there is a database
        if len(self.parent.original_database) == 0:
            return
        
        n = len(self.columns_to_show)
        if n == 0:
            return
        
        # set the total width of the columns to show equal to the fixed width of the tree
        for col in self.columns_to_show:
            self.tree.column(col,
                             width=self.tree_width//n)
        
        # update the tree to fix its width
        self.tree.configure(displaycolumns=self.columns_to_show)
        
        # find and store the appropriate width of each column
        col_max_widths = {}
        # change the width of the columns to their appropreate size, but not the width of the tree
        for col in self.columns_to_show:

            # find the appropriate width for each column; only search for the maximum name
            if self.team_dataframe[col].count() == 0:
                max_width_column = Font().measure(col) + 8
            elif col == 'National Name':
                max_len_pos = self.team_dataframe[col].astype(str).apply(lambda x: len(x)).argmax()
                max_width_column = max(Font().measure(self.team_dataframe[col].iloc[max_len_pos]), Font().measure(col)) 
                max_width_column = int(max_width_column*0.8)
            elif col == 'Fide Name':
                max_len_pos = self.team_dataframe[col].astype(str).apply(lambda x: len(x)).argmax()
                max_width_column = max(Font().measure(self.team_dataframe[col].iloc[max_len_pos]), Font().measure(col))
                max_width_column = int(max_width_column*0.8)
            else:
                max_width_column = Font().measure(col) + 12
            
            col_max_widths[col] = max_width_column


        # check if the sum of the width exides the width of the tree; in that case allocate the remaining pixels equally to each column
        s = sum(list(col_max_widths.values()))
        width_diff_aver = max((self.tree_width - s)//n , 0) 
        
        for col in self.columns_to_show:
            min_width_column = col_max_widths[col]//2
            self.tree.column(col,
                             anchor= 'center',
                             stretch=False,
                             width= col_max_widths[col] + width_diff_aver,
                             minwidth= min_width_column
                            )
            
        # add the rows since initially the team_dataframe is empty
        self.add_rows()
    
    def add_rows(self):
        '''Clears the existing rows in the treeview 
        and insert the current rows in the database to the treeview.
        '''
        self.team_dataframe = self.team_dataframe.reset_index(drop=True)
        # Clear existing items in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add data to the treeview
        for i, row in self.team_dataframe.iterrows():
            text, url = self.extract_info(row['Fide ID'])
            row['Fide ID'] = text
            if i % 2 == 0:
                self.tree.insert("", "end", text=i, values=list(row), tags=("even_row",))
            else:
                self.tree.insert("", "end", text=i, values=list(row))
        
        self.tree.tag_configure("even_row", background="lightblue")

    def extract_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        url = soup.a['href']
        return text, url
    
    def open_url(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_name = self.tree.column(col, option="id")
   
        if row !='' and col_name == 'Fide ID':
            row_n = int(self.tree.item(row)['text'])
            html_tag = self.team_dataframe.loc[row_n, col_name]
            _ , url = self.extract_info(html_tag)
            webbrowser.open_new(url)

    def enter_fide_id_col(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_name = self.tree.column(col, option="id")
        if row !='' and col_name == 'Fide ID':
            self.tree.config(cursor='hand2')
        else:
            self.tree.configure(cursor='')

    def remove_player(self):
        '''Removes the selected players from the team_dataframe
        '''
        # find the index of the selected players; note that the index column starts at 1 not 0; subtract 1
        indices_to_remove = [self.tree.item(item_remove)['values'][0]-1 for item_remove in self.tree.selection()] 
        
        # remove the row with the selected index, reset the index, start it at 1
        self.team_dataframe = self.team_dataframe.drop(indices_to_remove).reset_index(drop=True)
        self.team_dataframe['index'] = self.team_dataframe.index+1
        self.add_rows()

        return

    def move_player_up(self):
        '''Moves the seleced player one position up
        '''

        if len(self.tree.selection()) == 1:
            # get the selected player
            selected_item = self.tree.selection()[0]
            # note the row index is the 'index'-column value -1
            ind = self.tree.item(selected_item)['values'][0]-1   
            if ind > 0 :
                # reverse the current and the previous row
                self.team_dataframe.iloc[[ind-1,ind]] = self.team_dataframe.iloc[[ind, ind-1]].values
                self.team_dataframe.reset_index(drop=True)
                self.team_dataframe['index'] = self.team_dataframe.index+1
                self.add_rows()
                # set the selection on the tree to the same row-player that was just moved up
                self.tree.selection_set(self.tree.get_children()[ind-1])
        else:
            messagebox.showinfo('Move Player', 'Please select one player to move up or down')
    
    def move_player_down(self):
        '''Moves the seleced player one position up
        '''

        if len(self.tree.selection()) == 1:
            ind = self.tree.item(self.tree.selection()[0])['values'][0]-1
            if ind < len(self.team_dataframe) -1:
                self.team_dataframe.iloc[[ind+1,ind]] = self.team_dataframe.iloc[[ind, ind+1]].values
                self.team_dataframe.reset_index(drop=True)
                self.team_dataframe['index'] = self.team_dataframe.index+1
                self.add_rows()
                # set the selection on the tree to the same row-player that was just moved up
                self.tree.selection_set(self.tree.get_children()[ind+1])
        else:
            messagebox.showinfo('Move Player', 'Please select one player to move up or down')

    
    def update_team_database(self, new_database_to_add):
        '''Adds the players in the dataframe new_database_to_add to the teams_dataframs.
        Checks if the total number of players excided the number of boards and terminates the process,
        if a player already exists on that team and terminates the process,
        and if a player is on another team which is allowed.
        '''
        
        if len(self.team_dataframe)+len(new_database_to_add)> self.number_boards:
            messagebox.showinfo('Number of Boards', 'You excided the number of boards for that team')
            return
        
        # check if some player is already on the current team; players will not be placed on the team
        new_players = list(new_database_to_add['National Name'])
        for new_player in new_players:
            if new_player in list(self.team_dataframe['National Name']):
                messagebox.showwarning(title='Plyer Already on Team', message=f'{new_player} is already on the team {self.team_name}')
                return
            
        # check if one or more of the selected players are already on another team; but allow the user to do that
        team_plyers_selected = []
        for team_frame in self.parent.created_teams_dic.values():
            team_plyers_selected += list(team_frame.team_dataframe['National Name'])

        for new_player in new_players:
            if new_player in team_plyers_selected:
                answer = messagebox.askquestion('Player on two teams', f'{new_player} is also on another team, procced?')
                if answer == 'no':
                    return
        
        # add the new players to the teams dataframe
        if self.team_dataframe.empty:
            self.team_dataframe = new_database_to_add
        else: 
            self.team_dataframe = pd.concat([self.team_dataframe, new_database_to_add], ignore_index=True)
        
        self.team_dataframe['index'] = self.team_dataframe.index+1
        
        # move to the tab of the selected team
        # 14/5/24 maybe I can simple add the rows
        self.parent.teams_selection_notebook.select(self)
        self.parent.update()
        self.modify_display_columns()

        return

    def remove_team(self):
        '''remove the team's frame, both from the notebook and from the parent.teams_frame_dic
        '''

        # ask the user for permission to remove the team
        answer = messagebox.askyesno('Remove Team', f'Do you want to remove the team {self.team_name}?')
        if answer == True:
            # remove frame from the notebook 
            self.parent.teams_selection_notebook.forget(self)

            # remove key-value, team_name : frame, from the dictionary 
            _ = self.parent.created_teams_dic.pop(self.team_name)

            # update the combobox list of values
            self.parent.select_player_to_teams_frame.created_teams_box.set('')
            self.parent.select_player_to_teams_frame.created_teams_box['values'] = list(self.parent.created_teams_dic.keys())
             # and the values in the comobox in columns to select frame
            self.parent.configure_table_columns_frame.team_col_toshow['values'] = ['Players Database'] + list(self.parent.created_teams_dic.keys())
            self.parent.configure_table_columns_frame.team_col_toshow.current(0)

        return
    
    def export_to_pdf(self):
        '''Creates a pdf with the match info in the cwd
        '''
        
        # make the necessary modifications to the database
        database_to_print = self.team_dataframe[self.columns_to_show]
        # set or reset the index column from 1 to the number of boards
        database_to_print['index'] = pd.Series([i for i in range(1, len(database_to_print)+1)])

        # set the Fide Id column to only the id text value
        if 'Fide ID' in database_to_print.columns:
            database_to_print['Fide ID'] = database_to_print['Fide ID'].map(lambda x: self.extract_info(x)[0] )
        
        doc = SimpleDocTemplate(f'{self.team_name}.pdf', pagesize=letter)
        styles = getSampleStyleSheet()

        game_info_style = ParagraphStyle(name='Normal',
                                        # fontName='Helvetica',
                                        fontSize=10,
                                        leading=14,
                                        )

        title = Paragraph(f'Team Composition of {self.team_name}', styles['Title'])
        
        match_name = Paragraph(f'Match: {self.game_title}', styles['Title'])
        
        game_info_1_str = f'Tournament: {self.tournmanet},   round: {self.round},   date: {self.match_date}'
        game_info_1 = Paragraph(game_info_1_str, game_info_style)

        game_info_2_str = f'Adrress: {self.adrress}'
        game_info_2 = Paragraph(game_info_2_str, game_info_style)

        game_info_3_str = f'Additional Info: {self.additional_info_entry.get()}'
        game_info_3 = Paragraph(game_info_3_str, game_info_style)

        # creating the table
        data = [database_to_print.columns.tolist()] + database_to_print.values.tolist()

        table = Table(data)

        table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                              ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                              ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(table_style)

        captain_str = "Team's Captain:"
        captain = Paragraph(captain_str, game_info_style)
        
        pdf_elements_list = [title,
                            Spacer(0,10),
                            match_name,
                            Spacer(0,10),
                            game_info_1,
                            Spacer(0,10),
                            game_info_2,
                            Spacer(0,10),
                            game_info_3,
                            Spacer(0,20),
                            table,
                            Spacer(0,20),
                            captain,
                            ]

        doc.build(pdf_elements_list)

    def sort_by_column(self, column):
        '''Sorts the database wrt to the clicked column and then calls the add_rows()
        '''

        if self.sort_column == column:
            self.sort_direction = not self.sort_direction
        else:
            self.sort_column = column
            self.sort_direction = True

        # sort the dataframe wrt the clicked column, reset the index but do not add the previous index to a new column
        self.team_dataframe = self.team_dataframe.sort_values(by=column, ascending= self.sort_direction).reset_index(drop =True)
        
        self.team_dataframe.reset_index(drop=True)
        self.team_dataframe['index'] = self.team_dataframe.index+1
        
        self.add_rows()
