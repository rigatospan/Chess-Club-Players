import re
import os
from datetime import datetime
import time

import csv
import json
import pandas as pd

import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import requests

class FetchPlayersDatabase:

    def __init__(self, parent, club_url):
        self.parent = parent 
        self.club_url = club_url
        self.number_of_players = 0
        self.team_name = ''

    # this needs improvement
    def remove_newlines_tabs_spaces(self,my_string):
        """
        Removes tabs, newline and redundant whitespace characters from a strig.
        """
        
        for char in '\n\t':
            my_string = my_string.replace(char, ' ')        
        my_string = ' '.join([word for word in my_string.split() if word != ' '])
        
        return my_string
    
    #--------------------------------------Get Fide Information for one player--------------------------------------------------------------------------------

    async def web_page_rating_scrab(self, players_url):
        """ 
        Gets the players_url for the profile of a player from the fide site 
        and returns a dictionary with information about the player
            
        If the page is empty returns None
    
        Args:
           players_url (string): 
            For example:
                https://ratings.fide.com/profile/
    
        Returns:
            dict: dictionary with information about the player, keys are strings and values are strings
            For expamle:
                {'fide name': 'Spirakopoulos Ioannis', 'std': '2035', 'rapid': '1998', 'blitz': '2009', 'Fide Title': '0', 'federation': 'GRE', 'National Rank All': 507, 'National Rank Active': 264}
        """
        
        # # fetch the page data, no API is provided
        # check if the player has fide profile; return an empty dictionary otherwise
        if not players_url[-1].isdigit():
            return {}
        
        async with ClientSession() as session:
            async with session.get(players_url) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')

        # if no fide_id is present the page is empty and the title is None the player is not listed in Fide in this case
        if soup.title == None:
            return None
        
        # find the fide name of the player, removing unnecessary characters, as of 3/25 there is FIDE Profile in the title
        player_name  = soup.title.text
        # some players have a comma in their name, some a dot 'only one actually: diplas michail
        char_to_split = ',' if ',' in player_name else '.'
        
        surname, name = player_name.split(char_to_split)
        name = name.split()[0]
        
        # define the dictionary to be returned and add the name of the player
        elo_dict = {'fide name': ' '.join([surname, name])}
            
        # find the three types of elo values
        elo_tag = soup.find('div', class_='profile-games')
        for elo_type_tag in elo_tag:
            
            # find the elo type, value and inactive status
            elo_type_value = self.remove_newlines_tabs_spaces(elo_type_tag.text)
            
            # find the type and value of the elo; if Not rated set value as 0
            if 'STANDARD' in elo_type_value:
                elo_type = 'std'
            elif 'RAPID' in elo_type_value:
                elo_type = 'rapid'
            elif 'BLITZ' in elo_type_value:
                elo_type = 'blitz'
            else:
                continue
                
            if 'Not rated' in elo_type_value:
                elo_value = '0'
            else:
                elo_value = elo_type_value[0:4]
            
            # store elo type-values
            elo_dict[elo_type] = elo_value
    
        # find additional information, here only federation,
        # loop thorugh tags for Global, National and European rank amond all and active players             
        for tag in soup.find_all('div', class_="profile-rank-block"):
            info = self.remove_newlines_tabs_spaces(tag.text)
            
            # only keep the native rankings
            if 'National' in info:
                # capture the Federation acronim (i.e GRE)
                federation = re.search(r'National Rank (\b[A-Z]+\b)',info)
                federation = federation.groups()[0]
                national_ranks = [int(word) for word in info.split() if word.isnumeric()]
                
                # store the federation, all and active rank
                elo_dict['federation'] = federation
                elo_dict['National Rank All'] = national_ranks[1]
                elo_dict['National Rank Active'] = national_ranks[0]
        # if the player is not rated set them to 0
        if 'federation' not in elo_dict:
            elo_dict['federation'] = 'GRE'
            elo_dict['National Rank All'] = 0
            elo_dict['National Rank Active'] = 0
            
        # find the title of the player, if any else set it to '0'
        title_tag = soup.find('div', class_='profile-info-title')
        if title_tag:
            title = title_tag.text.strip()
            if title == 'None':
                title = '0'
            elo_dict['Fide Title'] = title

        # uncomment the follwing line to check the information 
        # print(elo_dict)
        
        return elo_dict
    
    #--------------------------------------Get Club National Elo information for all players-------------------------------------------
    
    async def fetch_eso_players(self):
        '''This script receives as input a chessclub's URL from the Greek National chess federation with information about the club's player,
        and creates a csv file with that information.

        For example:
        Input: eso_club_url = 'https://chesstu.be/eso/club/01151'
        Output: eso_club_players.csv
        '''            

        # fetch and write the page's data; No API is provided; response is in text/html format 
        response = requests.get(self.club_url)
        players_info = response.text

        with open("eso_players_ratings.html", 'w', encoding='utf-8') as f:
            f.write(players_info)

        with open('eso_players_ratings.html', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # find the name of the team from the <title> tag
        self.team_name = soup.find('title').text
        self.team_name = self.remove_newlines_tabs_spaces(self.team_name)

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
            
            self.number_of_players+=1

            # create lists to store the players data in the cells of the row
            player_row = []
            player_row_hyperlinks = []
            
            # loop though the row of the player
            for row_data in row.children:
                
                # check that the child tag is a table data
                if row_data.name == 'td':
                    
                    # remove unnecessary characters
                    info = self.remove_newlines_tabs_spaces(row_data.text)
                    
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
    
        return 
    
    #-------------------------------Fetch Fide Ratings and Info for all club's players------------------------------------------------------
    
    async def fide_players_scrapping(self, urls):
 
        async with asyncio.TaskGroup() as tg:
            tasks = []
            for url in urls:
                task = tg.create_task(self.web_page_rating_scrab(url))
                tasks.append(task)
            
        results = [task.result() for task in tasks]

        return results

    async def fetch_fide_all_club_players(self):
        '''This script receives a CSV file with info including the fide-ratings URL of chessclub's players,
        and return two CSV files, one with only the fide info of players and one with national and fide info.

        Example:
        Input: 'eso_players_ratings.csv'
        Output: 'fide_players_ratings.csv' , 'eso_and_fide_players_ratings.csv'
        '''

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
                    fide_player_dict = await self.web_page_rating_scrab(fide_player_link)
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
            
            players_data = list(csv.DictReader(file))
            # loop through the eso players to tget the fide urls
            urls = []
            for i,eso_player_row in enumerate(players_data):
                fide_player_link = eso_player_row['fide link'] 
                urls.append(fide_player_link)

            fide_players_list_dicts = await self.fide_players_scrapping(urls)

            for eso_player_row, fide_player_dict in zip(players_data, fide_players_list_dicts):
                # write player data to eso_fide file
                writer_fide.writerow(fide_player_dict)
                writer_eso_fide.writerow({**eso_player_row, **fide_player_dict})

        # close the files
        fide_players_ratings.close()
        eso_fide_players_ratings.close()

        return
    
    async def built_database_to_present_to_user(self):
        ''' Builts the database to present in the main application user as the default database of players that 
        the user is watching and searching to
        
        Example:
        Input: 'eso_and_fide_players_ratings.csv'
        Output: 'table_toshow.pkl'
        '''

        # import and inspect the table
        df_eso_fide_players = pd.read_csv('eso_and_fide_players_ratings.csv')

        # replace NaN values and othe empty values: 'Not rated', '-' with '0'
        modified_players_list = df_eso_fide_players.fillna('0').replace(['Not rated', 'Not', '-'], '0')

        # replace gender Greek characters to English
        modified_players_list = modified_players_list.replace(['Α','Θ'], ['M','F'])

        # create a column with the Fide Id hyperlinked when using .style attribute
        def make_clickable(url, value_to_apply_url):
            return '<a href="{}">{}</a>'.format(url,value_to_apply_url)

        modified_players_list['FIDE'] = modified_players_list['FIDE'].astype(int)
        modified_players_list['Fide ID'] = modified_players_list.apply(lambda col: make_clickable(col['fide link'], col['FIDE']) , axis=1)

        # discard hyperlink columns
        modified_players_list = pd.concat([modified_players_list.iloc[:, :11] , modified_players_list.iloc[:, 14:]], axis=1)


        # transform integer values to int type
        for col in modified_players_list.columns:
            try:
                modified_players_list[col] = modified_players_list[col].astype(int)
            except:
                pass

        # renaming column index 
        modified_players_list = modified_players_list.rename(columns= {
                                    'ΑΑ': 'Club Rank National',
                                    'ΚΩΔΙΚΟΣ': 'National ID',
                                    'FIDE': 'Fide',
                                    'ΟΝΟΜΑ': 'National Name',
                                    'Η/Γ': 'Date of Birth' ,
                                    'ΦΥΛΟ': 'Gender',
                                    'ΤΙΤΛΟΣ': "National Title",
                                    'ΕΛΟ': 'National Elo',
                                    'ΠΑΡΤΙΔΕΣ': 'Games last 6 months',
                                    '*': 'Outsider' ,
                                    'ΤΔ': 'Eso Fee',
                                    'fide name' : 'Fide Name',
                                    'federation' : 'Federation',
                                    })

        # parse the date of birth and creare a new Age column; birthday is in the form 'mm/yyyy' so a add '01/' as the day 
        modified_players_list['Birthday'] = pd.to_datetime('01/'+ modified_players_list['Date of Birth'], dayfirst=True)
        modified_players_list['Age'] = modified_players_list['Birthday'].map(lambda x: datetime.today().year - x.year)

        # create a column with boolean values to state if the player appears active in fide or not
        modified_players_list['Fide Active'] = modified_players_list['National Rank Active'].map( lambda rank_active: rank_active > 0)

        # table to present and order of columns
        col_toshow = [
                'National Name',
                'Fide Name',
                'National Elo', 
                'std', 
                'rapid', 
                'blitz',
                'Age',
                'Birthday',
                'Eso Fee', 
                'Fide Active', 
                'Gender',
                'National ID',
                'Fide ID',
                'Federation',
                'National Title',
                'Fide Title',
                ]
        table_toshow = pd.concat([modified_players_list[col] for col in col_toshow], axis=1)
        
        # create a database with the name of the team 
        table_toshow.to_pickle(f'{self.team_name}.pkl')
        
        # create a json file with the team's name - url and the total number of players, date updated
        teams_info_dic = {self.team_name : self.club_url, 
                          'Number of Players': self.number_of_players,
                          'Last Updated': datetime.today().date().isoformat(),
                          }
        with open(f'{self.team_name}.json', 'w', encoding='utf-8') as file:
            json.dump(teams_info_dic, file)

        return 
    
    async def delete_csv_html_files(self):
        '''Deletes the csv and html files that were used to fetch, explore
        and build the database
        '''
        os.remove('eso_and_fide_players_ratings.csv')
        os.remove('eso_players_ratings.csv')
        os.remove('fide_players_ratings.csv')
        os.remove('eso_players_ratings.html')
        
        return
    
    async def main_fetch_built_database(self):
        '''control the flow of the fetching and database building
        '''

        t1= time.time()
        await self.fetch_eso_players()
        t2 = time.time()
        # print(f'time for eso players scrapping {round(t2-t1, 3)}')

        t3 = time.time()
        await self.fetch_fide_all_club_players()
        t4 = time.time()
        # print(f'time for all fide players scrapping {round(t4-t3, 3)}')

        t5 = time.time()
        await self.built_database_to_present_to_user()
        t6 = time.time()
        # print(f'time for modifiying and building the database {round(t6-t5,3)}')
        
        # delete the csv and html files
        await self.delete_csv_html_files()


if __name__ == '__main__':
    so_aigaleo_players_url = 'https://chesstu.be/eso/club/01151'
    so_aigaleo = FetchPlayersDatabase(None, so_aigaleo_players_url)
    
    # use the following line to fetch the database of all players
    asyncio.run(so_aigaleo.main_fetch_built_database())
    
    # use the following line to test for only one player if the information is correct and the website is the same
    # asyncio.run(so_aigaleo.web_page_rating_scrab(players_url='https://ratings.fide.com/profile/4233395'))