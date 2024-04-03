'''This module gets the URL of a fide player profile rating page and returns a dictionary with information about the player.

It contains two functions:
- a simple one to discart unnecessary characters from a string, 
  called remove_newlines_tabs_spaces(some_sting)
- one to get the URL of the player and return a dictionary with information 
'''

import requests
from bs4 import BeautifulSoup
import re
import csv

# this needs improvement
def remove_newlines_tabs_spaces(my_string):
    """
    Removes tabs, newline and redundant whitespace characters from a strig.
    """
    
    for char in '\n\t':
        my_string = my_string.replace(char, ' ')        
    my_string = ' '.join([word for word in my_string.split() if word != ' '])
    
    return my_string

def web_page_rating_scrab(url):
    """ 
    Gets the url for the profile of a player from the fide site 
    and returns a dictionary with information about the player
        
    If the page is empty returns None

    Args:
        url (string): 
        For example:
            https://ratings.fide.com/profile/

    Returns:
        dict: dictionary with information about the player, keys are strings and values are strings
        For expamle:
            {'fide name': 'Drakopoulos Polihronis', 'std': '2114', 'rapid': '2037', 'blitz': '1977', 'GRE Rank all': 303, 'GRE Rank active': 176}
    """
    
    # fetch the page data, no API is provided
    responce  = requests.get(url)
    soup = BeautifulSoup(responce.content, 'html.parser')
    
    # if no fide_id is present the page is empty and the title is None the player is not listed in Fide in this case
    if soup.title == None:
        return None
    
    # find the fide name of the player, removing unnecessary characters
    player_name  = soup.title.text
    player_name = player_name.replace('"','')
    
    # define the dictionary to be returned and add the name of the player
    elo_dict = {'fide name': ''.join(player_name.split(','))}
    
    # loop through the tags for the values of std, rapid and blitz elo
    for tag in soup.find_all('span', class_='profile-top-rating-dataDesc'):
        
        # return to parent tag to include the type of elo and the value
        elo_type_value = remove_newlines_tabs_spaces(tag.parent.text).split()
        
        # check if the player is rated or not
        if len(elo_type_value) == 2:
            elo_type, elo_value = elo_type_value
        else:
            elo_type, elo_value = elo_type_value[0], ' '.join(elo_type_value[1:])
            
        # store elo type-values     
        elo_dict[elo_type] = elo_value

    # find additional information, here only federation,
    # loop thorugh tags for Global, National and European rank amond all and active players             
    for tag in soup.find_all('table', class_="profile-table profile-table_offset_3"):
        info = remove_newlines_tabs_spaces(tag.text)
        
        # only keep the native rankings
        if 'National' in info:
            # capture the Federation acronim (i.e GRE)
            federation = re.search(r'National Rank (\b[A-Z]+\b)',info)
            federation = federation.groups()[0]
            national_ranks = [int(word) for word in info.split() if word.isnumeric()]
            
            # store the federation, all and active rank
            elo_dict['federation'] = federation
            elo_dict['National Rank All'] = national_ranks[0]
            elo_dict['National Rank Active'] = national_ranks[1]

    return elo_dict

if __name__ == '__main__':
    # use the following lines to construct the html file of the page
    url = 'http://ratings.fide.com/card.phtml?event=4232984'
    url_not_rated = 'https://ratings.fide.com/profile/4217217'
    # with open('fide_rating_site.html','w', encoding='utf-8') as file:
    #     file.write(responce.text)
    print(web_page_rating_scrab(url))
    print(web_page_rating_scrab(url_not_rated))