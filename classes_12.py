# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 10:42:00 2021

@author: grab
Current version:
    monitor class: takes care of the monitoring, should never be called by the user.
    overseer:      oversees monitoring class. contains all the usefull functions for monitoring
        add_match
        start/stop monitoring
    gambler:       gets the overseer data and takes care of mining/gambling
    
    
Stuff left to do:
    1- make comments more consistent
    2- rename variables/function more consistently
    3- add safe try/catch mechanism everywhere
     i.   add broker dependent inhibitors and kill switches
     ii.  check if threadkills is properly done
     iii. 
    4- add a function that checks if the odds sent to the bet are still equal to the current odds!!!
    
Then:
    1- make an external class that commits the dictionnaries to a database structure

Then:
    1- code the save data functions to SQL db stack
    2- code the analysis tools to perform numerical simulation of bankroll
    3- make a neural net to assimilate the outcomes name consistently
    
Then:
    1- make scrapping functions and other tools necessary to commit queries data to the dictionnaries
    

"""
import random
import numpy as np
import time
import logging
import threading
# import pandas as pd
# import matplotlib.pyplot as plt
from tqdm import tqdm

#% user input class       
class user_input_generator():
    def __init__(self):
        global sleepTime
        sleepTime = 1e-3
        print("User input machine instanciated")
        
    def initiate_random_match(self):
    #Generate data for a match w/ random sport & random nb_of_brokers
    #This function simulate a match initialization
    #Draws a random sport type and number of broker
    #Generate the initial values for the matchList stack
        sportList  = ["Tennis","Soccer","HorseRace", "Hockey"]
        brokerList = ["Brkr1", "Brkr2", "Brkr3", "Brkr4", "Brkr5", "Brkr6", "Brkr7", "Brkr8"] 
        
        nbBroker = random.randint(2,len(brokerList)-1)
        brokers  = brokerList[0:nbBroker]
        
        sportSelector = random.randint(0,len(sportList)-1)
        sport         = sportList[sportSelector]
        
        if sport=="Tennis":
            outcomeList   = ["p1","p2"] 
            
        elif sport=="Soccer":
            outcomeList   = ["p1","p2","p3"] 
            
        elif sport=="HorseRace":
            outcomeList   = ["p1","p2","p3","p4","p5","p6","p7"] 
             
        elif sport=="Hockey":
            outcomeList   = ["p1","p2","p3","p4"] 
        
        matchId    = random.randint(0,15254)
        brokerIds  = [random.randint(12,2056) for ii in range(nbBroker)]
        
        startime   = time.time()
        
        
        return matchId, brokerIds, brokers, outcomeList, sport, startime
    
    
    def get_batch_matches(self,nbOfMatches):
    # Calls initiate_random_match in a loop to generate fake matches in batches
        matchIds    = []
        brokerIds   = []
        brokers     = []
        outcomeList = []
        sport       = []
        startime    = []
        
        for ii in range(nbOfMatches):
            matchId_temp, brokerIds_temp, brokers_temp, outcomeList_temp, sport_temp, startime_temp = self.initiate_random_match()    
            
            matchIds.append(matchId_temp)
            brokerIds.append(brokerIds_temp)
            brokers.append(brokers_temp)
            outcomeList.append(outcomeList_temp)
            sport.append(sport_temp)
            startime.append(startime_temp)
            time.sleep(0.01)  
        return matchIds, brokerIds, brokers, outcomeList, sport, startime


'''
#############################This class oversees the whole operation ######################
### overseer class controls monitor class in a user-friendly way
### overseer classwill control saving data, formatting and commit to stack


'''            
            
class overseer:
    #############################
    ### INTERNAL FUNCTIONS ### 
    # Only used internally or for debugging, user should not have to call these 
    #############################   
    def __init__(self,SleepTime=1):
        #These 3 dictionnaries contain the full information about the matches.
        self.match_list = {}
        self.match_data = {}
        self.match_monitor_control = {}
        
        #This variable destroys all monitoring and assigning
        self.kill_assigning = False

        #Monitor query delay - is overseer input        
        global querySleepTime 
        querySleepTime = SleepTime
        
        #instanciate the monitor subclass
        self.monitorWasCreated = False
        self.instanciate_monitor()
        
    def assign_monitor_to_overseer(self):
    #this function assigns monitor data to overseer data
    #runs in a loop in its own thread until kill_assigning is true
        def run_thread_assign_monitor_to_overseer(stop, kill_assigning):
            while True:
                try:
                   self.match_list = self.moni.match_list
                   self.match_data = self.moni.match_data
                   self.match_monitor_control = self.moni.match_monitor_control
                   time.sleep(1e-3)
                   #if kill_assigning is true, monitoring and assigning stops
                   if self.kill_assigning == True:
                        
                        self.match_list = self.moni.match_list
                        self.match_data = self.moni.match_data
                        self.match_monitor_control = self.moni.match_monitor_control
                        print("Monitoring and assigning stoped")
                        break
                except:
                   time.sleep(1e-3)
                    
        
        #run the assigning function in a new thread
        stopflag = False #syntax only variable, useless.
        thread_assign_monitor_to_overseer = threading.Thread(target = run_thread_assign_monitor_to_overseer, args =(lambda : stopflag, ), kwargs = {'kill_assigning' : self.kill_assigning} )
        thread_assign_monitor_to_overseer.name = "assign_monitor_to_overseer"
        thread_assign_monitor_to_overseer.start()
        return

    def instanciate_monitor(self):
    #Instanciate monitor and assign its output to overseer data
            if self.monitorWasCreated == False:
                self.moni = self.monitor()          #instanciate monitor
                self.assign_monitor_to_overseer()   #assign monitor data to overseer
                self.monitorWasCreated = True
                print("Overseer instanciated")
                
            else:
                print("Monitor already created")
            return
    #############################
    ### END OF INTERNAL FUNCTIONS # 
    #############################.  
    
    
    #############################
    ### CALLABLE FUNCTIONS ###
    # user friendly functions #
    #############################    
       
    def kill_all(self):
    #inhibits matches and stops monitoring all matches
        # self.kill_assigning = True
        time.sleep(1e-4)
        self.moni.inhibit_all_match()
        return
    
    def live_all(self): 
    #resume or start monitoring all matches. Does not interupt matches that were already monitored
        print("Resuming all...")
        # self.kill_assigning = False
        self.moni.allow_all_match()
        time.sleep(1e-4)
        # self.assign_monitor_to_overseer() #restart the assignement to overseer
        self.moni.monitor_all_markets()     #restoring monitoring of all markets
        print("--")
        return
    
    def kill_match(self, matchId):
    #stops monitoring of a single match
        self.moni.inhibit_match(matchId)
        return
    
    def live_market(self,matchId, broker):
    #resume monitoring of single market
        print("Resuming match: " + str(matchId) + " | broker: " + broker)
        self.kill_assigning = False
        self.assign_monitor_to_overseer()
        self.moni.allow_single_match(matchId)
        time.sleep(1e-4)
        self.moni.monitor_single_market(matchId, broker)        
        return
   
    def live_match(self,matchId):
    #resume monitoring of single match
        print("Resuming match: " + str(matchId) + " | broker: all")
        self.kill_assigning = False
        self.assign_monitor_to_overseer()
        self.moni.allow_single_match(matchId)
        time.sleep(1e-4)
        self.moni.monitor_single_match(matchId)        
        return
    
    def add_matches(self,matchIds, brokerIds, brokers, outcomeList, sport, startime):
    #add matches from the full match information. Does not start the monitoring! use the above function after this one!
    #matches can be added in batch. If a match preexists in the list it is not added.
        if self.monitorWasCreated == False:
            self.instanciate_monitor()
            time.sleep(1e-3)
        
        self.moni.generate_match_list(matchIds, brokerIds, brokers, outcomeList, sport, startime)
        return

    def show(self):
    #List all mining and betting allowance and current states   
        try:       
            matchIds = self.match_list['matchId']
            for matchId in self.match_list['matchId']:
                print("Match: " + str(matchId))
                matchIndex = self.match_list['matchId'].index(matchId)
                print("Sport: " + self.match_list['sport'][matchIndex])
                for key in self.match_monitor_control[str(matchId)]:
                    print(key + "=" + str(self.match_monitor_control[str(matchId)][key]))
                print("---")
        except:
            print("Could not list monitored matches, maybe there are none ?")
        return    
            

    #############################This class fetches the odds ##########################################    
    # monitor class     : superclass owning all the broker/match dependent classes
    # you should never to have to call functions from this class. It handles all the execptions internally
    class monitor():
        def __init__(self):            
        #These 3 dictionnaries contain the full information about the matches.
            self.match_list = {}            #matches metadata
            self.match_data = {}            #matches data, brokers odds, time etc.
            self.match_monitor_control = {} #control options for monitoring
            print("Monitor instanciated")
            
        #############################
        ### TEST FUNCTIONS ###
        # Only used as place holder for future functions #
        #############################
        
        def get_broker_market(self,match_list, matchId):
        # fake single internet query for unique match, unique broker, all outcomes
        # to be replaced by broker/sport dependent HTML payload functions
        # to be run in a thread to avoid waiting for query response
            index = match_list["matchId"].index(matchId)
            
            nBOutcomes = len(match_list["outcomes_List"][index])
            
            muOneOverOdds = 1.1 #average of inverse Odds
            sigGauss      = .3   #Gaussian error
            
            odds       = [round(random.gauss(nBOutcomes/muOneOverOdds,sigGauss),2) for ii in range(nBOutcomes)]
            marketOpen =  random.choices([0,1], weights=(5,95),k=nBOutcomes) 
            theTime    = time.time()
            time.sleep(sleepTime)
            return odds, marketOpen, theTime
        #############################
        ### END OF TEST FUNCTIONS ###
        #############################
        
        
        
        #############################
        ### INTERNAL FUNCTIONS ### 
        # Only used internally or for debugging, user should not have to call these 
        #############################   
        
        def instanciate_match_data(self,match_list, matchId):
        # instanciate match_data dictionnary using the match_list      
            index = match_list["matchId"].index(matchId)
            nBOutcomes = len(match_list["outcomes_List"][index])  
            nbBrokers  = len(match_list["brokers_list"][index])  
            
            column1 = [match_list["brokers_list"][index][ii]+"_Odd"    for ii in range(nbBrokers)]
            column2 = [match_list["brokers_list"][index][ii]+"_isOpen" for ii in range(nbBrokers)]
            column3 = [match_list["brokers_list"][index][ii]+"_time"   for ii in range(nbBrokers)]
            
            columns = column1 + column2 + column3
            columns = np.transpose(columns) 
            
            matchDictionnary = {}
            matchDictionnary["matchId"] = [matchId]
            for jj in range(nBOutcomes):    
                d = {}
                for ii in range(len(columns)):
                    d[columns[ii]] = []
            
                matchDictionnary[match_list["outcomes_List"][index][jj]] = d
            
            match_data_dictionnary = matchDictionnary
            return match_data_dictionnary
        
        
        def instanciate_all_match_data(self,match_list):
        # instanciate match_data in a loop with the full match list
            allMatchesDictionnary = {}
            allMatchesDictionnary["matchId"] = []
            for matchId in match_list["matchId"]:
                allMatchesDictionnary["matchId"].append(matchId)
                matchDictionnary = self.instanciate_match_data(match_list, matchId)    
                allMatchesDictionnary[str(matchId)] = matchDictionnary
                
            allmatch_data_dictionnary = allMatchesDictionnary
            return allmatch_data_dictionnary  
        
        
        def append_newmatch_match_data(self,match_list,allMatchesDictionnary):
        # append match_data when adding a match to the match_list
            match_list_ids = match_list["matchId"]
            allMatchesDictionnary_ids = allMatchesDictionnary["matchId"]
            
            notInList = np.setdiff1d(match_list_ids, allMatchesDictionnary_ids)
            
            if len(notInList) != 0:
                
                for matchId in notInList:
         
                    allMatchesDictionnary["matchId"].append(matchId)
                    matchDictionnary = self.instanciate_match_data(match_list, matchId)    
                    allMatchesDictionnary[str(matchId)] = matchDictionnary
            
            allmatch_data_dictionnary = allMatchesDictionnary
            return allmatch_data_dictionnary
    
        
        def instanciate_match_list(self, matchId, brokerIds, brokers, outcomeList, sport, startime):
        # Instanciate the match list
            matchDictionnary = {}
            matchDictionnary["matchId"]             = [matchId]
            matchDictionnary["sport"]               = [sport]
            matchDictionnary["outcomes_List"]       = [outcomeList]
            matchDictionnary["brokers_list"]        = [brokers]
            matchDictionnary["match_brokerIds"]     = [brokerIds]
            matchDictionnary["start_Time"]          = [startime]
            matchDictionnary["end_Time"]            = [0]
            matchDictionnary["final_outcome"]       = ["-"]
    
            
            print("Instanciated")
            print("Appended matchId:" + str(matchId) + "| sport: " + sport)
        
            match_list_dictionnary = matchDictionnary
            return match_list_dictionnary
    
    
        def append_match_list(self, matchDictionnary, matchId, brokerIds, brokers, outcomeList, sport, startime):
        # Append match_list when adding a match     
            if matchDictionnary["matchId"].count(matchId) == 0:
                matchDictionnary["matchId"].append(matchId)
                matchDictionnary["sport"].append(sport)
                matchDictionnary["outcomes_List"].append(outcomeList)
                matchDictionnary["brokers_list"].append(brokers)
                matchDictionnary["match_brokerIds"].append(brokerIds)
                matchDictionnary["start_Time"].append(startime)
                matchDictionnary["end_Time"].append(0)
                matchDictionnary["final_outcome"].append("-")
    
                
                print("Appended matchId:" + str(matchId) + "| sport: " + sport)
            else:
                print("matchId already in matchList")
            
            allmatch_list_dictionnary = matchDictionnary
            return allmatch_list_dictionnary    
    
    
        def instanciate_match_monitor_control(self, match_list, matchId):
        # instanciate match_monitor dictionnary using the match_list           
            index = match_list["matchId"].index(matchId)    
            nbBrokers  = len(match_list["brokers_list"][index])  
            
            column1 = [match_list["brokers_list"][index][ii]+"_isMonitored"  for ii in range(nbBrokers)]
            column2 = [match_list["brokers_list"][index][ii]+"_wasMonitored" for ii in range(nbBrokers)]
            column3 = ["inhibitor"]
            
            columns = column1 + column2 + column3
            columns = np.transpose(columns) 
            
            d = {}
            for ii in range(len(columns)):
                d[columns[ii]] = False #Monitoring is not done initially
                if columns[ii] == "inhibitor":
                    d[columns[ii]] = True #Monitoring is forbidden initially
        
            
            match_data_dictionnary = d
            return match_data_dictionnary
        
            
        def instanciate_all_match_monitor_control(self,match_list):
        # instanciate match_monitor_control in a loop with the full match list
            allMatchesDictionnary = {}
            allMatchesDictionnary["matchId"] = []
            for matchId in match_list["matchId"]:
                
                allMatchesDictionnary["matchId"].append(matchId)
                matchDictionnary = self.instanciate_match_monitor_control(match_list, matchId)    
                allMatchesDictionnary[str(matchId)] = matchDictionnary
                
            allmatch_data_dictionnary = allMatchesDictionnary
            return allmatch_data_dictionnary  
        
            
        def append_newmatch_monitor_control_list(self,match_list,allMatchesDictionnary):
        # append match_monitor when adding a match to the match_list
            match_list_ids = match_list["matchId"]
            allMatchesDictionnary_ids = allMatchesDictionnary["matchId"]
            
            notInList = np.setdiff1d(match_list_ids, allMatchesDictionnary_ids)
            
            if len(notInList) != 0:
                
                for matchId in notInList:
         
                    allMatchesDictionnary["matchId"].append(matchId)
                    # allMatchesDictionnary[str(matchId)]["inhibitor"] = False
    
                    matchDictionnary = self.instanciate_match_monitor_control(match_list, matchId)    
                    allMatchesDictionnary[str(matchId)] = matchDictionnary
            
            allmatch_data_dictionnary = allMatchesDictionnary
            return allmatch_data_dictionnary
        
            
        def update_single_market(self, matchId, broker):
        # makes a single query on a single broker & match
        # this function will be rewritten for each broker and each sport type!
            indexMatch = self.match_list["matchId"].index(matchId)
            outcomes   = self.match_list["outcomes_List"][indexMatch]
            
            odds, marketOpen, theTime = self.get_broker_market(self.match_list, matchId) 
            for outcome in outcomes:
               indexOutcome = outcomes.index(outcome)
               self.match_data[str(matchId)][outcome][broker+"_isOpen"].append(marketOpen[indexOutcome])
               self.match_data[str(matchId)][outcome][broker+"_Odd"].append(odds[indexOutcome])
               self.match_data[str(matchId)][outcome][broker+"_time"].append(theTime)
                    
            match_data = self.match_data
            return match_data
        #############################
        ### END OF INTERNAL FUNCTIONS # 
        #############################.
        
        
        
        #############################
        ### CALLABLE FUNCTIONS ###
        # user friendly functions #
        #############################
        
        def generate_match_list(self, matchId_batch, brokerIds_batch, brokers_batch, outcomeList_batch, sport_batch, startime_batch):
        # generate or append match list data using private instanciate/append functions - can be used in batch.            
            #if one of the dictionnary is empty we instanciate a new one
            if self.match_list == {} or self.match_data == {} or self.match_list == [] or self.match_data == []:
                for ii in range(len(matchId_batch)):
                    if ii == 0:
                        match_list = self.instanciate_match_list(matchId_batch[ii], brokerIds_batch[ii], brokers_batch[ii], outcomeList_batch[ii], sport_batch[ii], startime_batch[ii])
                        
                    else: 
                        match_list = self.append_match_list(match_list, matchId_batch[ii], brokerIds_batch[ii], brokers_batch[ii], outcomeList_batch[ii], sport_batch[ii], startime_batch[ii])
                        
                match_data = self.instanciate_all_match_data(match_list)
                match_monitor_control = self.instanciate_all_match_monitor_control(match_list)
    
            #appending if dictionnaries are not empty   
            else:
                for ii in range(len(matchId_batch)):
                    match_list = self.append_match_list(self.match_list, matchId_batch[ii], brokerIds_batch[ii], brokers_batch[ii], outcomeList_batch[ii], sport_batch[ii], startime_batch[ii])
                
                match_data = self.match_data
                match_data = self.append_newmatch_match_data(match_list,match_data)
                match_monitor_control = self.match_monitor_control
                match_monitor_control = self.append_newmatch_monitor_control_list(match_list,match_monitor_control)
    
    
            
            #update the internal variables.                
            self.match_list = match_list
            self.match_data = match_data
            self.match_monitor_control = match_monitor_control
            
            return match_list, match_data, match_monitor_control
    

        
        def monitor_single_market(self, matchId, broker):
        #continuously makes query on a single market using update_single_market(self, matchId, broker) function
        #Opens thread when functon called, closes thread when inhibitor is set to True
             # The thread function       
            def run_thread_monitor_single_market(stop, matchId, threadInhibitors):
            
                while True:
                    self.match_monitor_control[str(matchId)][broker + "_isMonitored"]  = True
                    self.match_monitor_control[str(matchId)][broker + "_wasMonitored"] = True
    
                    #query function. Will be broker/sport dependent later on
                    self.update_single_market(matchId, broker)
                    
                    #pause between queries
                    time.sleep(querySleepTime)
            
                    if self.match_monitor_control[str(matchId)]['inhibitor'] == True:
                        self.match_monitor_control[str(matchId)][broker + "_isMonitored"] = False
                        print("Match: "+ str(matchId)+ " : "+ broker+" killed" +"\n")
                        break
                
                    
              
            stopflag = False     #This variable is useless and here for syntax only     
            if self.match_monitor_control[str(matchId)]['inhibitor'] == False:
                if self.match_monitor_control[str(matchId)][broker + "_isMonitored"] == False:
                    thread_monitor_single_market = threading.Thread(target = run_thread_monitor_single_market, args =(lambda : stopflag, ), kwargs = {'matchId' : matchId, 'threadInhibitors': self.match_monitor_control[str(matchId)]['inhibitor']} )
                    thread_monitor_single_market.name = "thread_monitor_single_market_matchId: " + str(matchId) + " | broker: " + str(broker)
                    thread_monitor_single_market.start()
                    print("Match: "+ str(matchId)+ " : "+ broker+" now monitored")
                else:
                    print("Match: "+ str(matchId)+ " : "+ broker+" already monitored")
                
               
            else:
                print("Match: "+ str(matchId) + " inhibited" +"\n")
        
            return
        
        
        def monitor_single_match(self, matchId):
        #Monitor all brokers for a single match. Loops through monitor_single_market
            indexMatch = self.match_list["matchId"].index(matchId)   
            for broker in self.match_list["brokers_list"][indexMatch]:
                self.monitor_single_market(matchId, broker)
                
            return
        
        def monitor_all_markets(self):
        #Monitor all markets by opening threads for each match & brokers
        #Calls monitor_single_market(self, matchId, broker) to open each thread
            for matchId in self.match_list["matchId"]:
                
                indexMatch = self.match_list["matchId"].index(matchId)
                brokers    = self.match_list["brokers_list"][indexMatch]
                    
                for broker in brokers:
                    self.monitor_single_market(matchId, broker)
       
                print("--")       
            return
            
        
        def inhibit_match(self, matchId):
        #inhibit monitoring of a single match
            self.match_monitor_control[str(matchId)]['inhibitor'] = True
            return
        
        def inhibit_all_match(self):
        #inhibit monitoring of all matches
            print("killing all matches")
            for matchId in self.match_list["matchId"]:
                for broker in brokers:
                    self.inhibit_match(matchId)
            
            return
        
        
        def allow_single_match(self, matchId):
        #deinhibit monitoring of a single match. Does not start monitoring!
            print("Allowing match: " + str(matchId))
            self.match_monitor_control[str(matchId)]['inhibitor'] = False
            return
        
        
        def allow_all_match(self):
        #inhibit all matches. Stops monitoring!
            print("Allowing all matches")
            for matchId in self.match_list["matchId"]:
                for broker in brokers:
                    self.allow_single_match(matchId)
            
            return



#############################This class analyses match_data, places bets and stores them ##########################################    
# inherit the match_data and match_list from the overseer class.

class gambler(overseer):
    def __init__(self, class_overseer): 
        time.sleep(.5)
        global randomQueryReponseTime 
        randomQueryReponseTime = 8
        print("Gambler instanciated")
        self.match_list = class_overseer.match_list # The match list from the overseer (itself a copy of the monitor.match_list)
        self.match_data = class_overseer.match_data # The match data from the overseer (itself a copy of the monitor.match_data)
        self.match_monitor_control = class_overseer.match_monitor_control # The match_monitor_control from the overseer (itself a copy of the monitor.match_monitor_control)
        

        if self.match_list == [] or self.match_list == {}:
            print("Nothing in match_list. Please add matches to overseer before instanciating gambler")

        else:
            self.match_gambler_control = self.instanciate_all_match_gambler_control() #contains gambler inhibitions (used for control)
            self.match_decision = self.instanciate_match_decision()                   #contains gambler decisions   (is a log) 
            self.refresh_match_gambler_control() # This will automatically add new matches to match_gambler_control when adding in overseer.
            time.sleep(.25)
            self.handle_gambler_inhibitor()      # Automatically inhibits gambling if monitoring is inhibited
            time.sleep(.25)
            self.handle_mining()
            time.sleep(.25)

                
        
        #############################
        ### TEST FUNCTIONS ###### 
        # These will be replaced by proper functions.
        #############################. 
    def run_thread_bet(self,matchId, best_odds, best_brokers, outcomesList):
    #Thread being run during the betting on a single match.    
    # places bet over all brokers/outcomes for a single match  
        #compute the actual bet strategies and values by looking at the particular match
        bet_Values, profit, roi = self.compute_bet_value(matchId, best_odds)
        #format the bet_payload to accomodate for the query_bet function
        brokers_bet, outcomes_bet, odds_bet, stakes_bet, time_bet, brokersId_bet, sport = self.format_bet_payload(matchId, best_odds, best_brokers, bet_Values, outcomesList)
        #sends the actualy query, this will open a thread for each market and place the bet.
        place_bet_responses = self.query_bet(matchId, brokers_bet, outcomes_bet, odds_bet, stakes_bet, time_bet, brokersId_bet, sport)
        #stores bet in match_decision
        self.append_match_decision(matchId, brokers_bet, outcomes_bet, odds_bet, stakes_bet, profit, roi, time_bet, sport, place_bet_responses)
        return
       
          
    def query_bet(self, matchId, brokers_bet, outcomes_bet, odds_bet, stakes_bet, times_bet, brokers_Id, sport):
    # send the bet query, broker/sport dependent, the input must be formated by calling format_bet_payload
    # Each subbet (for each stake/odd) is ran on a different thread to avoid waiting for queries to end.
    # We must add a function that checks if the query odds are still equal to the mined odds
        responses = [] #This variable will store the responses of the queries this enables the thread to run in parallel without waiting for the reponses
        

        for index in range(len(outcomes_bet)):
             
            broker   = brokers_bet[index]
            outcome  = outcomes_bet[index]
            odd      = odds_bet[index]
            stake    = stakes_bet[index]
            brokerId = brokers_Id[index]
            
            def run_thread_queryBet(matchId, index, sport, broker, outcome, odd, stake, brokerId):
                nonlocal responses #make responses accessible within the thread
                time.sleep(random.randrange(0,randomQueryReponseTime)) # This random pause is the random query time. To verify the queries are sent in parallel
                print("-------"  + "\n" +
                "subBet query placed on match: " + str(matchId) + "\n" +
                'Query nb: '   + str(index)   + "\n" +
                'Sport: '      + str(sport)   + "\n" +
                'Broker: '     + str(broker)  + "\n" +
                'Outcome: '    + str(outcome) + "\n" +
                'Odd: '        + str(odd)     + "\n" +
                'Stake: '      + str(stake)   + "\n" 
                + "------")
                

                responses.append(index) #update the thread
                return 
                        
            
            #run the assigning function in a new thread
            stopflag = False #syntax only variable, useless.
            thread_query_bet = threading.Thread(target = run_thread_queryBet, args =(matchId, index, sport, broker, outcome, odd, stake, brokerId) )
            thread_query_bet.name = "query_bet matchId: " + str(matchId)
            thread_query_bet.start()
            print("Closing Mining/Betting on Match: " + str(matchId))
            self.unmine_match(matchId)
            
        query_responses = responses
        return query_responses
    
    def compute_bet_value(self, matchId, best_odds):
    #Once a match has been identified by the mining function by the mining_opportunities function
    # this one computes the payload (stakes, broker etc.)
    # formula is set to adjust the winnings to be equal on all outcomes
    # stake_j = stake/(sum_i(o_j/o_i))
        nbOutcomes = len(best_odds)
        oneOverOdds = [1/best_odds[ii] for ii in range(nbOutcomes)]
        
        stake = 10 #This is the total stake accross all outcomes

        # only allowed if 1/p is lower than 1. useless here since the check was already done
        if np.sum(oneOverOdds)<1:
            bet_Values  = [ stake/(sum( np.multiply(best_odds[ii],oneOverOdds) ) )  for ii in range(nbOutcomes) ]
            profits     = [bet_Values[ii]*(best_odds[ii]) - stake                   for ii in range(nbOutcomes) ]
            roi         = [ (profits[ii]/stake)*100                                 for ii in range(nbOutcomes) ]


        return bet_Values, profits, roi
    
    def format_bet_payload(self, matchId, best_odds, best_brokers, bet_Values, outcomesList) :
    # This function formats the payload into human understandable format, fitting the gambler_decision dictionnary
        indexMatch  = self.match_list['matchId'].index(matchId)
        macth_data = self.match_data[str(matchId)]
        
        nbBets = len(self.match_list['outcomes_List'][indexMatch])
        #generate random numbers for now.
        brokers_bet     = best_brokers
        outcomes_bet    = outcomesList
        odds_bet        = best_odds
        stakes_bet      = bet_Values
        time_bet        = time.time()
        sport           = self.match_list['sport'][indexMatch]
        
        brokersId_bet   = []
        for broker in brokers_bet:
            indexBroker        = self.match_list['brokers_list'][indexMatch].index(broker)
            brokersId_bet.append(self.match_list['match_brokerIds'][indexMatch][indexBroker])
        
        return brokers_bet, outcomes_bet, odds_bet, stakes_bet, time_bet, brokersId_bet, sport

        
        #############################
        ### END OF TEST FUNCTIONS ### 
        #############################.         



        
        
        #############################
        ### INTERNAL FUNCTIONS ###### 
        #############################.
        
    def instanciate_match_decision(self):
    # Instanciate match_decision, "vanilla" is the empty template to keep for understanding
        initial_match_decision_level2 = {}
        initial_match_decision_level2['brokers_bet']     = []
        initial_match_decision_level2['outcomes_bet']    = []
        initial_match_decision_level2['odds_bet']        = []
        initial_match_decision_level2['stakes_bet']      = []
        initial_match_decision_level2['stake']           = []        
        initial_match_decision_level2['profit']          = []
        initial_match_decision_level2['roi']             = []
        initial_match_decision_level2['time_bet']        = []
        initial_match_decision_level2['sport']           = []
        initial_match_decision_level2['reponses']        = []

        
        initial_match_decision={}
        initial_match_decision['vanilla']    = []
        initial_match_decision['vanilla'].append(initial_match_decision_level2)
        initial_match_decision['matchId']    = []             
        return initial_match_decision
    
    
    def append_match_decision(self, matchId, brokers_bet, outcomes_bet, odds_bet, stakes_bet, profit, roi, time_bet, sport, place_bet_responses):
    # Updates match_decision when a bet is placed
        temp_match_decision_level2 = {}
        temp_match_decision_level2['brokers_bet']     = brokers_bet
        temp_match_decision_level2['outcomes_bet']    = outcomes_bet
        temp_match_decision_level2['odds_bet']        = odds_bet
        temp_match_decision_level2['stakes_bet']      = stakes_bet
        temp_match_decision_level2['stake']           = np.sum(stakes_bet)        
        temp_match_decision_level2['profit']          = profit
        temp_match_decision_level2['roi']             = roi
        temp_match_decision_level2['time_bet']        = time_bet
        temp_match_decision_level2['sport']           = sport 
        temp_match_decision_level2['responses']       = place_bet_responses 
        
    
        
        try:     #Try to append bet if a bet was already placed
            self.match_decision[str(matchId)].append(temp_match_decision_level2)
            self.match_decision['matchId'].append(matchId)
        except KeyError: #Instanciate a new match ID 
            self.match_decision[str(matchId)] = []
            self.match_decision[str(matchId)].append(temp_match_decision_level2)
            self.match_decision['matchId'].append(matchId)
            
        print("Appended match_decisions")
        return
    
    
    def instanciate_match_gambler_control(self,matchId):
    # instanciate match_gambler control dictionnary using the match_list          
            index = self.match_list["matchId"].index(matchId)    
            nbBrokers  = len(self.match_list["brokers_list"][index])  
            
            column1 = ["isMined"]
            column2 = ["wasMined"]    
            column3 = ["inhibitor_mine"]
            column4 = ["inhibitor_bet"]
            
            columns = column1 + column2 + column3 + column4
            columns = np.transpose(columns) 
            
            d = {}
            for ii in range(len(columns)):
                d[columns[ii]] = False #Mining is not done initially
                if columns[ii] == "inhibitor_bet" or columns[ii] == "inhibitor_mine":
                    d[columns[ii]] = True #Bet/Mining is forbidden initially
            
            match_data_dictionnary = d
            return match_data_dictionnary
   
    
    def instanciate_all_match_gambler_control(self):
    # instanciate match_monitor_control in a loop with the full match list
            allMatchesDictionnary = {}
            allMatchesDictionnary["matchId"] = []
            for matchId in self.match_list["matchId"]:
                
                allMatchesDictionnary["matchId"].append(matchId)
                matchDictionnary = self.instanciate_match_gambler_control(matchId)    
                allMatchesDictionnary[str(matchId)] = matchDictionnary
                
            allmatch_data_dictionnary = allMatchesDictionnary
            return allmatch_data_dictionnary
    
    
    
    def append_newmatch_gambler_control_list(self):
    # append match_control when adding a match to the match_list
            match_list_ids = self.match_list["matchId"]
            allMatchesDictionnary_ids = self.match_gambler_control["matchId"]
            
            notInList = np.setdiff1d(match_list_ids, allMatchesDictionnary_ids)
            
            if len(notInList) != 0:
                
                for matchId in notInList:
         
                    self.match_gambler_control["matchId"].append(matchId)
                    # allMatchesDictionnary[str(matchId)]["inhibitor"] = False
    
                    matchDictionnary = self.instanciate_match_gambler_control(matchId)    
                    self.match_gambler_control[str(matchId)] = matchDictionnary
                    print("Appended match to gambler_control")

            allmatch_data_dictionnary = self.match_gambler_control
            return allmatch_data_dictionnary
     
        
    def refresh_match_gambler_control(self):
    # #continously update the match_gambler_control dictionnary in a new thread when a new match is added via the overseer
        def run_thread_refresh_match_gambler_control(stop):

            while True:
                try:
                    self.append_newmatch_gambler_control_list()
                    #pause between updates
                    time.sleep(1e-3)
                except:
                    time.sleep(1e-3)
            return                
                
        stopflag = False     #This variable is useless and here for syntax only  
        thread_refresh_match_gambler_control = threading.Thread(target = run_thread_refresh_match_gambler_control, args =(lambda : stopflag, ) )
        thread_refresh_match_gambler_control.name = "thread_refresh_match_gambler_control"
        thread_refresh_match_gambler_control.start()
        return
         
    
    def handle_gambler_inhibitor(self):
    #Turning off gambler mining&gambling if monitoring is off for a broker or inhibited in the monitor.
    #Runs on its own thread, constantly.
        def run_thread_gambler_inhibitor(stop):
                  
                while True:
                    try:
                        for matchId in self.match_gambler_control['matchId']:
                            #only enter the open thread loop if gambling or mining is already allowed
                            if (self.match_gambler_control[str(matchId)]["isMined"] == True         or                                 
                                self.match_gambler_control[str(matchId)]["inhibitor_bet"]  == False):
                            
                       
                                #if match is not allowed to be monitored, we turn off mining and gambling
                                if self.match_monitor_control[str(matchId)]['inhibitor'] == True: 
                                    self.inhibit_bet_match(matchId) #turning off mining and gambling
                                    self.unmine_match(matchId)
                            
                                #if any of the broker is not monitored, we turn off mining and gambling
                                matchIndex = self.match_list['matchId'].index(matchId)   
                                brokerMonitoringTruths = [ self.match_monitor_control[str(matchId)][broker + "isMonitored"] for broker in self.match_list['matchId']["brokers_list"][matchIndex] ]  
                                for brokerMonitoringTruth in brokerMonitoringTruths:                                   
                                    if brokerMonitoringTruth == False: # if any of the broker is not monitored we turn off mining and gambling                                    
                                            self.inhibit_bet_match(matchId) #turning off mining and gambling
                                            self.unmine_match(matchId) 
                                
                        #pause between updates
                        time.sleep(1e-3)
                    except:
                        time.sleep(1e-3)                                    
                return                
                
        stopflag = False     #This variable is useless and here for syntax only  
        thread_handle_gambler_inhibitor = threading.Thread(target = run_thread_gambler_inhibitor, args =(lambda : stopflag, ) )
        thread_handle_gambler_inhibitor.name = "thread_handle_gambler_inhibitor"
        thread_handle_gambler_inhibitor.start()
        return
    
    def handle_mining(self):
    # This function continously turns on/off the mining in a separate thread for all markets, runs in its own thread
    # Continously reads the inhibitiors and mine status to open the threads if needed
    # Threads are closed by the mine_thread_function when needed
    # starts the mining if needed!
        thread_handle_mining = threading.Thread(target = self.run_thread_mining)
        thread_handle_mining.name = "handle_mining"
        thread_handle_mining.start()  
        print("Opening mining (sub)threads ...")
        return
    
    
    def run_thread_mining(self):
    # Opens new thread for each minined matches. This function is called by handle_mining
        while True:
            time.sleep(1e-3)            
            try:
                for matchId in self.match_gambler_control['matchId']:
                    
                    #only enter the check loop mining if already allowed and match not mined already, monitoring must be allowed too.
                    if (self.match_gambler_control[str(matchId)]["isMined"] == False          and                                 
                        self.match_gambler_control[str(matchId)]["inhibitor_mine"]  == False  and
                        self.match_monitor_control[str(matchId)]['inhibitor'] == False):
                        # print(matchId)
                        #starts the mining if needed!
                         
                        thread_run_thread_mining = threading.Thread(target = self.mine_thread_function, args=(matchId,)) 
                        thread_run_thread_mining.name = "main_mine_" + str(matchId)
                        thread_run_thread_mining.start()
                        print( "-----" + "\n" +
                               thread_run_thread_mining.name + " is now open" + "\n" +
                              "match " + str(matchId) + " is now mined" + "\n" +
                              "-----")
                       
                        
            except:
                time.sleep(1e-3)                                    
        return 
    
    
    def mine_thread_function(self, matchId):
    # This function is the thread for the mining, it kills itself when inhibitors are set to high
        while True:            
            time.sleep(1e-6)
            if (self.match_gambler_control[str(matchId)]["inhibitor_mine"]  == False  and
                self.match_monitor_control[str(matchId)]['inhibitor'] == False):
    
                self.match_gambler_control[str(matchId)]["isMined"]  = True
                self.match_gambler_control[str(matchId)]["wasMined"] = True            
                
                self.mining_opportunities(matchId)
    
            else:                
                self.match_gambler_control[str(matchId)]["isMined"]  = False                
                print("closing the thread for match: " + str(matchId))
                break
        return
    
    def mining_opportunities(self, matchId):
    # This function takes the match_data and reads all odds at the time. Checking if there is a playable bet accross all brokers.
    # It calls the place_bet function when an opportunity exists   
        match_data = gambi.match_data[str(matchId)] # Match To mine
    
        # Data needed from the match
        matchIndex  = gambi.match_list['matchId'].index(matchId)
        outcomeList = gambi.match_list['outcomes_List'][matchIndex]
        brokerList  = gambi.match_list['brokers_list'][matchIndex]
    
        # Placeholder for best odds/brokers amongts all brokers
        best_odds = []
        best_brokers = []
    
        # Loop through all outcomes
        for outcome in outcomeList:
            temp_odds    = []
            temp_brokers = []
            #Loop through all brokers
            for broker in brokerList:
                # If market is open, append the odds and corresponding broker
                if (match_data[outcome][broker + '_isOpen'][-1]) == 1:            
                    temp_odds.append(match_data[outcome][broker + '_Odd'][-1])  #looking at the last updated odds
                    temp_brokers.append(broker)
                    
                    
                else: #If market is not open, we place unrealistic odds
                    temp_odds.append(1e-5) 
                    temp_brokers.append(broker) 
            
            # Grabs the best odds (biggest!) and corresponding broker
            best_odds.append(np.max(temp_odds))
            brokerIndex = np.argmax(temp_odds, axis=0) 
            best_brokers.append(brokerList[brokerIndex])
        
        inverse_Odds = (1./np.array(best_odds))
        sumOdds = np.sum(inverse_Odds)
        # print(best_odds)
        # print(sumOdds)  
        # actual triggers for bets
        if sumOdds < 1 and self.match_gambler_control[str(matchId)]["inhibitor_bet"]  == False and self.match_gambler_control[str(matchId)]["inhibitor_mine"]  == False:
            print("!!!######!!!#######!!!"           + "\n" +
                  "##!Possible Bet on!##"            + "\n" +
                  "##!match: " + str(matchId)+"!##"  + "\n" +
                  "!!!######!!!######!!!" )
            #Stops the mining only, betting will be canceled later once the bet is placed
            self.match_gambler_control[str(matchId)]["inhibitor_mine"]  = True
            #Place the bets
            self.place_bet(matchId,best_odds,best_brokers,outcomeList)

        return 
            
 
        
    def place_bet(self, matchId, best_odds, best_brokers, outcomeList):
    # This function places the bet: call the following function: compute the payload, format the payload and send the individual queries to the broker (in separate thread)
    #  place_bet itself runs in separate threads to allow multiple matches to be bet on the same time.
    #  within a match, each outcome is sent queries within own thread (subthreads), this allow each subbet to be placed in parallel
               
        #run the assigning function in a new thread
        if self.match_gambler_control[str(matchId)]['inhibitor_bet'] == False:
            print('###### Opening bet thread... ######') 
            stopflag = False #syntax only variable, useless.
            thread_place_bet = threading.Thread(target = self.run_thread_bet(matchId, best_odds, best_brokers, outcomeList), args =(matchId) )
            thread_place_bet.name = "thread_place_bet matchId: " + str(matchId)
            thread_place_bet.start()
        else:                
            print("Gambing inhibited for match: " + str(matchId) )           
        #############################
        ### END OF INTERNAL FUNCTIONS # 
        #############################.      
        
   
        
        #############################
        ### CALLABLE FUNCTIONS ###
        # user friendly functions #
        #############################
        
        
    def inhibit_bet_match(self, matchId):
    #inhibit a single match gambling
        print("Killing gambling on match: " + str(matchId))
        self.match_gambler_control[str(matchId)]['inhibitor_bet'] = True
        return

        
    def inhibit_bet_all_match(self):
    #inhibit all matches gambling
        print("Killing gambling on all matches")
        for matchId in self.match_list["matchId"]:            
            self.inhibit_bet_match(matchId)        
        return

        
    def allow_bet_match(self, matchId):
    #deinhibit a single match gambling, only allowed if all brokers are monitored and if match is being mined
        if self.match_monitor_control[str(matchId)]['inhibitor'] == False :
            index = over.match_list['matchId'].index(matchId)
            monitoring_Truth = [over.match_monitor_control[str(matchId)][broker + "_isMonitored"] for broker in over.match_list['brokers_list'][index]]
            mining_Truth = [gambi.match_gambler_control[str(matchId)]["isMined"]]
    
            if all(monitoring_Truth) and all(mining_Truth):
                print("Allowing gambling on match: " + str(matchId))
                self.match_gambler_control[str(matchId)]['inhibitor_bet'] = False
            else:
                print("Match: " + str(matchId) + " not monitored or not mined. Turn on monitoring/mining first!")
        else:
            print("Match: " + str(matchId) + " monitoring inhibited. Turn on monitoring first!")
        return

        
    def allow_bet_all_match(self):
    #deinhibit all matches gambling
        print("Allowing gambling on all matches")
        for matchId in self.match_list["matchId"]:
            self.allow_bet_match(matchId)              
        return


    def mine_match(self,matchId):
    #start mining a single match, only if monitored and not already mined. Start/Stop a thread for each match/broker
        index = self.match_list["matchId"].index(matchId)    
        monitoring_Truth = [over.match_monitor_control[str(matchId)][broker + "_isMonitored"] for broker in over.match_list['brokers_list'][index]]

        
        if self.match_monitor_control[str(matchId)]['inhibitor'] == True :
            print("Match: " + str(matchId) + " monitoring inhibited. Turn on monitoring first!")
            
        elif all(monitoring_Truth) == False :
            print("Match: " + str(matchId) + " some brokers are not monitored. Turn on monitoring first!")
                        
        else:
                
                if self.match_gambler_control[str(matchId)]["isMined"] == True:
                    print("Match: " + str(matchId) + " is already being mined")
                
                elif self.match_gambler_control[str(matchId)]["isMined"] == False:
                    self.match_gambler_control[str(matchId)]["inhibitor_mine"]  = False
                    print("Allowing mining for match: " + str(matchId))  
        return


    def mine_all_matches(self):
    #mine all allowed matches, does not turn off bet inhibitor!
        print("Mining all possible matches...")
        for matchId in self.match_list["matchId"]:
            self.mine_match(matchId)
        return


    def unmine_match(self,matchId):
    #Stop mining and inhibits betting on a single match.
        print("Killing mining and inhibiting betting on match: "+ str(matchId))
        index = self.match_list["matchId"].index(matchId) 
        self.inhibit_bet_match(matchId) #not mining prevents betting
        self.match_gambler_control[str(matchId)]["inhibitor_mine"]  = True #This variable will be used to kill the mine_match thread
        return
 
    
    def unmine_all_matches(self):
    #Stop mining and inhibits betting on all single matches.
        print("Stop Mining and inhibiting betting on all possible matches...")
        for matchId in self.match_list["matchId"]:
            self.unmine_match(matchId)       
        return
 
    
    def show(self):
    #List all mining and betting allowance and current states   
        try:       
            matchIds = self.match_list['matchId']
            for matchId in self.match_list['matchId']:
                print("Match: " + str(matchId))
                matchIndex = self.match_list['matchId'].index(matchId)
                print("Sport: " + self.match_list['sport'][matchIndex])
                for key in self.match_gambler_control[str(matchId)]:
                    print(key + "=" + str(self.match_gambler_control[str(matchId)][key]))
                print("---")
        except:
            print("Could not display bet inhibitors and monitoring status")
        return
    

        #############################
        ### END OF CALLABLE FUNCTIONS ###
        #############################
        






