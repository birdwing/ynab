# ynab

YNAB component for Home Assistant
This component will retreieve the following data from your YNAB budget

1. To be budgeted amount
2. Current month's budgeted amount
3. Current month's category information
  - Remaining Balance
  - Total Budgeted this month
  - Total Activity this month
  - Goal Type
  - Goal Target
  - Goal Target Month
  - Goal Percentage Complete
5. Current balance of any specified account
6. Number of transactions needing approval
7. Number of uncleared transactions
8. Number of overspent categories

## Update Frequency & YNAB API Rate Limit
To keep api usage low, the sensor updates every 5 minutes which equates to 12 times per hour.  YNAB has a rate limit (<https://api.ynab.com/#rate-limiting>) of 200 requests per hour and that number resets every hour _on the hour_.

## Installation

### HACS

1. Open HACS > Settings
2. In ADD CUSTOM REPOSITORY box paste this git's URL <https://github.com/birdwing/ynab> and select type Integration
3. Click INSTALL
4. Restart Home Assistant

### Manual install

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ynab.
4. Download all the files from the custom_components/ynab/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

### Generate YNAB API key

API:

1. Log on to YNAB
2. Go to My Budget > My Account > Developer Settings
3. Click on New Token
4. Enter your password and click Generate
5. Copy the token that appears at the top of the page

### Setup the integration

1. Navigate to Settings -> Devices & Services on your Home Assistant instance
2. Select "Add Integration" in the bottom right hand corner
3. Search for and select "ynab" from the list
4. Enter your API key from the previous step into the "API Key" field and click submit
5. Your API key will be validated and your budgets retrieved.  Select the budget you want to use from the list
6. Select one or more categories to sync then click "Submit", or if you don't want to sync any categories just click "Submit"
7. Select one or more accounts to sync then click "Submit", or if you don't want to sync any accounts just click "Submit"

The budget is now setup and will start updating automatically.  You can go through the same process to add multiple budgets all of which will be kept updated.