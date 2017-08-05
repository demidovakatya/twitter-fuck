import json
import os
import tweepy
import time

from tweepy import OAuthHandler

datadir = 'data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

credsdir = 'credentials'

cred_names = ["consumer_key", "consumer_secret", "access_token", "access_secret"]
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
        for k, v in filters.items(): f[k] = v

        if type(f['languages']) == type('str'):
            f['languages'] = [f['languages']]

    return f


class TweepyListener(tweepy.streaming.StreamListener):
    def on_data(self, raw_data):
        """
        Called when raw data is received from connection.
        """
        data = json.loads(raw_data)

        try:
            text = data['text']
        except:
            text = "fail"
            return text

        timestamp = int(time.time())
        print(str(timestamp))

        with open(os.path.join(datadir, '%s.txt' % timestamp), 'wa') as out:
            out.write(text + '\n')

        return True

    def on_error(self, status_code):
        print("oops: %s" % status_code)
        if status_code == 420:
            time.sleep(420)


def main(creds=default_creds, debug=False):
    listener = TweepyListener()

    auth = OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
    auth.set_access_token(creds['access_token'], creds['access_secret'])
    stream = tweepy.Stream(auth=auth, listener=listener)

    if debug:
        print("credentials")
        print(creds)
        print('-------')
        print("filters")
        print(f)
        print('-------')
        try:
            print(auth.get_username())
        except:
            print('fail with auth')

    return stream


if __name__ == '__main__':
    path_to_creds = 'credentials/credentials.json'
    creds = get_credentials(path_to_creds)

    filters = {'languages': 'ru', 'track': ' ,', 'locations': [60, 31, 59.5, 30]}
    f = make_filters_dict(filters)

    stream = main(creds, debug=True)

    while True:
        try:
            stream.filter(follow=f['follow'], track=f['track'],
                          languages=f['languages'],
                          encoding=f['encoding'], filter_level=f['filter_level'])
        except:
            print("oops")
