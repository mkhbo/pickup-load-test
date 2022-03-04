# basic singleton pattern to read config once and use it everywhere
import json
import jsonschema
import time
import sys

config = None

END_TIME = int(time.time())
START_TIME = END_TIME - 157680000 # we can only go back 5 years

# basic tests for making sure config is sane
def validated_config(config):

    # STEP1 : import schema - run validation for basic sanity
    with open('config_schema.json', 'r') as f:
        schema_data = f.read()
        schema = json.loads(schema_data)
    schema = json.loads(schema_data)
    jsonschema.validate(config, schema)

    # STEP 2 : validate epochs
    if config['updateTimeStart'] not in range(START_TIME, END_TIME):
        raise('updateTimeStart should be b/w [now-5years, now]')
    if config['updateTimeEnd'] not in range(START_TIME, END_TIME):
        raise('updateTimeEnd should be b/w [now-5years, now]')
    
    # STEP 3 : the total number of records
    # to be inserted for a user should be exactly
    # equal to the number of assets provided - why?
    # because for cw - each user will have one record
    # per asset (feature or episode)
    feature_count = len(config['assets']['features'])
    if int(config['recordsPerUser']) > feature_count:
        raise Exception('Not enough assets per user for ingestion. Each record needs a unique asset!')
    return config

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return validated_config(json.loads(config_file.read()))
    except KeyError as missingKey:
        sys.exit('missing key {0} in config'.format(missingKey))
    except Exception as e:
        sys.exit(e)

if not config:
    config = load_config()









