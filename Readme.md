'''
## Project:
Pipeline for sync-threaded bet/monitoring on multiple brokers accross multiple matches.
## Features:
- This code monitors odds on multiple online sport-gambling broker.
- You can monitor multiple matches on any sports
- The code will detect and flag arbitrage opportunities accross all brokers.
- You can enable automatic betting to launch your arbritage bets.
## Notes:
Note : This project is on hold: brokers are changing their APIs too often for me to make a solid scrapping/betting system... :(
- Everything runs on its own thread (match monitoring, database handling, match gambling).
- URL-related functions (scrapping, betting, tokenId user_id) are placeholder, you will have to code your own (this will depend on which websites/brokers you wish to operate on, their versions).
- GUI is not ready to be shared.
- 99% of the overhead is waiting for URL requests, therefore I coded this code to be userfriendly and readable rather than fast.


class user_input_generator:  a placeholder for your user_inputs (match lists, match url or anything you'd like) - replace once you know where you wish to gamble.

class overseer: the main user UI class. This is class handle gambling/monitoring user input. This is the class you wish to insert in your GUI later on.

class monitor: monitors matches. A new instance of this class is created and lives in its own thread for each match you wish to monitor or gamble on.
This class also performs the URL requests (the scrap functions in this repo are placeholder - because its implementation will depends on the broker you wish to monitor, the website version i.e the hard work goes here;) etc.)
This class handle the database in the form of a dictionnary hashmap.

class gambler: continiously reads the monitor database and performs relevent actions (such as betting). URL functions are also placeholder (for identical reasons).

logchange (pre git)
Current version:
    monitor class: takes care of the monitoring, should never be called by the user.
    overseer:      oversees monitoring class. contains all the usefull functions for monitoring
        add_match
        start/stop monitoring
    gambler:       gets the overseer data and takes care of mining/gambling
    
'''
