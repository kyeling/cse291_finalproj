import venmo_api as venmo
import emoji
import pandas as pd
import time

with open('access_token.txt', 'r') as file:
    access_token = file.read().rstrip()
client = venmo.Client(access_token=access_token)

def paginate_transactions(client: venmo.Client, user_id, max_pages=None):
    transactions = client.user.get_user_transactions(user_id=user_id)
    pages = [transactions]
    i = 0
    # continue only if there are still more pages and we have not
    # yet reached the max pages limit
    while transactions and not (max_pages is not None and i >= max_pages-1):
        i += 1
        transactions = transactions.get_next_page()
        pages.append(transactions)
    return pages

def paginate_explore(client: venmo.Client, seed_user, degree, max_pages_per_user=None):
    user_pages = {}
    # users are explored when we have paginated their transactions
    explored_users = set()
    # users are in the frontier when they are not explored but they share a
    # transaction with a user in the explored set
    frontier_users = set([seed_user])
    start = time.time()
    for d in range(degree):
        # get all new neighbors of all users in frontier
        # users are new if they are neither explored nor in the frontier set
        new_users = set()
        for user in frontier_users:
            print(time.time()-start)
            explored_users.add(user)
            # get all new neighbors of a user in frontier
            pages = paginate_transactions(client, user, max_pages=max_pages_per_user)
            for transactions in pages:
                for t in transactions:
                    actor = t.actor.id
                    target = t.target.id
                    if actor not in explored_users and actor not in frontier_users:
                        new_users.add(actor)
                    if target not in explored_users and target not in frontier_users:
                        new_users.add(target)
            # record user's paged transactions
            user_pages[user] = pages
        # update frontier
        frontier_users = new_users
    return user_pages

def update_user_entry(user: venmo.User, transaction: venmo.Transaction, data):
    if not user.id in data:
        data[user.id] = [
            user.id,
            user.display_name,
            [transaction.date_created]
        ]
    else:
        data[user.id][2].append(transaction.date_created)

user_pages = paginate_explore(client, '2555599778742272054', 2, max_pages_per_user=1)
transactions_dict = {}
users_dict = {}
for pages in user_pages.values():
    for transactions in pages:
        for t in transactions:
            # skip duplicate transactions
            if t.id in transactions_dict:
                continue

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