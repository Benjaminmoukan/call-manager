from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import mysql.connector

host = "..."
user = "..." # user name
password = "..." # password
database = "..." # db name

# Create a connection
# connection, cursor = None, None

def create_connection():
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor()
    return connection, cursor

# different variables we will need
person, numero, raison, frequence = "", "", "", ""

# different queries
yet_to_call_query = "SELECT personne, numero, raison FROM today_calls WHERE was_called = 'NON'"
already_called_query = "SELECT personne FROM today_calls WHERE was_called = 'OUI'"


app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    
    intent = payload['queryResult']['intent']['displayName']
    answer = ""
    connection, cursor = create_connection()

    if intent == 'know-persons-to-call':
        cursor.execute(yet_to_call_query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            answer = "Il semblerait qu'il n'y ait pas (ou plus du tout) de personnes à appeler aujourd'hui."
        else:
            answer = "Voici les personnes à appeler :\n"
            for row in rows:
                personne, numero, raison = row
                answer += f"{personne}, {numero} : {raison}\n"

    
    elif intent == 'delete-called-person':
        personnes_object = payload['queryResult']['parameters']['person']
        personnes = set()
        for p in personnes_object:
            personnes.add(p['name'])

        cursor.execute(already_called_query)
        rows = cursor.fetchall()
        already_persons = list(map(lambda row: row[0], rows))
        already_lower = [person.lower() for person in already_persons]

        cursor.execute(yet_to_call_query)
        rows = cursor.fetchall()
        yet_persons = list(map(lambda row: row[0], rows))
        yet_lower = [person.lower() for person in yet_persons]

        for p in personnes:
            personne = p.lower()
            found = False
            for i, y in enumerate(yet_lower):
                if personne in y:
                    answer += yet_persons[i] + ", OK !\n"
                    mark_as_called_query = f"UPDATE `calls_db`.`today_calls` SET `was_called` = 'OUI' WHERE personne = '{yet_persons[i]}'"
                    cursor.execute(mark_as_called_query)
                    connection.commit()
                    found = True
                    break # on suppose pour le moment qu'il y a au-plus 1 match possible dans la BD
            if found:
                continue

            for i, a in enumerate(already_lower):
                if personne in a:
                    answer += "Il semblerait que tu aies déjà appelé " + already_persons[i] + "...\n"
                    found = True
                    break
            if found:
                continue

            answer += p + " ne fait pas partie des personnes à appeler, semble-t-il.\n"
        
    cursor.close()
    connection.close()

    return JSONResponse(content={
            "fulfillmentText": answer
    })
        

