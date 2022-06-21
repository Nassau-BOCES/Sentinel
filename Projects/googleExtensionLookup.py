import logging
import bs4
import azure.functions as func
import requests
import os
import pyodbc

def inputIntoDB(conn, id):	#Make a re-usable function; we might need to input multiple times based on the json recieved
	html = requests.get(f"https://chrome.google.com/webstore/detail/{id}").text #Get the HTML code from the Chrome Webstore
	soup = bs4.BeautifulSoup(html)												#Make it a soup object
	title = soup.title.string[:-19]												#Get the title of the webpage (ex. "Google Drive - Chrome Web Store")
	#logging.info(title,html)																			#Use [:-19] to strip off the unnecessary information (" - Chrome Web Store")
	command = f"Begin IF NOT EXISTS (SELECT * FROM chromeextensions WHERE extensionid ='{id}') Begin INSERT INTO dbo.chromeextensions(extensionid,extensionname) VALUES('{id}','{title}') END END"
	cursor = conn.cursor()																			#Create command to input into database if it doesn't exist already
	cursor.execute(command)														#Run the command using pyodbc
	conn.commit()	

def main(req: func.HttpRequest) -> func.HttpResponse:
    #logging.info('Python HTTP trigger function processed a request.')
    #"", status_code=200
    #name = req.params.get('name')
    json = req.get_json()
    #json = req.get_body()
    #raise Exception(json[0]["id"])
    logging.info('Python HTTP trigger function processed a request.')
    server="sentdb.database.windows.net"
    database="sent-db"
    driver="{ODBC Driver 17 for SQL Server}"
    #query= """INSERT INTO dnstwist (domainname) VALUES ('3.4.3.5')"""
    #query= "SELECT * FROM dbo.dnstwist"
    # Optional to use username and password for authentication
    # username = 'name' 
    # password = 'pass'
    db_token = ''
    connection_string = 'DRIVER='+driver+';SERVER='+server+';DATABASE='+database
    #When MSI is enabled
   # if os.getenv("MSI_SECRET"):
    conn = pyodbc.connect(connection_string+';Authentication=ActiveDirectoryMsi')
    #cursor = conn.cursor()
    #logging.info('Within the os.getENV If Statement.')
    for body in json:
        #logging.info('Started in the loop')
        if body["kind"] == "Malware":
            extension = body["properties"]["malwareName"]
            #logging.info('Within the If Body equals malware for loop',":",extension)
            inputIntoDB(conn,extension)

    return func.HttpResponse(f"Received the message: {json}", status_code=200)	
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )
