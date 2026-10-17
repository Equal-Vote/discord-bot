import asyncio
import time


#Discord.py automatically checks for most rate limiting, but not global. This tracks global rate limiting
#When we get too close to the limit, it is logged in a database as well as whether it happened during startup, as this is the most common time for it and the solution for that is far simpler than other rate limiting issues
#Limit as of writing is 50 per second

#If we hit this number, we make note of it. It may be time to split the bots
barrier = 45
class rateCheck():
    
    def __init__(self):
        #collection of all channels interaction data. "1" represents interactions that have no channel id, such as changing bot's online status
        self.globalInteractions = []
        self.deployment = True
        self.decrementAmount = .05

    #Add interaction to be ticked down
    def addInteraction(self):
        self.globalInteractions.append(1)
    
    #tick all items down by .05 seconds. Remove all items with a value 0 or less
    def tickDown(self):
        for i in range(len(self.globalInteractions)):
            self.globalInteractions[i] -= self.decrementAmount
        self.globalInteractions = [x for x in self.globalInteractions if x > 0]

    #Wait for a clear global rate limit
    #This should be called before every discord API call
    async def wait(self):
        while True:
            if len(self.globalInteractions) >= barrier:
                await asyncio.sleep(1)
            else:
                self.addInteraction()
                return



  