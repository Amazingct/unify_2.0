import pyrebase
import json
import time
import firebase_admin
#from firebase_admin import credentials, firestore, db

"""
with open("cofig.json") as config_file:
    config = json.loads(config_file.read())


fire_base = pyrebase.initialize_app(config)
auth = fire_base.auth()
database = fire_base.database()

email = input("emial: ")
password = input("password: ")
try:
    user = auth.create_user_with_email_and_password(email, password)
    print("signed up", user)

except Exception as e:
    print("User exits")
    user = auth.sign_in_with_email_and_password(email, password)
    print("logged in", user)


"""
"""
data = {"name": "daniel"}
# post new data with new tag
d = database.child("users").push(data)
print(d)


# update existing tag
time.sleep(10)
data = {"name": "samuel"}
d = database.child("users").child(d["name"]).update(data)


# get data
data = database.child("users").child("-MAWoMkv1kH7E1mjUYDj").get()
print(data.val())

# remove data/user
# database.child("users").child("-MAWoMkv1kH7E1mjUYDj").remove()


data = {"name": "daniel"}
# post new data with new tag
d = database.child("users").child(user).push(data)
print(d)


cred = credentials.Certificate("sdk.json")
firebase_admin.initialize_app(cred, {'databaseURL":"https://unify-has.firebaseio.com/'})

ref = db.reference('/')
ref.set({
    'Employee': {

        {'first':
             {'name': 'daniel'}
         }
    }
})

"""

d = {"name":"daniel", "age":"7"}
print(type(d.keys()))