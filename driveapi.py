#pip install google-api-python-client

def update_artists_list():
    # download new copy of artists-new.json from google drive if updated
    print("nothing to see here")
    
def get_file_list():
    import datetime
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from dateutil.relativedelta import relativedelta
    from config import DRIVE_FOLDER_ID
    from constants import DEBUG, AUTH_SCOPE

    SERVICE_ACCOUNT_FILE = 'service_account.json'
    DATE = (datetime.datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%dT%X")           # today - 3 years ago
    if DEBUG: print(f"DATE contains: {DATE}")
    QUERY = f"mimeType='image/jpeg' and modifiedTime > '{DATE}' and '{DRIVE_FOLDER_ID}' in parents"
    # '{OWNER}' in owners # orderBy

    try:
        print("starting try for files().list")
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=AUTH_SCOPE)
        service = build('drive', 'v3', credentials=credentials)
        if DEBUG: print("credentials built")
        results = service.files().list(pageSize=1000, spaces='drive', fields="nextPageToken, files(id, name, webContentLink)", q=QUERY).execute()
        files = results.get('files', [])
        if DEBUG: print(f"Found [{len(files)}] files")
        return files

    except Exception as error:
        print(F'An error occurred: {error}')
        return [ {"webContentLink" : "images/slideshow-error.png"} ]


def upload_image(file_path):
    import os
    import json
    from config import DRIVE_FOLDER_ID
    from constants import DEBUG, AUTH_SCOPE

    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except Exception as error:
        print(f'An import error occurred: {error}')
        return
    
    file_name = os.path.basename(file_path)
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    QUERY = f"name='{file_name}' and '{DRIVE_FOLDER_ID}' in parents"           # mimeType='image/jpeg' and name='2023-09-24-vermeer-IF.jpg'
    
    try:
        if DEBUG: print("starting try")
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=AUTH_SCOPE)
        service = build('drive', 'v3', credentials=credentials)
        if DEBUG: print("credentials built")

        results = service.files().list(pageSize=1000, spaces='drive', fields="nextPageToken, files(id, name, description, properties)", q=QUERY).execute()
        files = results.get('files', [])
        if DEBUG: print(f"printing files\n{files}")
 
        if files:                                                                               # list not empty
            if DEBUG: print("file already found in drive")                                      # do nothing
        else:                                                                                   # list empty
            if DEBUG: print("file not found in drive")

            with open("file_metadata.json", "r") as fp:
                metadata = json.load(fp)

            file_metadata = {
                            'name' : file_name,
                            'description': metadata["prompt"] + "|" + str(metadata["seed"]) + "|" + str(metadata["cost"]),
                            'parents' : [DRIVE_FOLDER_ID],
                            'properties': {
                                           'steps' : metadata["steps"],
                                           'model' : metadata["model"]
                                          }          
                            }
            file = service.files().create(body=file_metadata, media_body=file_path).execute()
            print(f"File {file_name} uploaded to google drive")
    except Exception as error:
        print(f'An error occurred: {error}')