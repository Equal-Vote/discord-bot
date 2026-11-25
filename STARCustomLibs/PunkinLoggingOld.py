#This is to help with some kinds of error logging
from datetime import datetime

class errorLogger():
    def __init__(self, path):
        
        self.path = path
        #create file now so it doenst delay error logging later
        self.log("Creating PunkinLog file", False, False)

    #print and log text or error
    def log(self, text, error: bool, detailedMode: bool) -> None:
        try:
            if detailedMode:
                printText = vars(text)
            else:
                printText = text
            if error:
                tag = "ERROR"
            else:
                tag = "Printed"

            finalText = f'\n[{datetime.now()}]: {tag} logged with PunkinLogging: {printText}'

            print(finalText)
            with open(self.path, 'a') as file:
                file.write(finalText)
        except Exception as e:
            print("Punkin logging tried to print this:")
            print(text)
            print("But ran into this error:")
            print(e)