import json
import os
import tweepy
from time import time, sleep
from re import sub

from tweepy import OAuthHandler

datadir = 'data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

credsdir = 'credentials'

cred_names = ["consumer_key", "consumer_secret",
              "access_token", "access_secret"]
default_creds = {zip(cred_names, cred_names)}


def get_credentials(filename=None):
    if filename:
        creds = json.loads(open(filename).read())
    else:
        try:
            cred_values = [os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'],
                           os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET']]
        except KeyError:
            print('Please enter your credentials.')
            cred_values = []
            cred_values.append(input('consumer key: '))
            cred_values.append(input('consumer secret: '))
            cred_values.append(input('access token: '))
            cred_values.append(input('access secret: '))

        creds = {zip(cred_names, cred_values)}

    new_filename = os.path.join(credsdir, 'credentials.json')

    if os.path.exists(new_filename):
        new_filename = 'credentials_%s.json' % list(os.stat(new_filename))[-1]

    json.dump(creds, open(os.path.join(credsdir, 'credentials.json'), 'w'))

    return creds


def connect_to_twitter(creds=default_creds):
    auth = OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
    auth.set_access_token(creds['access_token'], creds['access_secret'])
    api = tweepy.API(auth)

    try:
        api.get_settings()
    except tweepy.TweepError:
        print("Tweepy could not authenticate you. Please try again.")
        return None

    return api, auth


def make_filters_dict(filters: dict) -> dict:
    f = {
        'follow': None, 'track': None, 'async': False,
        'locations': None, 'stall_warnings': False,
        'languages': None, 'encoding': 'utf8', 'filter_level': None
    }

    if filters:
        for k, v in filters.items():
            f[k] = v

        if type(f['languages']) == type('str'):
            f['languages'] = [f['languages']]

    return f


def check_tweepy_data_json(data: dict) -> bool:
    """
    data (dict): A dictionary (probably, raw Tweepy data laded with json library).
    returns: True or False – if by the given json we can make a conclusion its corresponding tweet is okay.
    """
    return not ('text' not in data.keys() or data['in_reply_to_status_id'] or data['is_quote_status'])
    # if 'text' not in data.keys() or data['in_reply_to_status_id'] or data['is_quote_status']:
    #     return False
    # else:
    #     return True    


class TweepyListener(tweepy.streaming.StreamListener):
    def on_data(self, raw_data):
        """
        Called when raw data is received from connection.
        """
        data = json.loads(raw_data)

        if not check_tweepy_data_json(data):
            # print('useless tweet: %s', data['id'])
            return True
            
        elif 'retweeted_status' in data.keys():
            data = data['retweeted_status']
            # print("this was a RT... ")
            if not check_tweepy_data_json(data):
                # print('useless tweet: %s', data['id'])
                return True
        
        # else: # only text tweets get here alive
        text = sub("\n", " ", data['text'])
        if __name__ == '__main__':
            print(text)

        ts = int(time() / (60 * 5))
        print(str(ts))
        with open(os.path.join(datadir, '%s.txt' % ts), 'a') as out:
            out.write(text + '\n')

        return True

    def on_error(self, status_code = 228):
        print("oops: %s" % status_code)
        sleep(int(status_code))
        # else: sleep(120)
        return True


def main(creds=default_creds, debug=False):
    auth = OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
    auth.set_access_token(creds['access_token'], creds['access_secret'])

    if debug:
        print("credentials:\t\t%s\n" % creds)
        print("filters:\t\t%s\n" % f)
        try:
            print(auth.get_username())
        except:
            print('auth failed')

    stream = tweepy.Stream(auth=auth, listener=TweepyListener())
    return stream


if __name__ == '__main__':
    creds = get_credentials('credentials/credentials.json')

    filters = {'languages': 'ru',
               'track': 'в,a,я,с,и,о,у',
               'locations': [60.6, 50.0, 55.2, 30.2]}
    f = make_filters_dict(filters)

    stream = main(creds, debug=True)

    while True:
        try:
            stream.filter(follow=f['follow'],
                          track=f['track'],
                          languages=f['languages'])
        except:
            print("oops, %s" % "an error")
            break
