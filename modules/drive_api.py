def update_artists_list():                      # download new copy of artists-new.json from google drive if updated
    print("nothing to see here")

def get_file_list():                            # retrieve a list of already uploaded images
    import random
    import datetime
    import logging
    from googleapiclient.discovery import build                                         # pip install google-api-python-client
    from google.oauth2 import service_account
    from dateutil.relativedelta import relativedelta
    from data.env import AUTH_SCOPE, SERVICE_ACCOUNT_FILE
    from data.config import DRIVE_FOLDER_ID

    logger = logging.getLogger(__name__)
    
    DATE = (datetime.datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%dT%X")   # today - 3 years ago
    QUERY = (
        f"mimeType='image/jpeg' and "
        f"modifiedTime > '{DATE}' and "
        f"'{DRIVE_FOLDER_ID}' in parents"
    )
    # '{OWNER}' in owners # orderBy

    try:
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, 
                                                                            scopes=AUTH_SCOPE)
        service = build('drive', 'v3', credentials=credentials)
        logger.debug("credentials built")
        results = service.files().list(pageSize=1000, 
                                       spaces='drive', 
                                       fields="nextPageToken, files(id, name, webContentLink)", 
                                       q=QUERY).execute()
        file_list = [(d['webContentLink'], "slideshow") for d in results['files']]
        logger.debug(f"Found [{len(file_list)}] files")
        random.shuffle(file_list)
        del file_list[5:]
        return file_list
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return [("images/slideshow-error.png", "slide")]

def upload_image(file_path):
    import os
    import json
    import logging
    from data.env import AUTH_SCOPE, SERVICE_ACCOUNT_FILE
    from data.config import DRIVE_FOLDER_ID

    logger = logging.getLogger(__name__)
    logger.info(f"saving artimage: {file_path}")

    try:
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except Exception as error:
        logger.error(f'An import error occurred: {error}')
        return
    
    file_name = os.path.basename(file_path)
    QUERY = f"name='{file_name}' and '{DRIVE_FOLDER_ID}' in parents"                    # mimeType='image/jpeg' and name='2023-09-24-vermeer-IF.jpg'
    
    # 2024-09-17 12:24:01,771:googleapiclient.discovery:WARNING:media_mime_type argument not specified: trying to auto-detect for generated/2024-09-17-lowry-sJ.jpg

    try:
        logger.debug("starting credentials build")
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=AUTH_SCOPE)
        service = build('drive', 'v3', credentials=credentials)
        logger.debug("credentials built")

        results = service.files().list(pageSize=1000, 
                                       spaces='drive', 
                                       fields="nextPageToken, files(id, name, description, properties)", 
                                       q=QUERY).execute()
        files = results.get('files', [])
        logger.debug(f"retrieved files: {files}")

        if files:                                                                       # if list not empty
            logger.info("file already found in drive")                                  # do nothing
        else:                                                                           # list empty, upload
            logger.debug("file not found in drive")

            with open("data/image-metadata.json", "r") as fp:
                metadata = json.load(fp)
            file_metadata = {
                            'name' : file_name,
                            'description': f'{metadata["prompt"]}|{metadata["seed"]}|{metadata["cost"]}',
                            'parents' : [DRIVE_FOLDER_ID],
                            'properties': {
                                           'steps' : metadata["steps"],
                                           'model' : metadata["model"]
                                          }          
                            }
            media = MediaFileUpload(file_path, mimetype="image/jpeg")
            # media_mime_type = 'image/jpeg'
            file = (
                service.files()
                .create(body=file_metadata, media_body=media)
                .execute()
            )
            logger.info(f"file {file_name} uploaded to google drive")
    except Exception as error:
        logger.error(f"an error occurred: {error}")