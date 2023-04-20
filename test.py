import os
import json
import time
import sys

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)
lib_path = os.path.join(package_path, "lib")

if lib_path not in sys.path:
    sys.path.append(lib_path)

from evernote.api.client import EvernoteClient

def setup():
    """
    oauth flow for new users or updating users
    adapted from https://gist.github.com/inkedmn/5041037
    """
    client = EvernoteClient(
        consumer_key="geselle-joy",
        consumer_secret="11d19a384c2ed641",
        sandbox=False
    )

    request_token = client.get_request_token('http://localhost:10668')
    print(
        "Paste this URL in your browser and login:"
        "-> {url}  \n\n"
        "Be advised, this will save your oauth token in plaintext to ~/.not_token !"
        "if you aren't cool with that, ctrl-c now and never return!".format(
            url=client.get_authorize_url(request_token)
        )
    )
    single_server = single_serve()
    single_server.handle_request()
    auth_url = path  # noqa
    vals = parse_query_string(auth_url)
    auth_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        vals['oauth_verifier']
    )
    with open(os.path.join(os.environ['HOME'], '.not_token'), 'w') as f:
        f.write(auth_token)
        print("Token saved.")

setup()