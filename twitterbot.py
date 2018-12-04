import tweepy
import string
import re
import operator
from time import sleep
from nltk.tokenize import RegexpTokenizer
from credentials import *  # Import twitter credentials from the file
from random import *
import datetime

# Gets the hashtags from the tweets
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
def tokenize(text):
    return [word.lower().strip(string.punctuation) for word in text.split()]

def sortDict(d):
    return sorted(d, key=d.get, reverse=True)

def createTweet(MasterDict):
    # Start the sentence
    text = 'the'
    prev = 'the'

    # Create the tweet 
    for i in range(0, random.randint(10,30)):
        # Sort the dictionary at MasterDict[prev]
        workingDict = sortDict(MasterDict[prev])

        # Pick a random threshold
        threshold = random.randint(
            MasterDict[prev][workingDict[-1]], MasterDict[prev][workingDict[0]])
        
        # Pick a random work from the dictionary
        word = random.choice(workingDict)

        # set the check as the frequency of the word
        check = MasterDict[prev][word]

        # while the check is less than the threshold
        while check < threshold:

            # Choose random words
            word = random.choice(workingDict)
            check = MasterDict[prev][word]
        # Add the choosen word to the text
        text += ' ' + word

        # Set prev to the chosen word
        prev = word
    # Return the created text
    return text

def disect(tokens):
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

    #return the new MasterDict
    return MasterDict

# Get rid of some of the unwanted things that are in normal tweets
def clean(tweet):
    tweet = re.sub("https?\:\/\/", "", tweet)  # links
    tweet = re.sub("#\S+", "", tweet)  # hashtags
    tweet = re.sub("\.?@", "", tweet)  # at mentions
    tweet = re.sub("RT.+", "", tweet)  # Retweets
    tweet = re.sub("rt.+", "", tweet)  # retweets in lower case
    tweet = re.sub("Video\:", "", tweet)  # Videos
    tweet = re.sub("\n", "", tweet)  # new lines
    tweet = re.sub("^\.\s.", "", tweet)  # leading whitespace
    tweet = re.sub("\s+", " ", tweet)  # extra whitespace
    tweet = re.sub("&amp;", "and", tweet)  # encoded ampersands
    return tweet

# Returns an array with all the tokens from all the tweets
def gatherTweetData(info):
    # Set up the arrays
    data = []
    tokens = []

    # Search twitter for the info
    tweets = api.search(info)
    for tweet in tweets:
        data.append(clean(tweet.text))
    for d in data:
        gathered = tokenize(d)
        for t in gathered:
            tokens.append(t)
    return tokens

# Returns the trending hashtag from the top trending topics for the US
def trending():
    contrycode = 2487610
    trending = api.trends_place(contrycode)
    data = trending[0]
    trends = data['trends']
    hashtags = [trend['name'] for trend in trends]
    hashtag = hashtags[randint(0, len(hashtags))]
    return hashtag

# Give it 2 times (in hours) you want to wait between and it gives you the number of seconds
def waittime(first, second):
    if (first > second):
        high = first * 3600
        low = second * 3600
    else:
        high = second * 3600
        low = first * 3600
    return randint(low, high)

# Tweets a given message
def tweet(message, print):
    try:
        #print = true means DEBUGGING
        if(print):
            print(message)
        else:
            # Otherwise tweet the message
            api.update_status(message)
    # print any errors
    except tweepy.TweepError as e:
        writeToFile('errors.txt', e.reason)

# Writes likes to a given file
def writeToFile(filename, toWrite):

    # Open the file
    f = open(filename, 'a')

    # Write to the file and close it
    f.write(toWrite)
    f.close()


# Run the tweet bot
def main():

    # Write the start message to the file
    writefile('errors.txt', ('Twitter bot started at: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    while(True):

        # Wait 3 to 6 hrs between tweets
        wait = waittime(3, 6)

        # Pick a subject
        subject = trending()

        # Grab a trending topic for North America and create a tweet from it
        twt = createTweet(gatherTweetData(trending()))

        # If the tweet is 'None' or its length is 1 ignore it
        if twt is not None or len(twt) > 1:

            # Otherwise we add a hashtag to it
            hashtags = getHashtags(subject)

            # If a hashtags were found pick one and add it to the tweet
            if hashtags is not None:
                twt += ' ' + hashtags[randint(0, len(hashtags)-1)]
            # Tweet out the newly formed twitter message
            tweet(twt)
    # While loop runs forever


# Access and authorize the twitter credentials from the file
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Run tweepy api and wait to do anything until the rate limit is gone
api = tweepy.API(auth, wait_on_rate_limit=True)
main()
