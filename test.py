import venmo_api as venmo
import emoji
import pandas as pd

def update_user_entry(user: venmo.models.user.User, transaction, data):
    if not user.id in data:
        data[user.id] = [
            user.id,
            user.display_name,
            [transaction.date_created]
        ]
    else:
        data[user.id][2].append(transaction.date_created)

with open('access_token.txt', 'r') as file:
    access_token = file.read().rstrip()

client = venmo.Client(access_token=access_token)

transactions_list = client.user.get_user_transactions(user_id='2555599778742272054')
transactions_dict = {}
users_dict = {}
for t in transactions_list:
    # add transaction to data dict
    payer = t.target if t.payment_type == 'charge' else  t.actor
    payee = t.actor if t.payment_type == 'charge' else  t.target
    transactions_dict[t.id] = [
        payer.id,
        payee.id,
        'Directed',
        t.id,
        emoji.demojize(t.note),
        t.date_created,
        t.amount
    ]

    # add/update user entry in data dict
    update_user_entry(payer, t, users_dict)
    update_user_entry(payee, t, users_dict)

transactions_df = pd.DataFrame.from_dict(transactions_dict, orient='index', columns=[
    'Source',
    'Target',
    'Type',
    'Id',
    'Label',
    'Timestamp',
    'Amount'
])
users_df = pd.DataFrame.from_dict(users_dict, orient='index', columns=[
    'Id',
    'Label',
    'Timestamp'
])

transactions_df.to_csv('transactions_test.csv', index=False)
users_df.to_csv('users_test.csv', index=False)