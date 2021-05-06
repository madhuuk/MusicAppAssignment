import time
from decimal import Decimal
import json
import boto3
import key_config as keys


def load_movies(songs, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    for song in songs['songs']:
        title = song['title']
        artist = song['artist']
        year = int(song['year'])
        print("Adding Song details:", year, title, artist)
        table.put_item(Item=song)


if __name__ == '__main__':
    with open("a2.json") as json_file:
        songs_list = json.load(json_file, parse_float=Decimal)
    print(songs_list)
    load_movies(songs_list)
