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

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] {%(pathname)s:%(lineno)d} [%(levelname)-5.5s]  %(message)s")
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
    
# generator for generating an item
def generate_item():
    start_time = int(config['updateTimeStart'])
    end_time = int(config['updateTimeEnd'])
    users = config['hurleyUserIds']
    product_code = config['productCode']
    for user in users:
        for unique_asset in generate_asset():
            item = {}
            item['PutRequest'] = {}
            item['PutRequest']['Item'] = {
                    "prof": {"S":user+':'+product_code},
                    "parent": {"S":unique_asset},
                    "asset":{"NULL":True},
                    "showcw": {"BOOL":True},
                    "runtime":{"N":str(randrange(5000,8000))},
                    "ttl":{"N":str(int(time.time())+2*365*24*3600)}, # 2 years from now
                    "time": {"N":str(round(time.time() * 1000))},
                    "position":{"N":str(randrange(500,1000))},
                    "done": {"BOOL":False}
                }
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
    total_record_count = len(config['hurleyUserIds'])*config['recordsPerUser']
    current_record_count = 0

    while run_loop and current_record_count < total_record_count:
        try:
            # STEP 1 : create a batch request
            logger.info('creating next batch of records')
            next_batch_of_items = []
            remaining_record_count = total_record_count-current_record_count
            try:
                for _ in range(min(remaining_record_count,BATCH_SIZE)):
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
            print('encountered exception in ingestion, please check logs for more details...')
        batch_number+=1
        
        # STEP 3 : loop invariant
        current_record_count += BATCH_SIZE

main()