import os
import time
import re

import schedule as schedule
import tweepy
import json
import schedule
import time
from slackclient import SlackClient
import config

slack_client = SlackClient('xoxb-412431558647-410967757153-pnR6j58kO49dncsCNqZgoDFh')

starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "toptrends"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel="#portiapps",
        text= post_trends()
    )
def post_trends():
    authenticate = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    authenticate.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(authenticate)

    # Where On Earth ID for Pasig is1187115.
    PASIG_WOE_ID = 1

    trend = api.trends_place(PASIG_WOE_ID)

    trend = json.loads(json.dumps(trend, indent=1))

    trend_temp = []
    for trend_loop in trend[0]["trends"]:
        trend_temp.append((trend_loop["name"]))

    trending_all = ', \n'.join(trend_temp[:10])

    return trending_all

def post_message():
    slack_client.api_call(
        "chat.postMessage",
        channel="#portiapps",
        text= post_trends()
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        schedule.every(10).minutes.do(post_message)

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
            schedule.run_pending()
    else:
        print("Connection failed. Exception traceback printed above.")


