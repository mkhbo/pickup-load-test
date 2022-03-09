# Pickup-api Load Test

### Summary

This load test was written for the following tickets: 

- [GA-90902](https://jira.dp.hbo.com/browse/GA-90902)
-  [GA-90903](https://jira.dp.hbo.com/browse/GA-90903)

Helps insert data in SNP dynamoDB for running a pickup-api load test.

---
Following is the description of files/folders included in this repo:

#### Files
- `loadtest.py` - Script for running load tests using locust

- `pickup_cw_insertion.py` - Script for inserting data into `pickup-cw-snp` table in SNP DynamoDB. It uses `config.json` for the generating fake markers data using listed users and assets.

- `config_generator.py` - Script for generating `config.json` to be used for insertion. It is helpful for bulk profileID and assetID generation. 

- `config.json` - Schema for validating `config.json`. This shouldn't be changed unless there's a change introduced in the config schema.

- `config_reader.py` - Script for validating and loading `config.json` in memory. Used by pickup_cw_insertion.py.

- `token_generator.py` - Helps generate tokens for test profileIDs using Hurley-Token service.

- `requirements.text` - pip requirements for this project

#### Folders
- `aws_cli_utils` - Folder containing aws cli commands for insertion/reading data from DynamoDB. This can be used for authenticating/authorizing before running pickup_cw_insertion.py
- `token_payloads` - Payloads for token-service, used by token_generator.py
---
### Setup on local machine
This is a typical python installation.
-   `git clone <repo>`
-   `cd <repo>`
-   `pip install virtualenv`  (if you don't already have virtualenv installed)
-   `virtualenv venv`  to create your new environment (called 'venv' here)
-   `source venv/bin/activate`  to enter the virtual environment
-   `pip install -r requirements.txt`  to install the requirements in the current environment

---
### Steps to run this load test


1. Run `perform get-okta-aws-keys` and get aws credentials for `user-developer` role.

2. Use `config_generator.py` to generate `config.json` for DDB insertion.

> 	python config_generator.py <no_of_users> <no_of_days> <no_of_records_per_user>
- *no_of_users* - number of users to run the load test for
- *no_of_days* - number of days from today into past for creating fake markers. Default : 90 days.
- *no_of_records_per_user* - number of records to be generated for each user. This records will be uniformly distributed in the time range [now, now-no_of_days]
> 
> You can also list down profileIDs you want  to insert markers for (for
> eg: your SNP profileID) or assets that you want the users to have
> markers for.

3. Run `python pickup_cw_insertion.py`. Open a new terminal to tail the `runtime.log` log file for updated logs. Use `tail -f runtime.log`. The script currently has an exception threshold of `5`, which means it'll shut after encountering `5` exceptions. Requests are made in a batch size of 25 records(why?) and a collective response for each batch is logged. `unprocessedItems` key in response lists records which failed to insert. Ideally, we shouldn't have a lot of unprocessed Items. This script can be improved by introducing async insertion and retry using exponential backoff (read here), but was out of scope for this implementation.

4. We can verify insertion using either AWS DDB console or [querying pickup-api](https://www.getpostman.com/collections/cb93299b8b71034cc610) (through postman) using a token of a profileID we generated markers for. The token can be generated via postman as well.

5. After making sure that the data ingestion was successful, you'll now need to change the `cutOffInDays` [parameter in configs](https://github.com/HBOCodeLabs/pickup/blob/e341b026cf6c9b155cbb343fe1a37f032f62d13e/master.config.json#L258) in accordance to the number of days in history you want to retrieve markers for. You might also want to change the `continueWatchingLimit` in case you are expecting more markers to be returned than specified in the config.

6. You are now ready to run the load test! 
	
> locust -f loadtest.py

    [2022-03-08 18:07:52,373] Mohits-MacBook-Pro.local/INFO/locust.main: Starting web interface at http://0.0.0.0:8089 (accepting connections from all network interfaces)
    [2022-03-08 18:07:52,384] Mohits-MacBook-Pro.local/INFO/locust.main: Starting Locust 2.8.3
Hop onto `http://0.0.0.0:8089` to run locust using a web interface.

![Locust web interface](https://docs.locust.io/en/stable/_images/webui-splash-screenshot.png)

Make sure the number of users you spawn are equal to the number of users mentioned in the config or the load test will throw an exception. Each of user gets his own thread and fires a `/continuewatchinghistory` request b/w a random wait time of 1 to 5 seconds. 

Press the stop button in top right corner to stop locust from firing requests. (Don't do a CTRL+C on the terminal as we want the local server to keep running to download test report). Now go to download data to download load test statistics.

![Locust statistics screenshot](https://docs.locust.io/en/stable/_images/webui-running-statistics.png)

----
### References
- Pickup Design 
- Locust Documentation 
- DynamoDB SDK Documentation 
- Pickup API Documentation
---