#This code houses several functions for interacting with the equal vote website

import jwt
import secrets
import requests
import json
import time
import hashlib



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

        
        pass
        
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
        print(self.URL)
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
        self.resultsJSON = json.loads(resp.text)
        self.winner = self.resultsJSON['results'][0]['elected'][0]['name']

    #Creating an election
    #unfinished DO NOT USE
    def createElection(self, title: str, description: str = "") -> None:
        url = f"{self.API}/Elections"

        payload = {}



    #functions for submitting ballots
    #did this user already vote
    #note this isnt inter platform. There is an exploit where a user could vote on the website then again on another platform
    #The only current way around this is to make elections private and only call the election with your bot on your platform
    def alreadyVoted(self, user_id: str):
        pass
    
    #give score and discord user id to this function. It will submit the ballot and add the user to the already voted list. 
    #returns False if user already voted, True on success, and None on an error
    def submitBallot(self, userID: str, scores: list) -> bool:
        #if the user already voted, return False. The vote should not be counted
        #put something here

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
        hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
        cookie = f"vd-{hash}"
        resp = requests.post((self.URL + '/vote'), json = payload, cookies={'temp_id': cookie})
        return True
            

        


