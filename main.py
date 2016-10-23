# -*- coding: utf-8 -*-

import sys
import json
import chardet
import requests
import win32gui
from time import sleep

client = requests.session()
AUTH = 'https://modal.moe/api/api-token-auth/'
example = "[%album artist% - ]['['%album%[ CD%discnumber%][ #%tracknumber%]']' ]%title%[ '//' %track artist%]"

# Welcome to the thunderdome.
# def parse_syntax():4
#     keys = [
#         '%album artist%', '%album%', '%iscnumber%',
#         '%tracknumber%', '%title%', '%track artist%'
#     ]
#     for key in keys:
#         index = example.find(key)
#         # key found
#         if index != -1:
#
#


class WhatIListenTo:

    def __init__(self):
        self.user = input('Username: ')
        self.password = input('Password: ')
        self.authed = False
        self.last_played = '' # Clarity

        client.get('https://modal.moe')
        self.cookies = dict(client.cookies)
        self.headers = {
            "X-CSRFToken": '',
            'Authorization': ''
        }

    def login(self):
        self.headers['Referer'] = AUTH
        r = requests.post(AUTH, data={
            'username': self.user,
            'password': self.password
        }, cookies=self.cookies)
        token = json.loads(r.text)['token']
        self.headers['Authorization'] = 'Token {}'.format(token)
        self.authed = True
        print('Logged in. Thanks {}'.format(self.user))

    def scrobble(self, song, artist, album=None):
        if not self.authed:
            print('Login idiot')
        else:
            if song != self.last_played:
                self.last_played = song
                r = requests.post(
                    'https://modal.moe/api/scrobbles/',
                    headers=self.headers,
                    data={'song': song, 'artist': artist})
                print('Scrobbled {} by {}'.format(song, artist))


class Foobar:

    def __init__(self):
        self.window_title = '' # For clarity
        self.WILT = WhatIListenTo()

    def post(self, title):
        try:
            delim = title.split(' - ')
            if delim[1][0] == '[':
                album = delim[1].split('[')[1]
                album = album.split(']')[0]
            delim[1] = delim[1].split(' [foo')[0]
            artist = delim[0].rstrip().lstrip()
            song = delim[1].split(']')[1].split('[')[0].lstrip().rstrip()
            if self.WILT.authed:
                self.WILT.scrobble(song, artist)
            else:
                self.WILT.login()
                self.WILT.scrobble(song.encode('utf-8'), artist.encode('utf-8'))
        except Exception as e:
            print('Is this shit fucking unicode?')
            print(e)

    def enum_window_titles(self):

        def callback(handle, data):
            title = win32gui.GetWindowText(handle)
            if 'foobar2000 v' in title.lower():
                if self.window_title != title:
                    self.window_title = title
                    self.post(title)


        win32gui.EnumWindows(callback, None)


if __name__ == '__main__':
    # parse_syntax()
    f = Foobar()
    while 1:
        f.enum_window_titles()
        sleep(5)
