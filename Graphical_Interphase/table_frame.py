from tkinter import *
from tkinter.ttk import Treeview
from tkinter.ttk import *
from tkinter.font import Font
from bs4 import BeautifulSoup
import webbrowser

class RestrictedPlayersDatabaseFrame(LabelFrame):

    def __init__(self, parent):

        super().__init__(parent, 
                         text= f'{parent.team_name} Players Databse,  Total Players: {parent.number_of_players},  Last Updated: {parent.database_date_modified} {parent.database_time_modified}',
                         )
        
        self.parent = parent

        # create a copy of the restricted database so we can sorted without affecting the users restrcions
        self.dataframe = self.parent.original_database.copy()

        # set two attributes to control when a column is clicked to sort it
        # self.sort_column stores the column name that is being clicked
        # self.sort_direction will be True or False and reverses the direction of the sorting of that column if it is clicked twice 
        self.sort_column = None
        self.sort_direction = None
        
        self.columns_to_show = self.parent.original_database_headers_to_show.copy()
        self.all_headers = self.parent.original_database_all_headers

        self.tree = Treeview(self, 
                        columns=self.all_headers,
                        show="headings",
                        # displaycolumns= self.columns_to_show, # choose which columns to display
                        height= 13, # number of rows to display at a time
                        )
        
        # set the total default width of the tree
        self.tree_width = self.parent.tree_width
        
        # set all the headers and columns for the tree and initiallize the tree width
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
                             )
        
        # initially add all the rows in the database to the tree
        self.add_rows()

        # bind the tree to double click to open the fide url of the player; change the cursor to hand above Fide ID column
        self.tree.bind(f'<Double-1>', lambda event: self.open_url(event))
        self.tree.bind('<Motion>', lambda event: self.enter_fide_id_col(event))

        # Add vertical scrollbar 
        self.v_scrollbar = Scrollbar(self, 
                                     orient="vertical", 
                                     command=self.tree.yview,
                                     )
        self.tree.configure(yscrollcommand = self.v_scrollbar.set)

        # Add horizontal scrollbar
        self.h_scrollbar = Scrollbar(self, 
                                     orient="horizontal", 
                                     command=self.tree.xview,
                                     )
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
        
         # grid the treeview and scrollbars to the frame
        self.tree.grid(row=0,
                       column=0,
                       )
        self.v_scrollbar.grid(row=0,
                              column=1,
                              sticky='ns'
                              )
        self.h_scrollbar.grid(row=1,
                              column=0,
                              sticky='ew',
                              )

    def add_rows(self):
        self.dataframe = self.dataframe.reset_index(drop=True)
        # Clear existing items in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add data to the treeview
        for i, row in self.dataframe.iterrows():
            text, url = self.extract_info(row['Fide ID'])
            row['Fide ID'] = text
            if i % 2 == 0:
                self.tree.insert("", "end", text=i, values=list(row), tags=("even_row",))
            else:
                self.tree.insert("", "end", text=i, values=list(row))
        
        self.tree.tag_configure("even_row", background="lightblue")

    def modify_display_columns(self):

        # check if there is a database
        if len(self.dataframe) == 0:
            return
        
        n = len(self.columns_to_show)
        # if no columns are selected for display do nothing
        if n == 0:
            return

        # set the total width of the displayed columns equal to the fixed width of the tree
        for col in self.columns_to_show:
            self.tree.column(col,
                             width=self.tree_width//n)
        
        # update the tree to fix its width to the current displayed columns
        self.tree.configure(displaycolumns=self.columns_to_show)

        col_max_widths = {}
        # change the width of the columns to their appropreate size, but not the width of the tree
        for col in self.columns_to_show:

            # find the appropriate width for each column; only search for the maximum name
            if self.dataframe[col].count() == 0:
                max_width_column = Font().measure(col) + 8
            elif col == 'National Name':
                max_len_pos = self.dataframe[col].astype(str).apply(lambda x: len(x)).argmax()
                max_width_column = max(Font().measure(self.dataframe[col].iloc[max_len_pos]), Font().measure(col)) 
                max_width_column = int(max_width_column*0.8)
            elif col == 'Fide Name':
                max_len_pos = self.dataframe[col].astype(str).apply(lambda x: len(x)).argmax()
                max_width_column = max(Font().measure(self.dataframe[col].iloc[max_len_pos]), Font().measure(col))
                max_width_column = int(max_width_column*0.8)
            else:
                max_width_column = Font().measure(col) + 12

            col_max_widths[col] = max_width_column
        
        # check if the sum of the width exides the width of the tree; in that case allocate the remaining pixels equally to each column
        s = sum(list(col_max_widths.values()))
        
        width_diff_aver = max((self.tree_width - s)//n , 0) 

        # place the remaining pixel from the eucledean division in the first column
        # if width_diff_aver>0:
        #     remaining_pixels = (self.tree_width - s)%n
        # else:
        #     remaining_pixels = 0

        for col in self.columns_to_show:

            min_width_column = col_max_widths[col]//2
            self.tree.column(col,
                             anchor= 'center',
                             stretch=False,
                             width= col_max_widths[col] + width_diff_aver,
                             minwidth= min_width_column
                            )


    def sort_by_column(self, column):

        if self.sort_column == column:
            self.sort_direction = not self.sort_direction
        else:
            self.sort_column = column
            self.sort_direction = True

        # sort the dataframe wrt the clicked column, reset the index but do not add the previous index to a new column
        self.dataframe = self.dataframe.sort_values(by=column, ascending= self.sort_direction).reset_index(drop =True)

        self.add_rows()

    # Function to extract text and URL from HTML tags
    def extract_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        url = soup.a['href']
        return text, url
    
    # Function to open URL in default web browser
    def open_url(self, event):
        
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_name = self.tree.column(col, option="id")
   
        if row !='' and col_name == 'Fide ID':
            row_n = int(self.tree.item(row)['text'])
            html_tag = self.dataframe.loc[row_n, col_name]
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