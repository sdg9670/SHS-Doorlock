from firebase_admin import credentials, storage
import firebase_admin

cred = credentials.Certificate("nabot-application-firebase-adminsdk-x0hvu-f51523847e.json")
firebase_admin.initialize_app(cred, {
    'storageBucket':'nabot-application.appspot.com'
})



def upload(file, name):
    bucket = storage.bucket('nabot-application.appspot.com')
    blob = bucket.blob(name)
    outfile = file

    with open(outfile,"rb") as my_file:
        blob.upload_from_file(my_file)

def download(name):
    bucket = storage.bucket('nabot-application.appspot.com')
    blob = bucket.get_blob(name)

    if blob:
        return True
    else:
        return False

def path(name):
    bucket = storage.bucket('nabot-application.appspot.com')
    path = bucket.path_helper(name)

    return path

