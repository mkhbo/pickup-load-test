# simple script for generating config for pickup_cw_insertion
import sys
import time
from random import randint
from math import log, ceil
import hashlib
from pprint import pprint
import json

def valid_int(i):
    try:
        x = int(i)
        return x > 0 
    except:
        return False

PRODUCT_CODE = 'hboMax'

def get_rand_char():
    return chr(randint(97,122)) if randint(0,1) else chr(randint(65,90))

def calc_bytes_needed(n):
    if n == 0:
        return 1
    return int(log(n, 256)) + 1

def generate_user_id(num_users,num_bytes):
    randNum = randint(0, num_users)
    randNumBytes = randNum.to_bytes(num_bytes, sys.byteorder)
    m = hashlib.sha256(randNumBytes)
    return "PICKUP-LT-" + m.hexdigest()[0:16]

def generate_asset_id(type="feature"):
    return 'urn:'+type+':'+''.join([get_rand_char() for _ in range(21)])

# function for generating random profile IDs for load testing
def get_user_array(num_users):
    num_bytes = calc_bytes_needed(num_users)
    return [
        generate_user_id(num_users, num_bytes) for _ in range(num_users)
    ]

# we need to have a unique asset per record, so we will
# have atleast as many assets as the number of records
# that need to be generated
def get_asset_dict(num_assets):
    # 70% features, 30% episode
    num_features = ceil(0.7*num_assets)
    num_episodes = ceil(0.3*num_assets)
    features = [
        generate_asset_id() for _ in range(num_features)
    ]
    series = {
        generate_asset_id('series'):generate_asset_id('episode') for _ in range(num_episodes)
    }
    return {
        "features":features,
        "series":series
    }

# by default generate num_users records for a duration of 90 days
def generate_config(num_users, duration, records_per_user):        
    config = {}
    config['productCode'] =  PRODUCT_CODE
    config['hurleyUserIds'] = get_user_array(num_users)
    config['assets'] = get_asset_dict(num_users*records_per_user)
    end_time = int(time.time())
    config['updateTimeStart'] = end_time-duration
    config['updateTimeEnd'] = end_time
    config['recordsPerUser'] = records_per_user
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# python config_generator no_of_users no_of_days[OPTIONAL] records_per_user[OPTIONAL]
if __name__== "__main__":
    
    if len(sys.argv) < 2:
        sys.exit('please provide the number of users to generate profileIDs for')
    
    num_users = sys.argv[1]
    num_days = 90
    records_per_user = ceil(num_days/7) # 1 movie per week

    if not valid_int(num_users):
        sys.exit('please provide a positive int for number of users')
    
    if len(sys.argv)==3:
        num_days = sys.argv[2]
        if not valid_int(num_days):
            sys.exit('please provide a positive int for number of days')

    if len(sys.argv)==4:
        records_per_user = sys.argv[3]
        if not valid_int(records_per_user):
            sys.exit('please provide a positive int for number of records per user')

    generate_config(int(num_users), int(num_days), int(records_per_user))
