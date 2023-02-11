from venmo_api import Client

with open('access_token.txt', 'r') as file:
    access_token = file.read().rstrip()

client = Client(access_token=access_token)

def callback(transactions_list):
    for transaction in transactions_list:
        print(transaction)

# callback is optional. Max number of transactions per request is 50.
client.user.get_user_transactions(user_id='2555599778742272054',
                                     callback=callback)