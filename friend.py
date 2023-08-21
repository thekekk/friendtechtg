import friendtech
import tweepy
import requests
from datetime import datetime, timezone, timedelta
from telegram import Bot
import asyncio
import time

# Add your API keys and tokens here
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# Etherscan API Key (replace with your BASE API key)
etherscan_api_key = ''

# Telegram bot token (replace with your bot's API token)
telegram_bot_token = '6A'

# Initialize the Telegram bot
bot = Bot(token=telegram_bot_token)
chat_id = '-'

# UTC+3 timezone offset (3 hours)
utc_offset = timedelta(hours=3)

# Store processed addresses in a set
processed_addresses = set()

# Authenticate with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create a Tweepy API object
api = tweepy.API(auth)

# Define your get_first_transaction function
def get_first_transaction(address):
    try:
        # Get the list of transactions for the address
        etherscan_url = f'https://api.basescan.org/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={etherscan_api_key}'
        response = requests.get(etherscan_url)
        data = response.json()

        if data['status'] == '1' and data['message'] == 'OK':
            transactions = data['result']
            if len(transactions) > 0:
                first_transaction = transactions[0]
                return first_transaction
    except Exception as e:
        print(f"Error: {e}")
    return None

# Define your format_timestamp_to_utc3 function
def format_timestamp_to_utc3(timestamp):
    try:
        # Convert timestamp to a datetime object
        timestamp_datetime = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        # Apply UTC+3 timezone offset
        timestamp_utc3 = timestamp_datetime + utc_offset
        # Format the timestamp to a string
        formatted_timestamp = timestamp_utc3.strftime('%Y-%m-%d %H:%M:%S UTC+3')
        return formatted_timestamp
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
    return None

# Define your friend function
def friend():
    platform = friendtech.Platform()
    recentlyJoined = platform.getRecentlyJoinedUsers().json()
    return recentlyJoined

# Define your send_telegram_message function
async def send_telegram_message(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Error sending message: {e}")

# Define your main function
async def main():
    while True:
        recentlyJoinedData = friend()

        for user in recentlyJoinedData['users']:
            holder_count = user['holderCount']
            username = user['twitterUsername']
            user_address = user['address']

            # Check if the address has already been processed
            if user_address in processed_addresses:
                continue

            try:
                user_info = api.get_user(screen_name=username)
                follower_count = user_info.followers_count

                if follower_count > 5001 and holder_count < 7:
                    message = (
                        f"Holder Count: {holder_count}\n"
                        f"Share Supply: {user['shareSupply']}\n"
                        f"Address: {user_address}\n"
                        f"https://twitter.com/{username}\n"
                        f"Twitter Followers Count: {follower_count}\n"
                        f"Link for friendtech- https://www.friend.tech/rooms/{user_address}\n"
                    )

                    # Get the first transaction
                    first_transaction = get_first_transaction(user_address)
                    if first_transaction:
                        timestamp_utc3 = format_timestamp_to_utc3(first_transaction['timeStamp'])
                        message += f"First  tx time - : {timestamp_utc3}\n"

                    # Send the message to your Telegram channel
                    await send_telegram_message(chat_id, message)

                    # Add the address to the set of processed addresses
                    processed_addresses.add(user_address)

            except tweepy.TweepError as e:
                if e.api_code == 88:
                    # Rate limit exceeded, wait for 15 minutes
                    print("Rate limit exceeded. Waiting for 15 minutes...")
                    time.sleep(900)  # Wait for 15 minutes (900 seconds)
                else:
                    print(f"Error: {e}")
            except Exception as e:
                print(f"Error: {e}")

        # Wait for 3 seconds before fetching data again
        await asyncio.sleep(31)

if __name__ == "__main__":
    asyncio.run(main())
