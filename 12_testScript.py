# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 19:10:41 2021

@author: grab
"""

exec(open('classes_12.py').read())

def disp():
    print("THREADS RUNNING:::::")
    for thread in threading.enumerate(): 
        print(thread.name)
        
#%%
nbmatches = 25
user = user_input_generator()
matchIds, brokerIds, brokers, outcomeList, sport, startime = user.get_batch_matches(nbmatches)   

over = overseer(.5)
over.add_matches(matchIds, brokerIds, brokers, outcomeList, sport, startime)  
time.sleep(0.5)
gambi = gambler(over)
over.live_all()
gambi.mine_all_matches()
time.sleep(0.5)
gambi.allow_bet_all_match()




tt = gambi.match_data


over.show()
time.sleep(0.5)
gambi.show()     
time.sleep(0.5) 
disp()

over.kill_all()

over.kill_match(matchId)
over.live_match(matchId)

gambi.unmine_match(matchId)
gambi.mine_match(matchId)
gambi.place_bet(matchId)
gambi.allow_bet_match(matchId)

    

