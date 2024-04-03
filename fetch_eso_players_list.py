'''This script receives as input a chessclub's URL from the Greek National chess federation with information about the club's player,
and creates a csv file with that information.

For example:
Input: eso_club_url = 'https://chesstu.be/eso/club/01151'
Output: eso_club_players.csv
'''

import requests
from bs4 import BeautifulSoup
import lxml
import csv

def remove_newlines_tabs_spaces(my_string):
    """
    Removes tabs, newline and redundant whitespace characters from a string.
    """
    for char in '\n\t':
        my_string = my_string.replace(char, ' ')        
    my_string = ' '.join([word for word in my_string.split() if word != ' '])
    
    return my_string

# provide the chess club's eso URL 
so_aigaleo_eso_url = 'https://chesstu.be/eso/club/01151'

# fetch and write the page's data; No API is provided; response is in text/html format 
response = requests.get(so_aigaleo_eso_url)
players_info = response.text

with open("eso_players_ratings.html", 'w', encoding='utf-8') as f:
    f.write(players_info)

with open('eso_players_ratings.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'lxml')

# find the headers in the players table
headers = [header.text for header in soup.find_all('th')]

# define the names of the hyperlinks, the order is manually placed 
hyperlink_headers = [
                    'fide link',
                    'eso player history',
                    'eso player last 6 month games',
                    ]

# add hyperlink names to the headers
headers += hyperlink_headers

# create an CSV file to store the players data
csv_file = open('eso_players_ratings.csv','w', encoding='utf-8', newline='') 
writer = csv.DictWriter(csv_file, fieldnames= headers)
writer.writeheader()

# loop through all players, i.e. all rows in the table 
for row in soup.find_all('tr')[1:]:
    
    # create lists to store the players data in the cells of the row
    player_row = []
    player_row_hyperlinks = []
    
    # loop though the row of the player
    for row_data in row.children:
        
        # check that the child tag is a table data
        if row_data.name == 'td':
            
            # remove unnecessary characters
            info = remove_newlines_tabs_spaces(row_data.text)
            
            #replace empty cell with 'NONE'
            if info=='':
                info = 'None'
            
            # append cell into the player's row list
            player_row.append(info)

            # get hyperlinks 
            for additional_child in row_data.children:
                
                # check that the tag is hyperlink
                if additional_child.name == 'a':
                    
                    # get the hyperlink throught the tag's 'href' attribute
                    url_player = additional_child.get('href')
                    
                    # add hyperlink to the players row hyperlinks list
                    player_row_hyperlinks.append(url_player)
    
    # constract the players dictionary and add it to the CSV file;
    # add some None values instead of hyperlinks if needed
    player_row =  player_row + player_row_hyperlinks + ['None']*(len(hyperlink_headers)-len(player_row_hyperlinks))
    player_dict = {head:value for head, value in zip(headers, player_row+player_row_hyperlinks)}
    writer.writerow(player_dict)

# close the CSV file
csv_file.close()