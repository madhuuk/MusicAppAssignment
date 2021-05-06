import json
import boto3
import requests

s3 = boto3.resource('s3')


def uploadToS3(AllSongs):
    for song in AllSongs['songs']:
        img_url = song['img_url']
        imageName = img_url.split('/')[-1]

        getImageData = requests.get(img_url, stream=True)
        image_raw = getImageData.raw
        ImageFile = image_raw.read()
        s3.Bucket('myassignmentsagar').put_object(Key=imageName, Body=ImageFile)
        print("Adding music:", img_url + " :::: " + imageName)


if __name__ == '__main__':
    with open("a2.json") as json_file:
        AllSongs = json.load(json_file)
    uploadToS3(AllSongs)
