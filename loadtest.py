from locust import HttpUser, TaskSet, task, constant_pacing, between
import sys
import json
from random import randint
from token_generator import TokenGenerator
import threading

REQUEST_TIMEOUT_SEC=5
threading_lock = threading.Lock()


config=None
try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())
except Exception as e:
    sys.exit('unable to load config.json\n{0}'.format(e))

hurleyUserIds = None
try:
    hurleyUserIds = config['hurleyUserIds']
    if not (hurleyUserIds and len(hurleyUserIds)):
        raise Exception('hurleyUserId data empty in config')
except Exception as e:
    sys.exit('error loading test user IDs, {0}'.format(e))

tg, num_users = TokenGenerator(), len(hurleyUserIds)

def get_random_user_token():
    return 

def get_user_id():
    with threading_lock:
        if len(hurleyUserIds):
            return hurleyUserIds.pop()
        raise Exception('number of users spawned greater than unique available user IDs')

class PickupUser(HttpUser):
   
    wait_time = between(0,5)
    host = 'https://pickup-snp.development.hurley.hbo.com'

    def on_start(self):
        #unique user id
        self.user_id = get_user_id()
        print(self.user_id)
        #generate token for it
        self.token = 'Bearer {}'.format(tg.get_token(self.user_id))
    
    @task(100)
    def get_continue_watching_history(self):
        with self.client.get("/continuewatchinghistory", headers={"Authorization": self.token}, timeout=REQUEST_TIMEOUT_SEC, catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Status = {r.status_code}")
            # print(r.json())

