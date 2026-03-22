#This code houses several functions for interacting with the equal vote website

import jwt
import secrets
import requests
import json
import time
import hashlib
import datetime
import random
import string
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

#generate a truly random 32 byte key for secure tokens
def randomKey():
    return secrets.token_hex(32)



class BVWebTranslator:
    def __init__(self):
        self.electJSON = None
        self.resultsJSON = None
        self.winner = ""
        self.token = None
        self.key = None
        self.URL = ""
        self.electionID = ""
        self.API = "https://bettervoting.com/API"
        #all user Ids start with this so it is easy to identify what source ballots come from
        self.cookieLead = ""
        
    #Functions related to generating keys
    
    #Function to create and return a token as well as its key
    #TODO store keys and tokens securely
    def createToken(self, user_id: str) -> str:
        key = randomKey()
        idToken = jwt.encode({"sub": user_id}, key, algorithm="HS256")
        self.token = idToken
        self.key = key
    #Function to decode a token with its key
    def decodeToken(self, token: str, key: bytes) -> str:
        return jwt.decode(token, key, algorithms=["HS256"])





    #Functions related to getting elections

    #Assign this object an election, should only be used once per object
    def assignElection(self, electionID: str) -> None:
        if not self.electJSON == None:
            print("ERROR: assignElection called but election already assigned to this object")
            return
        #creates URL with electionID created at bettervoting.com
        self.electionID = electionID
        self.URL = self.API + "/Election/" + self.electionID
        electResp = requests.get(self.URL)
        #creates dictionary with all election data
        self.electJSON = json.loads(electResp.text)
        print("elect JSON")
        print(self.electJSON)
    #Get election JSON file
    def getElection(self) -> dict:
        if self.electJSON == None:
            print("ERROR: getElection called but no election assigned to this object")
        else:
            return self.electJSON
    #update results
    def updateResults(self) -> None:
        url = f"{self.API}/ElectionResult/{self.electionID}"
        resp = requests.get(url)
        print(f"vars resp{vars(resp)}")
        self.resultsJSON = json.loads(resp.text)
        self.winner = self.resultsJSON['results'][0]['elected'][0]['name']
        self.prepCands()

    #Creating an election
    def createElection(self, question: str, endTime: datetime, userID: str, candidates: list) -> None:
        #URL for creating election
        url = f"{self.API}/Elections"
        self.electionID = self.randomChars(6)

        #TODO safeguard against duplicate candidate ids
        #prepare candidate list for API
        cands: list = []
        for candName in candidates:
            cands.append({
                            "candidate_id": f"c-{self.randomChars(3)}",
                            "candidate_name": candName,
                        })

        #prepare payload
        payload = {
            "Election":{
                "end_time": str(endTime),
                "owner_id": str(self.hashUser(userID)),
                "is_public": False,
                "state": "open",
                "races": [
                    {
                        "candidates": cands,
                        "num_winners": 1,
                        "race_id": f"r-{self.randomChars(3)}",
                        "title": question,
                        "voting_method": "STAR"
                    }
                ],
                "title": question,
                "settings": {
                    "voter_access": "open",
                    "voter_authentication": {
                        "address": False,
                        "email": False,
                        "ip_address": False,
                        "phone": False,
                        "voter_id": True
                    },
                    "public_results": True,
                },
            },
        }

        #send payload
        resp = requests.post(url=url, json= payload)
        resp = resp.json()
        #TODO account for fail sends

        self.electionID = resp['election']['election_id']
        #assign self the election just created
        self.assignElection(self.electionID)
        




    #functions for submitting ballots
    #did this user already vote
    #note this isnt inter platform. There is an exploit where a user could vote on the website then again on another platform
    def alreadyVoted(self, user_id: str) -> bool:
        hashedID = self.hashUser(user_id)
        resp = requests.get(f"{self.API}/Election/{self.electionID}", cookies={'user_id': hashedID})

        #if so return True, if not False, None on error
        if resp.status_code == 200:
            return False
        elif resp.status_code == 400:
            return True
        return None
    #get ballot, usually used to show user their ballot if they double vote attempt
    def getBallot(self, userID):
        pass
    
    #give score and discord user id to this function. It will submit the ballot and add the user to the already voted list. 
    #returns False if user already voted, True on success, and None on an error
    def submitBallot(self, userID: str, scores: list) -> bool:
        #if the user already voted, return False. The vote should not be counted
        alrVote = self.alreadyVoted(userID)
        print(f"alrvote func said {alrVote}")
        if alrVote:
            return False
        elif alrVote == None:
            return None
        
        #if the user didnt already vote, prepare their ballot for submission to BV
        candScores: list = []
        candidates = self.electJSON['election']['races'][0]['candidates']
        for i in range(len(candidates)):
            candScores.append({"candidate_id": candidates[i]['candidate_id'], "score": scores[i]})
        
        payload = {
            "ballot": {
                "election_id": self.electionID,
                "votes": [
                    {
                        "race_id": self.electJSON['election']['races'][0]['race_id'],
                        "scores": candScores
                    }
                ],
                "date_submitted": int(time.time()),
                "status": "submitted"
            },
        }

        #TODO implement error handling for fail sends, return None on fail send
        #Post election with a hashed userID, preceded by vd to indicated a discord voter
        cookie = self.hashUser(userID)
        resp = requests.post((self.URL + '/vote'), json = payload, cookies={'temp_id': cookie})
        return self.successSend(resp, True)

    
    #for hashing userIDs
    def hashUser(self, userID):
        hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
        cookie = f"{self.cookieLead}{hash}"
        return cookie
    def randomChars(self, chars: int):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=chars))
    def successSend(self, resp, noneOnFail: bool):
        if resp.status_code == 200:
            return True
        if noneOnFail:
            return None
        return False

    #Functions related to graphing
    #Create bar graph from data, returns a string which is the graphs png files
    def createBar(self) -> str:
        #makes the actual bar graph
        def actualBar(names: list, values: list, secondRound: bool, id: str):
            plt.barh(names, values)
            #is this the first or second round
            if secondRound:
                roundNum = "1"
                plt.title("Runoff Round")
            else:
                roundNum = "2"
                plt.title("Scoring Round")
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.savefig(f"graphTemp/{roundNum}{id}.png", dpi=50, bbox_inches="tight")

        #update results, the prepare data for graphs
        self.updateResults()
        categories = []
        votes = []
        for candidate in self.prepCands():
            categories.append(candidate[0])
            votes.append(candidate[1])

        finalists = [self.winner, self.resultsJSON['results'][0]['roundResults'][0]['runner_up'][0]['name'], "Equal Support"]
        finalistVotes =  [self.resultsJSON['results'][0]['roundResults'][0]['logs'][-1]['winner_votes'], self.resultsJSON['results'][0]['roundResults'][0]['logs'][1]['runner_up_votes'], self.resultsJSON['results'][0]['roundResults'][0]['logs'][1]['equal_votes']]
        finalists.reverse()
        finalistVotes.reverse()

        #makes ID that will later be used by program to get pngs
        #this system using processes seems backwards, but it makes sure that matplot keeps data on its own graph
        pngID = self.randomChars(10)
        p1 = Process(target=actualBar, args=(categories, votes, False, pngID))
        p2 = Process(target=actualBar, args=(finalists, finalistVotes, True, pngID))

        p1.start()
        p1.join()
        p2.start()
        p2.join()
        #return the pngID. Lead with 1 to get the score round, lead with 2 to get the runoff
        return pngID
        
        
    #Get a simple list of candidate names and scores. Sorting is unnecessary, they arrive in order
    def prepCands(self) -> list:
        candidates = []
        for candidate in self.resultsJSON['results'][0]['summaryData']['candidates']:
            candidates.append([candidate['name'], candidate['score']])
        candidates.reverse()
        return candidates