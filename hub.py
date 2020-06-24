import unify
import time
# unify.sign_up()
user = unify.sign_in()
hub = unify.Hub(user)


hub.start_sync_firebase_clients_localdb_thread()
# give hub time to download database
time.sleep(5)
hub.start_connection_thread()

# unify.logout()
