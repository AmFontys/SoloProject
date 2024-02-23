from flask import Flask, render_template, jsonify, request
import json

##############################
### Methods ##################
##############################

def loadJson():
    f=  open("./templates/example.json")
    data = json.load(f)
    f.close
    return data

def loadJsonInbox():
    f= open("./templates/inbox.json")
    data = json.load(f)
    f.close
    return data

def saveInKnowdledgeBase(file_path: str, data: dict ):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


##############################
########### App ##############
##############################

app = Flask(__name__)

@app.route("/")
def hello(): 
    return render_template('index.html')

@app.route("/Actor")
def actor():
    d= loadJson()
    return jsonify(d)

@app.route("/Inbox")
def inbox():
    d= loadJsonInbox()
    return d

@app.route('/Outbox', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        print(json)
        saveInKnowdledgeBase("./templates/inbox.json", json)
        return json
    else:
        return 'Content-Type not supported!'

  
if __name__=='__main__': 
   app.run(debug=True) 