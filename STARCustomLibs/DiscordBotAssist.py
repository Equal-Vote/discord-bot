import discord
import discord.ext.commands as commands


#set tokens for alpha, beta, and full versions for easy switching when pushing versions. True gets beta, false gets alpha, None gets full
#Unused token slots can be filled with any text, it does not matter
#ALWAYS remove tokens before pushing to repo. Tokens should NEVER be made public under ANY circumstances, inlcluding alpha ones
def toggleToken(alpha:str, beta:str, full:str, testType:bool):
        if testType is None:
            return full
        elif testType:
            return beta
        else:
            return alpha


#A collection of common functions for discord bots
class DisBotAssist:
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    #send or receive a DM from a user
    async def sendDM(self, message : str, user : discord.user) -> None:
        await user.send(message)
    async def receiveDM(self, user : discord.user, lower : bool = True) -> str:
        message = await self.bot.wait_for('message', check= lambda m: m.author == user)
        message = message.content
        if lower:
            message = message.lower()
        return message
    
    #ask a question, run a function depending on the response
    async def ask(self, question : str, pairs : dict, defErrorResp : str, user : discord.user, exitComm : str = 'exit') -> list:
        await self.sendDM(question, user)
        while(True):
            response = await self.receiveDM(user)
            response = response.strip()
            #If user decides to exit, exit
            if response == exitComm:
                return [None, None]
            
            #See if any the response matches a potential response, call relevant function if so
            for i in pairs.keys():
                if response == i:
                    
                    try:
                        return [pairs[i](), response]
                    except TypeError:
                        return [None, response]
                    except:
                        raise TypeError("What the fuck did you put in that dictionary?")
            
            #Send error response if not, then loop again
            await self.sendDM(defErrorResp, user)

    #ask a question, receive users response
    async def askSimple(self, question : str, user : discord.user) -> str:
        await self.sendDM(question, user)
        return await self.receiveDM(user)


    #get text after command
    def getCommArg(self, messageCont: str) -> str:
        arg:str = messageCont
        #look for space after command, return any text after (ex. ?Poll animals returns animals, ?Poll returns empty) 
        for i in range(len(messageCont)):
            arg = arg[1:]
            if arg[0] == " ":
                arg = arg[1:]
                break
        return arg



        
    


    

    
