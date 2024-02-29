import requests
import json
from difflib import get_close_matches
from pathlib import Path
from datetime  import datetime, timedelta, timezone
import time

max_retry: int = 3
retry_num: int =0

def getTime():
    now = datetime.utcnow()
    time = now - timedelta(minutes=10)
    return time

def sleepTime():
    print("Bot is sleeping")
    time.sleep(60)
    print("Bot is awake")


print("start program")

# The API endpoint
url = "http://host.docker.internal:5000/Actor"
print(url)
while True:
    # A GET request to the API
    try:
        response = requests.get(url)
        print("got response")
    except  requests.exceptions.ConnectionError:
        print("Not reachable",url)
        if retry_num <= max_retry:
            retry_num = retry_num+1
            sleepTime()
            continue
        else:
            print("Bot stopped")
            break
    # Print the response
    response_json = response.json()
    # print(response_json)

    # A GET request to the API for the inbox
    request_Inbox = response_json["inbox"]
    try:
        response = requests.get(request_Inbox)
    except  requests.exceptions.ConnectionError:
        print("Not reachable",request_Inbox)
        if retry_num < max_retry:
            retry_num = retry_num+1
            sleepTime()
            continue
        else:
            print("Bot stopped")
            break

    response_inbox_json = response.json()
    # print(response_inbox_json)
    filtered_inbox_json: dict = {"posts": []}

    def compareTime(getTime, cat): #23-02-2024:12:15:00
        date = datetime.strptime(cat["date"],'%d-%m-%Y:%H:%M:%S')
        return date >= getTime()

    for cat in response_inbox_json["posts"]:  
        if cat["category"] == "search" and compareTime(getTime, cat)==True: 
            filtered_inbox_json["posts"].append(cat)
        

    print(filtered_inbox_json)

    ############################################
    ############ Chatbot #######################
    ############################################

    script_location: str = Path(__file__).absolute().parent.__str__()

    def load_knowledge_base(file_path: str) -> dict:
        with open(file_path, 'r') as file:
            data: dict = json.load(file)
        return data

    def save_knowledge_base(file_path: str, data: dict ):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def find_best_matches(user_question: str, questions: list[str]) -> str | None:
        matches: list = get_close_matches(user_question,questions,n=1,cutoff=0.6)
        return matches[0] if matches else None

    def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
        for q in knowledge_base["questions"]:
            if q["question"] == question:
                return q["answer"]
            

    def chat_bot(input_request: str):
        location_knowledge_base: str = script_location+"/knowledge_base.json"
        knowledge_base: dict = load_knowledge_base(location_knowledge_base)

        # while True:
        user_input: str = input_request #input('You: ')
        print(user_input)

        #if user_input.lower() == 'quit':
            # break

        best_match: str | None = find_best_matches(user_input, [q["question"] for q in knowledge_base['questions']])

        if best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            print(f'Bot: {answer}')
            currentTime: str = getTime().strftime('%d-%m-%Y:%H:%M:%S')
            print(currentTime)
            return {"post": answer, "date": currentTime, "category": "search_response"}  
        else:
            print("Bot: IDK the answer. Can you teach me?")
            new_answer: str = input('Type the answer or "skip" to skip: ')

            if new_answer.lower() != 'skip':
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base(location_knowledge_base,knowledge_base)
                print('Bot: Thank you?! I learned a new response')

    response_data = None
    for response_post in filtered_inbox_json["posts"]:
        response_data: dict = chat_bot(response_post["post"])

    print("chatbot done")

    if(response_data != None): 
        print(response_data)   
        response_inbox_json["posts"].append(response_data)

        print(response_inbox_json)

        url_post = response_json["outbox"]
        print(url_post)
        # A POST request to tthe API
        post_response = requests.post(url_post, json=response_inbox_json)

        # Print the response
        post_response_json = post_response.json()
        print(post_response_json)
        print("response posted")
    
    retry_num = 0
    sleepTime()