"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait
from string import ascii_letters
from ucb import main, trace, interact, log_current_line
from math import pow,sqrt



###################################
# Phase 1: The Feelings in Tweets #
###################################

# The tweet abstract data type, implemented as a dictionary.

def make_tweet(text, time, lat, lon):
    """Returns a tweet, represented as a Python dictionary.

    text  -- A string; the text of the tweet, all in lowercase
    time  -- A datetime object; the time that the tweet was posted
    lat   -- A number; the latitude of the tweet's location
    lon   -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_text(t)
    'just ate lunch'
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    >>> tweet_string(t)
    '"just ate lunch" @ (38, 74)'
    """
    return {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}

def tweet_text(tweet):
    """Returns a string, the words in the text of a tweet."""
    return tweet['text']



def tweet_time(tweet):
    """Returns the datetime representing when a tweet was posted."""
    return tweet['time']

def tweet_location(tweet):
    """Returns a position representing a tweet's location."""
    
    def latitude(tweet):
        latit = tweet['latitude']
        return latit

    def longitude(tweet):
        longtit = tweet['longitude']
        return longtit
    
    tweet_location = (latitude(tweet), longitude(tweet))

    return tweet_location
    
# The tweet abstract data type, implemented as a function.

def make_tweet_fn(text, time, lat, lon):
    """An alternate implementation of make_tweet: a tweet is a function.
    
    >>> t = make_tweet_fn("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_text_fn(t)
    'just ate lunch'
    >>> tweet_time_fn(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> latitude(tweet_location_fn(t))
    38
    """
    def fn(key):
        
        tweet = {'text': text, 'time': time, 'lat': lat, 'lon': lon}
        return tweet[key]
      
        
    
    return fn



def tweet_text_fn(tweet):
    """Returns a string, the words in the text of a functional tweet."""
    return tweet('text')

def tweet_time_fn(tweet):
    """Returns the datetime representing when a functional tweet was posted."""
    return tweet('time')

def tweet_location_fn(tweet):
    """Returns a position representing a functional tweet's location."""
    return make_position(tweet('lat'), tweet('lon'))

### === +++ ABSTRACTION BARRIER +++ === ###

def tweet_words(tweet):
    """Returns the words in a tweet."""
    return extract_words(tweet_text(tweet))

def tweet_string(tweet):
    """Returns a string representing a functional tweet."""
    location = tweet_location(tweet)
    point = (latitude(location), longitude(location))
    return '"{0}" @ {1}'.format(tweet_text(tweet), point)

def extract_words(text):
    """Returns the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    >>> extract_words('@(cat$.on^#$my&@keyboard***@#*')
    ['cat', 'on', 'my', 'keyboard']
    """
    text.lower()
    for char in text:
            if char not in ascii_letters:
                text = text.replace(char," ")
    return text.split()


def make_sentiment(value):
    """Returns a sentiment, which represents a value that may not exist.
    
    >>> positive = make_sentiment(0.2)
    >>> neutral = make_sentiment(0)
    >>> unknown = make_sentiment(None)
    >>> has_sentiment(positive)
    True
    >>> has_sentiment(neutral)
    True
    >>> has_sentiment(unknown)
    False
    >>> sentiment_value(positive)
    0.2
    >>> sentiment_value(neutral)
    0
    """
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'     
    return value

    
def has_sentiment(s):
    """Return whether sentiment s has a value."""
    
    if s != None:
        return True
    else:
        return False

def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    return s

def get_word_sentiment(word):
    """Returns a sentiment representing the degree of positive or negative
    feeling in the given word.
    
    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    # Learn more: http://docs.python.org/3/library/stdtypes.html#dict.get
    
    return make_sentiment(word_sentiments.get(word))


def analyze_tweet_sentiment(tweet):
    """ Returns a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("saying, 'i hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("berkeley golden bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    # You may change any of the lines below.
    average = make_sentiment(None)
    final = 0
    count = 0
    
    for word in tweet_words(tweet):
        if get_word_sentiment(word) != None:
            #print(get_word_sentiment(word))
            final = final + get_word_sentiment(word)
            count = count + 1

    if count != 0:
        final = final / count
        return final
    
    else:
        return average
        

        
#################################
# Phase 2: The Geometry of Maps #
#################################

def find_centroid(polygon):
    """Finds the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> round5 = lambda x: round(x, 5) # Rounds floats to 5 digits
    >>> tuple(map(round5, find_centroid(triangle)))
    (3.0, 2.0, 6.0)
    >>> tuple(map(round5, find_centroid([p1, p3, p2, p1])))
    (3.0, 2.0, 6.0)
    >>> tuple(map(float, find_centroid([p1, p2, p1])))  # A zero-area polygon
    (1.0, 2.0, 0.0)
    """
    
    lat_x = []
    lon_y = []

    for x in polygon:
        lat_x.append(x[0])
        lon_y.append(x[1])

    
    area = 0

    for i in range(0, len(lat_x)-1):
        area = area + (lat_x[i] * lon_y[i+1] - lat_x[i+1] * lon_y[i])
    area = area * (1/2)
    if area == 0:
        return (lat_x[0],lon_y[0],0)


    latitude = 0    

    for i in range(0 , len(lat_x)-1):
        latitude = latitude + (lat_x[i] + lat_x[i+1]) * ((lat_x[i] * lon_y[i+1]) - (lat_x[i+1] * lon_y[i]))
    latitude = latitude / (area * 6)


    longitude = 0

    for i in range(0, len(lon_y)-1):
        longitude = longitude + ((lon_y[i] + lon_y[i+1]) * ((lat_x[i] * lon_y[i+1]) - (lat_x[i+1] * lon_y[i])))
    longitude = longitude / (area * 6)


    return (latitude,longitude,abs(area))
    

def find_state_center(polygons):
    """Computes the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_state_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_state_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    
    state_lat = 0
    state_lon = 0
 
    poly_lats = []
    poly_lons = []
    poly_areas = []

    for polygon in polygons:
        poly_lats.append(find_centroid(polygon)[0]) # list of lats
        poly_lons.append(find_centroid(polygon)[1]) # list of lons
        poly_areas.append(find_centroid(polygon)[2]) # list of areas

    #Final LAT
    citatel_lat = 0
    for i in range(0, len(poly_lats)):
        citatel_lat = citatel_lat + (poly_lats[i] * poly_areas[i]) 
    
    menovatel_lat = 0
    for i in range(0, len(poly_lats)):
        menovatel_lat = menovatel_lat + poly_areas[i]
        
    state_lat = citatel_lat / menovatel_lat

    #Final LON
    citatel_lon = 0

    for i in range(0, len(poly_lons)):
        citatel_lon = citatel_lon + (poly_lons[i] * poly_areas[i])

    menovatel_lon = 0

    for i in range(0, len(poly_lons)):
        menovatel_lon = menovatel_lon + poly_areas[i]
    
    
    state_lon = citatel_lon / menovatel_lon


    return state_lat,state_lon
###################################
# Phase 3: The Mood of the Nation #
###################################

def group_tweets_by_state(tweets):
    """Returns a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("welcome to san francisco", None, 38, -122)
    >>> ny = make_tweet("welcome to new york", None, 41, -74)
    >>> two_tweets_by_state = group_tweets_by_state([sf, ny])
    >>> len(two_tweets_by_state)
    2
    >>> california_tweets = two_tweets_by_state['CA']
    >>> len(california_tweets)
    1
    >>> tweet_string(california_tweets[0])
    '"welcome to san francisco" @ (38, -122)'
    """
    
    tweets_by_state = {}
    state_centers = {}

    #dictionary state_centers, keys(state) , values(centers)
    for key in us_states:
        new_key_val = find_state_center(us_states.get(key))
        state_centers[key] = new_key_val

    
    
    
    for tweet in tweets:
        #for every tweet in our input , we make a new tweet_point
        tweet_point = tweet_location(tweet) # (tuple with 2 elements , lat and lon)
        lowest_vector = 13371337
        current_vector = 0
        closest_state = "state"
        #tweet_point[0] is the lat_tweet
        #tweet_point[1] is the lon_tweet
        #state_centers[key][0] is the lat_state
        #state_centers[key][1] is the lon_state
        for key in state_centers
            
            a_pre = tweet_point[0] - state_centers[key][0]
            b_pre = tweet_point[1] - state_centers[key][1]
            a = pow(a_pre,2)
            b = pow(b_pre,2) 
            
            current_vector = sqrt(a + b)
            
            if current_vector < lowest_vector:
                lowest_vector = current_vector
                closest_state = key
            
        
        if closest_state not in tweets_by_state:
            tweets_by_state[closest_state] = [tweet]
        else:
            tweets_by_state[closest_state].append(tweet)
           
    
    return tweets_by_state


def average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
    """
    averaged_state_sentiments = {}
        
    for key in tweets_by_state:
        
        sent_value = 0
        sent_count = 0

        for tweet in tweets_by_state[key]:
            
            x = analyze_tweet_sentiment(tweet)
            if x != None:
                sent_value = sent_value + x
                sent_count = sent_count + 1
        
        if sent_count > 0:
            avg = sent_value / float(sent_count)
            averaged_state_sentiments[key] = avg
    
    return averaged_state_sentiments

##########################
# Command Line Interface #
##########################

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in words:
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_state_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_state_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_query(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def swap_tweet_representation(other=[make_tweet_fn, tweet_text_fn,
                                     tweet_time_fn, tweet_location_fn]):
    """Swap to another representation of tweets. Call again to swap back."""
    global make_tweet, tweet_text, tweet_time, tweet_location
    swap_to = tuple(other)
    other[:] = [make_tweet, tweet_text, tweet_time, tweet_location]
    make_tweet, tweet_text, tweet_time, tweet_location = swap_to


@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_query', '-m', action='store_true')
    parser.add_argument('--use_functional_tweets', '-f', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    if args.use_functional_tweets:
        swap_tweet_representation()
        print("Now using a functional representation of tweets!")
        args.use_functional_tweets = False
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))
