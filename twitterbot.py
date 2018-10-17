import tweepy
import string
import re
import operator
from time import sleep
from nltk.tokenize import RegexpTokenizer
from credentials import *  # Import twitter credentials from the file
from random import *
import datetime

# Writes likes to a given file
def writefile(filename, toWrite):
    f = open(filename, 'a')
    f.write(toWrite)
    f.close()

# Gets the hashtags from the tweets
def gethashtags(subject):
    tags = []
    tweets = api.search(subject)
    for tweet in tweets:
        words = re.split(' ', tweet.text)
        tags.extend(tag for tag in words if tag.startswith('#'))
    return tags

# Takes the sentence and returns an array of the words in the sentence
def tokenize(sentence):
    tokens = re.split('[^A-Za-z]+', sentence.lower())  # grab the words
    tokens = list(filter(None, tokens))  # remove nulls
    return tokens

# Takes 'info' and seraches twitter for tweets with that keyword and then
def ngram(words, n=2):
    gram = dict()
    assert n > 1 and n < 100
    # make a dictionary of words and their counts
    for i in range(len(words)-(n-1)):
        key = tuple(words[i:i+n])
        if key in gram:
            gram[key] += 1
        else:
            gram[key] = 1
    # now sort the list my frequency
    gram = sorted(gram.items(), key=operator.itemgetter(1))
    return gram

# Uses wordcount as a weight to pseuo-randomly choose the next word
def chooseword(choices):
    total = sum(wc for word, wc in choices)
    r = uniform(0, total)
    count = 0
    for word, wc in choices:
        if count + wc > r:
            return word[1]
        count += wc

# Uses a markov chain to create a sentence of given word size
def markov(words, chainlength=2, size=7):
    curr = choice(words)
    sentence = []
    gram2 = ngram(words, chainlength)
    for i in range(size):  # number of  words for the sentence
        sentence.append(curr)
        choices = [element for element in gram2 if element[0][0] == curr]
        curr = chooseword(choices)
        if curr is None:
            break
    if len(sentence) < 3:
        markov(words, chainlength, size)  # if our chain is bad try again
    return ' '.join(sentence)

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
def gatherinfo(info):
    data = []
    tokens = []
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
def tweet(message):
    try:
        # print(message)
        api.update_status(message)
    except tweepy.TweepError as e:
        print(e.reason)

# Run the tweet bot
def main():
    work = True
    print('Its time to Tweet baby! :P')
    starttime = 'started at: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writefile('errors.txt', starttime)
    while(work):
        # Wait 3 to 6 hrs between tweets
        x = waittime(3, 6)
        context = True
        subject = trending()
        twt = markov(gatherinfo(subject), 25, randint(10, 13))
        if twt is None or len(twt) is 1:
            context = False
        if context:  # If the tweet is 'None' ignore it
            hashtags = gethashtags(subject)  # Otherwise we add a hashtag to it

            if hashtags is not None:
                twt += '. ' + hashtags[randint(0, len(hashtags)-1)]
            if len(twt) < 140:  # Tweet is too long
                tweet(twt)
        context = True  # Reset the context
        work = False


# Access and authorize the twitter credentials from the file
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Run tweepy api and wait to do anything until the rate limit is gone
api = tweepy.API(auth, wait_on_rate_limit=True)
main()
