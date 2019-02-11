from credentials import *  # Import twitter credentials from the file
from random import *
import string
import tweepy
import re

# Gets the hashtags from the tweets
# subject: string - subject to gather tweets about
def getHashtags(subject):
    tags = []

    # Search the subject
    tweets = api.search(subject)

    # take each tweet split it by spaces and search for hashtags
    for tweet in tweets:
        words = re.split(' ', tweet.text)
        tags.extend(tag for tag in words if tag.startswith('#'))
    # Return all found tags
    return tags

# Tokenize a given text
# text: string - text from a tweet to be tokenized
def tokenize(text):
    return [word.lower().strip(string.punctuation) for word in text.split()]

# Sorts a dictionary in descending orderbased on the keys
# d: dictionary - dictionary to be sorted


def sortDict(d):
    return sorted(d, key=d.get, reverse=True)

# Creates a tweet using the master dictionary
# MasterDict: Dictionary<string, Dictionary<string, int>>
def createTweet(MasterDict):
    # Start the sentence
    pickedWord = list(MasterDict.keys())[0]

    text = pickedWord
    prev = text

    # Create the tweet
    for i in range(0, randint(10, 30)):
        # Sort the dictionary at MasterDict[prev]
        workingDict = sortDict(MasterDict[prev])

        # If the word leads to a dead end, quit the loop
        if len(workingDict) == 0:
            break

        # Pick a random threshold
        threshold = randint(
            MasterDict[prev][workingDict[-1]], MasterDict[prev][workingDict[0]])

        # Pick a random word from the dictionary
        word = choice(workingDict)

        # set the check as the frequency of the word
        check = MasterDict[prev][word]

        # while the check is less than the threshold
        while check < threshold:

            # Choose random words
            word = choice(workingDict)
            check = MasterDict[prev][word]
        # Add the choosen word to the text
        text += ' ' + word

        # Set prev to the chosen word
        prev = word
    # Return the created text
    return text

# Creates the MasterDict datastructure from a list of tokens
# tokens: Array<string> - array of words to be turned into the MasterDict
def createMasterDict(tokens):
    # Dictionary of dictionaries
    MasterDict = {}

    # prev starts as none
    prev = None

    # Tokenize the tweet
    for item in tokens:

        # If the item has not been seen yet
        if item not in MasterDict:

            # Add it to the first dictionary and set up its new dictionary
            MasterDict[item] = {}

        # If this is not the first loop
        if prev is not None:

            # If the current item has not been seen in the prev words dictionary
            if item not in MasterDict[prev]:

                # Add it to the dictionary
                MasterDict[prev][item] = 0

            # Add 1 to the count to the dictionary of prev
            MasterDict[prev][item] = (MasterDict[prev][item] + 1)

        # set prev to the current item
        prev = item

    # return the new MasterDict
    return MasterDict

# Get rid of some of the unwanted things that are in normal tweets
# tweet: string - the body of the tweets text
def clean(tweet):
    tweet = re.sub("http\S+", "", tweet)       # links
    tweet = re.sub("#\S+", "", tweet)          # hashtags
    tweet = re.sub("\.?@", "", tweet)          # at mentions
    tweet = re.sub("RT.+", "", tweet)          # Retweets
    tweet = re.sub("rt.+", "", tweet)          # retweets in lower case
    tweet = re.sub("Video\:", "", tweet)       # Videos
    tweet = re.sub("\n", "", tweet)            # new lines
    tweet = re.sub("^\.\s.", "", tweet)        # leading whitespace
    tweet = re.sub("\s+", " ", tweet)          # extra whitespace
    tweet = re.sub("&amp;", "and", tweet)      # encoded ampersands
    return tweet

# Returns an array with all the tokens from all the tweets
# info: string - subject to gather tweets about
def gatherTweetData(info):
    # Set up the arrays
    data = []
    tokens = []

    # Search twitter for the info
    tweets = api.search(info)
    # Clean each tweet
    for tweet in tweets:
        data.append(clean(tweet.text))

    # Tokenize each tweet
    for d in data:
        gathered = tokenize(d)

        # Add each token in the tokenlist to the tokens
        for t in gathered:
            tokens.append(t)
    # return a MasterDict from the tokens
    return createMasterDict(tokens)

# Returns the trending hashtag from the top trending topics for the US
def trending():
    # countryCode for the US
    countryCode = 23424977

    # Get trending topics for the US
    trending = api.trends_place(countryCode)

    # Grab the top trending one
    data = trending[0]

    # Collect the trends
    trends = data['trends']

    # Get the hastags for the trends
    hashtags = [trend['name'] for trend in trends]

    # Pick one of the Hastags and return it
    hashtag = hashtags[randint(0, len(hashtags) - 1)]
    return hashtag

# Returns the number of milliseconds to wait between to integers representing hours
# first: int - lowest number of hours to wait
# second: int - longest number of hours to wait
def waittime(first, second):
    if (first > second):
        high = first * 3600
        low = second * 3600
    else:
        high = second * 3600
        low = first * 3600
    return randint(low, high)

# Tweets a given message, if printMsg is true will print the result instead of tweet
# message: string - message to tweet out
# printMsg: boolean - determines if the tweet is printed in the console or posted on Twitter
def tweet(message, printMsg=False):
    try:
        # printMsg = true means DEBUGGING
        if(printMsg):
            # Print the message to the console
            print(message)
        else:
            # Otherwise tweet the message
            api.update_status(message)

    # Write any errors to the errors.txt file
    except tweepy.TweepError as e:
        writeToFile('errors.txt', e.reason)

# Writes likes to a given file
# filename: string - name of the file to be written to
# toWrite: stirng  - message to write
def writeToFile(filename, toWrite):

    # Open the file
    f = open(filename, 'a')

    # Write to the file and close it
    f.write(toWrite + '\r\n')
    f.close()


# Run the tweet bot
def main():

    # Attempt to create and send a tweet
    try:
        # Pick a subject
        subject = trending()

        # Grab a trending topic for North America and create a tweet from it
        twt = createTweet(gatherTweetData(subject))

        # Add a hashtag to the tweet
        hashtags = getHashtags(subject)

        # If a hashtags were found pick one and add it to the tweet
        if hashtags is not None:
            twt += ' ' + hashtags[randint(0, len(hashtags) - 1)]
            
        # Tweet out the newly formed twitter message
        tweet(twt)
    except Exception as ex:
        # Write the start message to the file
        writeToFile('errors.txt', "Error: " + str(ex))



# Access and authorize the twitter credentials from the file
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Run tweepy api
# wait_on_rate_limit=True : means wait to do anything until the rate limit is gone
api = tweepy.API(auth, wait_on_rate_limit=True)
main()
