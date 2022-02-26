# basic singleton pattern to read config once and use it everywhere
import json

config = None

# basic tests for making sure config is sane
def validated_config(config):
    # TODO :: STEP 1 - check all keys are present

    # TODO :: STEP 2 - validate date types

    # STEP 3 - the total number of records
    # to be inserted for a user should be exactly
    # equal to the number of assets provided - why?
    # because for cw - each user will have one record
    # per asset (feature or episode)
    feature_count = len(config['assets']['features'])
    episode_count = len(config['assets']['series'])
    if int(config['recordsPerUser']) > feature_count + episode_count:
        raise Exception('Not enough assets per user for ingestion. Each record needs a unique asset!')
    return config

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return validated_config(json.loads(config_file.read()))
    except Exception as e:
        print(e)
        exit(-1)

if not config:
    config = load_config()









