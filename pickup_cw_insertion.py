from pprint import pformat, pprint
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from collections import defaultdict
import json
from decimal import *
from random import randrange
import time
import logging
from config_reader import config

DDB_RESOURCE_STRING = 'dynamodb'
DDB_SNP_ENDPOINT = 'us-west-2'
TABLE_NAME = 'pickup-cw-snp'
PUT_REQUEST = 'PutRequest'
BATCH_SIZE = 25
LOG_FILE_NAME = 'runtime'
EXCEPTION_THRESHOLD = 5

client = boto3.client(DDB_RESOURCE_STRING, DDB_SNP_ENDPOINT)

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler("{0}.log".format(LOG_FILE_NAME), mode='w')
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

# util function to get records by profile and parent
def get_record(prof, parent,ddb_client=None):
    if not ddb_client:
        ddb_client = boto3.resource(DDB_RESOURCE_STRING, DDB_SNP_ENDPOINT)
    table = ddb_client.Table(TABLE_NAME)
    try:
        response = table.get_item(Key={
                "prof": prof,
                "parent": parent
            })
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(response['Item'])
 
def generate_asset():
    for feature in config['assets']['features']:
        yield feature
    for series, episode in config['assets']['series'].items():
        yield (series, episode)

# generator for generating an item
def generate_item():
    start_time = int(config['updateTimeStart'])
    end_time = int(config['updateTimeEnd'])
    users = config['hurleyUserIds']
    for user in users:
        for unique_asset in generate_asset():
            item = {}
            item['PutRequest'] = {}
            item['PutRequest']['Item'] = {
                    "prof": {"S":user},
                    "parent": {"S":unique_asset[0] if len(unique_asset)==2 else unique_asset},
                    "aws:rep:deleting": {"BOOL":False},
                    "showcw": {"BOOL":True},
                    "time": {"N":str(time.time())},
                    "aws:rep:updateregion": {"S":"us-west-2"},
                    "aws:rep:updatetime": {"N":str(randrange(start_time, end_time))+"."+str(randrange(500000,600000))},
                    "done": {"BOOL":False}
                }            
            if len(unique_asset)==2:
                item['PutRequest']['Item']['asset'] = {"S":unique_asset[1]}
            else:
                item['PutRequest']['Item']['asset'] = {"NULL": True}
            yield item

def log_request_response(batch_id, request, response):
    logger.info('-'*50+'BATCH '+str(batch_id)+'-'*50)
    logger.info(request)
    logger.info(pformat(response))
    logger.info('-'*100)

def make_batch_call(batch_of_items):
    return client.batch_write_item(
                RequestItems = {
                    TABLE_NAME:batch_of_items,
                },
                ReturnConsumedCapacity = 'TOTAL'
            )

def main():    
    # this loop generates records for ingestion
    # using a generator . Try to batch write 
    # records in a set of BATCH_SIZE & log 
    # the response in a log file.
    # The response contains UnprocessedItems
    # for each of the batch requests made. 

    # PHASE 2 : To give the program a better capability
    # we can include retry on unprocessed items
    # using async tasks
    print('starting ingestion...')
    batch_number = 0
    item_generator = generate_item()
    total_records_generated = 0
    run_loop = True
    exception_count = 0
    
    while run_loop and total_records_generated < (len(config['hurleyUserIds'])*config['recordsPerUser']):
        
        try:
            # STEP 1 : create a batch request
            logger.info('creating next batch of records')
            next_batch_of_items = []
            try:
                for _ in range(BATCH_SIZE):
                    next_batch_of_items.append(next(item_generator))
            except StopIteration as e:
                # incomplete batch
                pass
            
            # STEP 2: make batch request and log response
            response = make_batch_call(next_batch_of_items)
            log_request_response(batch_number+1, next_batch_of_items, response)

        except Exception as e:
            exception_count += 1
            logger.error('exception count : {0}'.format(exception_count))
            logger.error(e)
            if exception_count == EXCEPTION_THRESHOLD:
                run_loop = False
        
        batch_number+=1
        
        # STEP 3 : loop invariant
        total_records_generated += BATCH_SIZE
    print('ingestion ended, please check logs for more details...')

main()