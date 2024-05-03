from tkinter import Frame
from tkinter import *
from tkinter.ttk import Combobox
from tkinter.ttk import *
import re

class SideFrame1(Frame):

    def __init__(self, side_frame, parent):
        super().__init__(side_frame)
        
        # get the parent
        self.parent = parent

        #---------------------Add Widgets---------------------------------------------------

        # 0 set header
        self.label_header = Label(self, text="Configure Player's List", font= ('Arial', 16))
        self.label_header.grid(row = 0, column = 0, columnspan= 2 , pady=10 )
        
        # list all label and value restricitons

        self.restrictions_labels = []
        self.restrictions_values = []

        # 1 choose elo type
        self.label_elo_type = Label(self, 
                                    text='elo type:',
                                    )
        self.restrictions_labels.append(self.label_elo_type)

        self.choose_elo_type = Combobox(self,  
                                        values=['National Elo', 'std', 'rapid', 'blitz'], 
                                        state = "readonly",
                                        )
        self.restrictions_values.append(self.choose_elo_type)
        
        # 2 min elo range
        self.min_elo_range_label = Label(self, 
                                         text='min elo:',
                                         )
        self.restrictions_labels.append(self.min_elo_range_label)

        self.min_elo_scale = Combobox(self, 
                                      values=['None', 0,800] + [i for i in range(1000,2100,100)],
                                      state = "readonly",
                                      )
        self.restrictions_values.append(self.min_elo_scale)
        
        # 3 max elo range
        self.max_elo_range_label = Label(self, 
                                         text='max elo:',
                                         )
        self.restrictions_labels.append(self.max_elo_range_label)

        self.max_elo_scale = Combobox(self,
                                      values= ['None', 0,800] + [i for i in range(1000,2900,100)],
                                      state = "readonly"
                                      )
        self.restrictions_values.append(self.max_elo_scale)

        # 4 min age
        self.min_label_age = Label(self, 
                                   text='Min Age:',
                                   )
        self.restrictions_labels.append(self.min_label_age) 

        self.min_age_scale = Combobox(self, 
                                      values= ['None', 0] + [i for i in range(4,22,2)] + [30,40,50,60,65],
                                      state = "readonly",
                                      )
        self.restrictions_values.append(self.min_age_scale)

        # 5 max age
        self.max_label_age = Label(self,
                                   text='Max Age:',
                                   )
        self.restrictions_labels.append(self.max_label_age)

        self.max_age_scale = Combobox(self, 
                                      values=['None', 0] + [i for i in range(4,22,2)] + [30,40,50,60,65,100], 
                                      state = "readonly"
                                      )
        self.restrictions_values.append(self.max_age_scale)

        # 6 gender 
        self.label_gender = Label(self, 
                                  text= 'Gender:',
                                  )
        self.restrictions_labels.append(self.label_gender)

        self.choose_gender = Combobox(self,  
                                      values=['All', 'M', 'F'],
                                      state = "readonly"
                                      )
        self.restrictions_values.append(self.choose_gender) 

        # 7 fide active
        self.label_fide_active = Label(self, 
                                       text = 'Active Players',
                                       )
        self.restrictions_labels.append(self.label_fide_active)

        self.choose_fide_active = Combobox(self, 
                                           values=['All', 'Yes', 'No'], 
                                           state = "readonly",
                                           )
        self.restrictions_values.append(self.choose_fide_active)

        # 8 eso fee active
        self.eso_fee_active = Label(self, 
                                    text = 'Eso fee paid',
                                    )
        self.restrictions_labels.append(self.eso_fee_active)

        self.eso_fee_active = Combobox(self, 
                                       values=['All', 'Yes', 'No'], 
                                       state = "readonly",
                                       )
        self.restrictions_values.append(self.eso_fee_active)
        
        # add all restrictions labels and values to the frame
        for i, label in enumerate(self.restrictions_labels):
            label.grid(row=i+1, column=0, padx=5, pady=5, sticky="e")

        for i, choose_value in enumerate(self.restrictions_values):
            choose_value.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")
            choose_value.current(0)
        
        # get the next row number to place any more widgets
        row_number_after_restrictions = len(self.restrictions_labels)+1

        # 9 search by name input
        self.seearch_name_label = Label(self, 
                                        text='Search by name:',
                                        )
        self.restrictions_labels.append(self.seearch_name_label)

        self.search_name_entry = Entry(self, 
                                       )
        self.restrictions_values.append(self.search_name_entry)

        self.seearch_name_label.grid(row=row_number_after_restrictions, column=0, padx=5, pady=5, sticky="e")
        self.search_name_entry.grid(row=row_number_after_restrictions, column=1, padx=5, pady=5, sticky="w")


        # 10 apply restrictions button
        self.apply_restrictions_button = Button(self, 
                                                text='Apply', 
                                                command = self.update_table_to_show_frame,
                                                )
        self.apply_restrictions_button.grid(row=row_number_after_restrictions +1, column=0, padx=5, pady=5, sticky='e')

        # 10 clear restrictions button 
        self.clear_restirctions_button = Button(self, 
                                                text='Clear', 
                                                command = self.clear_restrictions,
                                                )
        self.clear_restirctions_button.grid(row=row_number_after_restrictions+1, column=1, padx=5, pady=5, sticky="w")


        #------------------------------------------Methods-------------------------------------------------

    def clear_restrictions(self):
        # comboboxes
        for combox in self.restrictions_values[:-1]:
            combox.current(0)
        # entry
        self.search_name_entry.delete(0, END)
        self.update_table_to_show_frame()


    def get_restrictions(self):
        all_entries = [entry.get() for entry in self.restrictions_values]
        return all_entries
            

    def apply_restrictions_to_restricted_database(self):
        ''' Modify the parent.restricted database by applyin the restrictions to the original database
        '''
        restrictions = []
        elo_type , elo_min, elo_max , age_min, age_max, gender, fide_active, eso_fee, name_search = self.get_restrictions()
        

        if elo_min.isdecimal():
            elo_min = int(elo_min)
            elo_restriction = (self.parent.original_database[elo_type] >= elo_min)
            restrictions.append(elo_restriction)

        if elo_max.isdecimal():
            elo_max = int(elo_max)
            elo_restriction = (self.parent.original_database[elo_type] <= elo_max) 
            restrictions.append(elo_restriction)
        
        if age_min.isdecimal():
            age_min = int(age_min)
            age_restriction =  (self.parent.original_database['Age']>=age_min ) 
            restrictions.append(age_restriction)

        if age_max.isdecimal():
            age_max = int(age_max)
            age_restriction =  (self.parent.original_database['Age']<=age_max ) 
            restrictions.append(age_restriction)
    
        if gender!= 'All' and gender in 'MF':
            gender_restriction = self.parent.original_database['Gender'] == gender
            restrictions.append(gender_restriction)
    
        if fide_active!= 'All' and fide_active in ['Yes', 'No']:
            fide_active = True if fide_active == 'Yes' else False
            fide_active_restriction =  self.parent.original_database['Fide Active'] == fide_active
            restrictions.append(fide_active_restriction)

        if eso_fee != 'All' and eso_fee in ['Yes', 'No']:
            eso_fee = 'OK' if eso_fee == 'Yes' else '0' 
            eso_fee_restriction = self.parent.original_database['Eso Fee'] == eso_fee
            restrictions.append(eso_fee_restriction)

        if len(name_search) > 0:
            # if the user enters a string return all matches and ignore the other restrictions
            
            # search for the national name match; only upper letters here
            row_index_match_national = [i for i in self.parent.original_database['National Name'].index if re.search(name_search.upper(), self.parent.original_database['National Name'][i])]
            # search for the Fide name match; 
            
            row_index_match_fide = [i for i in self.parent.original_database['Fide Name'].index if re.search(' '.join([word[0].upper()+ word[1:].lower() for word in name_search.split()]), self.parent.original_database['Fide Name'][i])]
            self.parent.table_to_show_frame.dataframe = self.parent.original_database.iloc[row_index_match_national+row_index_match_fide]

            return 

        if len(restrictions) == 0:
            self.parent.table_to_show_frame.dataframe =  self.parent.original_database#.sort_values(by=[elo_type], ascending= False)
            return
    
        # continue if there are some restrictions to apply
        all_restrictions = restrictions[0]

        # combine all restrictions with the logical and operator &
        # I haven't found a way to do that by a built in function
        for res in restrictions:
            all_restrictions = all_restrictions & res    

        self.parent.table_to_show_frame.dataframe = self.parent.original_database[all_restrictions]#.sort_values(by=[elo_type], ascending= False)
        
        return


    def update_table_to_show_frame(self):
        # aplly restrictions to the restricted database
        self.apply_restrictions_to_restricted_database()

        # reset columns to show
        self.parent.table_to_show_frame.columns_to_show =  list(self.parent.original_database_headers_to_show).copy()

        # update the tree in the table frame
        # self.parent.table_to_show_frame.display_dataframe()

        self.parent.table_to_show_frame.add_rows()

#---------------------------------------------------------------------------------------------------------------


class SideFrame2(Frame):
    
    def __init__(self, side_frame, parent):
        super().__init__(side_frame)
        self.parent = parent
        
        #create an attribute to store all team entries
        self.new_teams_entries_labels = []
        self.new_teams_entries= []

         # set header
        self.label_header = Label(self, 
                                  text="Create New Team", 
                                  font= ('Arial', 16),
                                  )
        self.label_header.grid(row = 0, column = 0, columnspan= 2 , pady=10 )

        # Team's name
        
        self.team_name_label = Label(self, 
                                     text="Team's Name:",
                                     )
        self.new_teams_entries_labels.append(self.team_name_label)

        self.team_name_entry = Entry(self, )
        self.new_teams_entries.append(self.team_name_entry)

        # opponent team's name
        self.opponent_team_name_label = Label(self, 
                                              text="Opp. Team's Name:",
                                              )
        self.new_teams_entries_labels.append(self.opponent_team_name_label)

        self.opponent_team_name_entry = Entry(self, )
        self.new_teams_entries.append(self.opponent_team_name_entry)

        # Tournament
        self.tournament_name = Label(self, 
                                    text="Tournament:",
                                    )
        self.new_teams_entries_labels.append(self.tournament_name)

        self.tournament_name_entry = Entry(self, )
        self.new_teams_entries.append(self.tournament_name_entry)
        
        # Date of the match
        
        self.date_of_match = Label(self, 
                                   text="Match Date:",
                                  )
        self.new_teams_entries_labels.append(self.date_of_match)

        self.date_of_match_entry = Entry(self, )
        self.new_teams_entries.append(self.date_of_match_entry)

        # Address

        self.adrress_label = Label(self,
                                     text='Address:',
                                     )
        self.new_teams_entries_labels.append(self.adrress_label)

        self.adrress_entry = Entry(self,)
        self.new_teams_entries.append(self.adrress_entry)

        # round
        self.round_label = Label(self,
                                     text='Round:',
                                     )
        self.new_teams_entries_labels.append(self.round_label)

        self.round_entry = Entry(self,)
        self.new_teams_entries.append(self.round_entry)

        # Home court
        self.home_court_label = Label(self, 
                                      text="Home Court:",
                                      )
        self.new_teams_entries_labels.append(self.home_court_label)

        self.home_court_entry = Combobox(self,
                                         values=['Yes','No'],
                                         state='readonly',
                                         width=5
                                         )
        self.new_teams_entries.append(self.home_court_entry)
        self.home_court_entry.current(0)

        # Number of Boards
        self.number_of_players_label = Label(self, 
                                             text="Number of Boards:",
                                             )
        self.new_teams_entries_labels.append(self.number_of_players_label)

        self.number_of_players_entry = Combobox(self, 
                                                values=[3,4,6,8,10,12],
                                                state='readonly',
                                                width=5
                                                )
        self.new_teams_entries.append(self.number_of_players_entry)
        self.number_of_players_entry.current(1)
        
        for i,label in enumerate(self.new_teams_entries_labels):
            label.grid(row=i+1,
                        column=0, 
                        padx=5, 
                        pady=5, 
                        sticky="e",
                        )
        for i,entry in enumerate(self.new_teams_entries):
            entry.grid(row=i+1,
                        column=1, 
                        padx=5, 
                        pady=5, 
                        sticky="w",
                        )
        
        row_number_after_entries = len(self.new_teams_entries)+1

        # create new team button 
        self.create_team_button = Button(self, 
                                         text='create',
                                         command= self.parent.create_new_team,
                                         )
        self.create_team_button.grid(row=row_number_after_entries, 
                                     column=0, 
                                     padx=5, 
                                     pady=5, 
                                     sticky="e",
                                     )

        # clear button
        self.clear_new_team_button = Button(self,
                                     text='clear',
                                     command=self.clear_new_team,
                                     )
        self.clear_new_team_button.grid(row=row_number_after_entries,
                                        column=1,
                                        padx=5, 
                                        pady=5, 
                                        sticky="w",
                                        )
    
    def clear_new_team(self):
        self.team_name_entry.delete(0, END)
        self.opponent_team_name_entry.delete(0, END)
        self.date_of_match_entry.delete(0, END)
        self.tournament_name_entry.delete(0, END)
        self.adrress_entry.delete(0, END)
        self.round_entry.delete(0, END)
        self.home_court_entry.current(0)
        self.number_of_players_entry.current(1)
        
        return


    def get_teams_info(self):
        '''returns a dictionary with keys the text of the labels
         and values the current entries in the coresponding entries
         '''

        return {label.cget('text'):entry.get() for label, entry in zip(self.new_teams_entries_labels, self.new_teams_entries) }


# -------------------------------------------------------------------------------------------------------------------------
