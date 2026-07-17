import discord
import datetime
import schedule
import time
import asyncio

#all interactions are checked against one object based on this class to avoid rate limiting
#for referece, discord allows 5 API requests per 5 seconds in channels, and 50 globally. Our limites are a bit lower to have a buffer

#How much we are decrementing by. This shouldnt change
decrementAmount = .25
class rateCheck():
    def __init__(self):
        #Contains timers that check we dont exceed rate limits for every channel
        self.rateData = {}
        #Checks that we dont exceed the global rate limit
        self.globalTimer = self.timer(True)
        #This is put here so it can be accessed by main.py
        self.decrementAmount = decrementAmount
    #delete timers with no interactions. These channels are safe
    def __decrementTimers(self):
        try:
            for key, value in self.rateData:
                if len(value.interactions) <= 0:
                    del self.rateData[key]
        except Exception as e:
            print(e)
    def runTasks(self):
        print("running tasks")
        #If there is at least one timer, decrement all of their interactions and delete empty ones
        if len(self.rateData) > 0:
            for key, value in self.rateData.items():
                value.decrementInteractions()
            datedTimers = []
            for key, value in self.rateData.items():
                if value.empty:
                    datedTimers.append(key)
            for i in datedTimers:
                if self.rateData[i].empty:
                    del self.rateData[i]
        return None
    
    class timer():
        def __init__(self, globalTimer = False):
            if globalTimer:
                self.maxInt = 48
                self.cooldown = 2
            else:
                self.maxInt = 3
                self.cooldown = 6
                #This avoids rare collisions where the item is added to the dict and culled before its first Interaction can be added. Add Interactions shoudnt be called after making this
            self.interactions = [self.cooldown]
            #is self empty
            self.empty = False
        #cull interactions sent more than 5 seconds ago. Most limits are based off of 5 second intervals
        def decrementInteractions(self):
            print(self.interactions)
            if len(self.interactions) <= 0:
                self.empty = True
            else:
                #oldest interactions will always be at the start of the list. Find how many dated interactions there are and delete them
                datedInteractions = 0
                for i in range(len(self.interactions)):
                    self.interactions[i] -= decrementAmount
                    if self.interactions[i] <= 0:
                        datedInteractions += 1
                for i in range(datedInteractions):
                    del self.interactions[0]
        #add an interaction
        def addInteraction(self):
            #this line is here to catch edge cases where the timer is set to empty and another interaction is added before the timer is culled
            self.empty = False
            self.interactions.append(self.cooldown)
        #are we full on interactions?
        def check(self):
            print("these are all interactions")
            print(self.interactions)
            if len(self.interactions) > self.maxInt:
                return False
            return True
        
        
    #to see if it can be sent, it must pass the global and channel specific rate limit
    def isClear(self, channelID):
        def addInteraction(channelTimer = None, globalTimer = self.globalTimer):
            #workaround since addinteraction shouldnt be called when making a timer
            if not channelTimer == None:
                channelTimer.addInteraction()
            globalTimer.addInteraction()

        key = channelID
        print("global test")
        #global test
        if not self.globalTimer.check():
            print("failed")
            return False

        print("channel test")
        #channel test
        if not key in self.rateData:
            print("making new timer")
            self.rateData[key] = self.timer()
            addInteraction()
            return True
        else:
            print("checking")
            if self.rateData[key].check():
                print("check passed")
                addInteraction(self.rateData[key])
                return True
        return False

    #return True once it can be sent
    #This should always be awaited
    async def waitForRate(self, channelID):
        limit = 100
        try:
            while True:
                print("waiting")
                if self.isClear(channelID):
                    print("int passed")
                    return True
                else:
                    limit -= 1
                    if limit <= 0:
                        print("Waiting for interaction timed out")
                        return False
                asyncio.sleep(decrementAmount)

                
        except Exception as e:
            print("Error from wait for rate")
            print(e)