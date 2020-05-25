import json
import requests
from flask import Flask, request
import os

app = Flask(__name__)
bot_id = os.environ['botID']
group_id = os.environ['groupID']
token = os.environ['token']

# Called on GET
@app.route('/', methods=['GET'])
def home():
    return "Hello! Welcome!"

# Called upon callback gets a POST
@app.route('/', methods=['POST'])
def webhook():
    message = request.get_json()

    #if message has a mentions, the sender is not a bot, and our botID is mentioned, reply back)
    if (('Bot, insult @' in message["text"]) and not senderIsBot(message)):
        #get the user_id of who we want to insult
        respondToID = findWhoToInsult(message) 

        #get the name from the userID
        userName = findNameByID(respondToID)

        #respond to the user with an insult
        respond(getInsult(), respondToID, userName)
    elif (('Bot, compliment @' in message["text"]) and not senderIsBot(message)):
        #get user_id
        respondToID = findWhoToInsult(message)

        userName = findNameByID(respondToID)

        respond(getCompliment(), respondToID, userName)
    else:
        if (senderIsBot(message)):
            print("LOG: Sender was a bot")

    return "ok", 200

def getCompliment():
    url = "https://complimentr.com/api"
    
    response = requests.get(url)
    return response.json()['compliment']

# get the sender's user_id
def findWhoToInsult(message):
    return message['attachments'][0]["user_ids"][0]

# get the name of who we want to insult given their ID
def findNameByID(IDnum):
    #Endpoint for getting group stats
    url = 'https://api.groupme.com/v3/groups/' + str(group_id) + str(token)
    
    #submit request for data
    response = requests.get(url)
    print("LOG: request for group is: " + str(response.status_code))
    data = response.json()

    #iterate over members to get the name
    mems = data["response"]["members"]
    
    for mem in mems:
        if (str(IDnum) == mem["user_id"]):
            return mem["nickname"]

    print("LOG: didn't find a match on name")


# send a message
def respond(msg, recID, name):
    #Endpoint for posting a message
    url = 'https://api.groupme.com/v3/bots/post'

    #Create the payload
    data = {}
    data["bot_id"] = bot_id
    data["text"] = "@" + name + ", " + msg
    print("LOG: sent text is " + data["text"])
    data["attachments"] = [{"type":"mentions","user_ids":[str(recID)],"loci":[[0,len(name)]]}]

    #Form and send payload
    response = requests.post(url, data)
    print("LOG: Post to new comment: " + str(response.status_code))
    

# determine if who just sent the message is a bot
def senderIsBot(message):
    return (message['sender_type'] == "bot")

# Get an insult message
def getInsult():
    #get the insult from https://evilinsult.com/generate_insult.php?lang=en&type=json
    url = 'https://evilinsult.com/generate_insult.php?lang=en&type=json'
    response = requests.get(url)
    print("LOG: Request for insult: " + str(response.status_code))

    #Get the insult into text form for upload to the message
    insult = response.json()["insult"]

    return insult
