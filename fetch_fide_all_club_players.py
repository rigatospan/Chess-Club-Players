'''This script receives a CSV file with info including the fide-ratings URL of chessclub's players,
and return two CSV files, one with only the fide info of players and one with national and fide info.

Example:
Input: 'eso_players_ratings.csv'
Output: 'fide_players_ratings.csv' , 'eso_and_fide_players_ratings.csv'
'''

from fetch_fide_one_player import web_page_rating_scrab
import csv

# create two CSV files, one for only the fide information, and one to merge fide and eso info
fide_players_ratings = open('fide_players_ratings.csv', 'w', encoding='utf-8',newline='')
eso_fide_players_ratings = open('eso_and_fide_players_ratings.csv', 'w', encoding='utf-8',newline='')

# search for the first player with fide rating to set up the headers
with open('eso_players_ratings.csv', 'r', encoding='utf-8') as file:
    players_data = csv.DictReader(file)
    
    # loop through the eso players until we find one with fide rating
    for eso_player_row in players_data:
        fide_player_link = eso_player_row['fide link']
        if fide_player_link[-1].isdigit():
            fide_player_dict = web_page_rating_scrab(fide_player_link)
            fide_headers = list(fide_player_dict.keys())
            eso_fide_headers = list(eso_player_row.keys()) + list(fide_player_dict.keys())
            break

# write headers
writer_fide = csv.DictWriter(fide_players_ratings, fieldnames= fide_headers) 
writer_fide.writeheader()
writer_eso_fide = csv.DictWriter(eso_fide_players_ratings, fieldnames=eso_fide_headers)
writer_eso_fide.writeheader()
      
# write the two CSV files  
with open('eso_players_ratings.csv', 'r', encoding='utf-8') as file:
    players_data = csv.DictReader(file)
    
    # loop through the eso players
    for eso_player_row in players_data:
        fide_player_link = eso_player_row['fide link'] 
        
        # initialize fide player dictionary to empty in case there is no fide rating
        fide_player_dict = {}
        
        # ask for the fide ratings only for the players who have them and write them in fide file
        if fide_player_link[-1].isdigit():
            fide_player_dict = web_page_rating_scrab(fide_player_link) 
            writer_fide.writerow(fide_player_dict)
         
        # write player data to eso_fide file
        writer_eso_fide.writerow({**eso_player_row, **fide_player_dict})
        
# close the files
fide_players_ratings.close()
eso_fide_players_ratings.close()