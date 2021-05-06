from flask import Flask, render_template, request, redirect, url_for, session
from boto3.dynamodb.conditions import Key, Attr
import boto3

app = Flask(__name__)
app.secret_key = 'af2ea574685f5a205b976c9e4a'

dynamodb = boto3.resource('dynamodb')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['post'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        table = dynamodb.Table('login')
        response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        print(response['Items'])
        if response['Items']:
            msg1 = "Email already exists"
            return render_template('index.html', msg=msg1)
        else:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            table = dynamodb.Table('login')

            table.put_item(
                Item={
                    'name': name,
                    'email': email,
                    'password': password
                }
            )

            # else:
            msg = "Registration Complete. Please Login to your account !"
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        table = dynamodb.Table('login')
        response = table.query(KeyConditionExpression=Key('email').eq(email))
        table = dynamodb.Table('subscription')
        subRes = table.scan(FilterExpression=Attr('email').eq(email))
        items = response['Items']
        name = items[0]['name']
        if password == items[0]['password']:
            session['name'] = name
            session['email'] = email
            return redirect(url_for('home'))
        else:
            msg = "Email/Password are invalid"
            return render_template('login.html', msg=msg)


@app.route('/home')
def home():
    print('EMAIL :: ' + session['email'])
    email = session['email']
    table = dynamodb.Table('subscription')
    subRes = table.scan(FilterExpression=Attr('email').eq(email))
    table = dynamodb.Table('music')
    res = table.scan()
    context = {
        'name': session['name'],
        'email': session['email'],
        'items': res['Items'],
        'subscription': subRes['Items'],
        's3bucket': 'https://myassignmentsagar.s3.amazonaws.com/'
    }
    return render_template('musichome.html', **context)


@app.route('/logout')
def logout():
    del session['name']
    del session['email']
    return render_template("login.html")


@app.route('/SubscribedMusic', methods=['post'])
def SubscribedMusic():
    if request.method == 'POST':
        artist = request.form['artist']
        title = request.form['title']
        year = request.form['year']
        email = request.form['email']
        img = request.form['img_url']

        table = dynamodb.Table('subscription')

        table.put_item(
            Item={
                'artist': artist,
                'title': title,
                'year': year,
                'email': email,
                'img_url': img
            }
        )
        msg = f"You have Subscribed to {title}  {artist} "
        return redirect(url_for('home'))


@app.route("/removeSub", methods=['POST'])
def removeSub():
    if request.method == 'POST':
        song_artist = request.form['artist']
        song_title = request.form['title']
        song_year = request.form['year']
        email = session['email']
        songImg = request.form['img_url']

        print(song_title, email, song_artist)

        music_table = dynamodb.Table('subscription')
        remove_Subscription = music_table.delete_item(
            Key={
                'title': song_title,
                'email': session['email'],
            }
        )
        return redirect(url_for('home'))


@app.route("/search", methods=['post'])
def search():
    if request.method == 'POST':
        song_artist = request.form['artist']
        song_title = request.form['title']
        song_year = request.form['year']
        email = session['email']

        music_table = dynamodb.Table('music')

        if song_title and song_year and song_artist:
            query_Results = fetch_MusicInfo(music_table, song_title, song_year, song_artist)
        elif song_title and song_year:
            query_Results = fetch_TitleAndYear(music_table, song_title, song_year)
        elif song_title and song_artist:
            query_Results = fetch_TitleAndArtist(music_table, song_title, song_artist)
        elif song_year and song_artist:
            query_Results = fetch_YearAndArtist(music_table, song_year, song_artist)
        elif song_title:
            query_Results = fetch_InfoByTitle(music_table, song_title)
        elif song_year:
            query_Results = fetch_InfoByYear(music_table, song_year)
        elif song_artist:
            query_Results = fetch_InfoByArtist(music_table, song_artist)
        else:
            query_Results = fetch_all(music_table)

        table = dynamodb.Table('subscription')
        subRes = table.scan(FilterExpression=Attr('email').eq(email))

        print(query_Results)
        if not query_Results:
            noRecords = "No Records Found"
            context = {
                'name': session['name'],
                'items': query_Results,
                'noRecords': noRecords,
                'subscription': subRes['Items'],
                's3bucket': 'https://myassignmentsagar.s3.amazonaws.com/'

            }
        else:
            print("USER NAME : " + session['name'])
            context = {
                'name': session['name'],
                'items': query_Results,
                'subscription': subRes['Items'],
                's3bucket': 'https://myassignmentsagar.s3.amazonaws.com/'
            }
        return render_template("musichome.html", **context)


def fetch_MusicInfo(table, title, year, artist):
    response = table.scan(
        FilterExpression=Attr('title').eq(title) & Attr('year').eq(year) & Attr('artist').eq(artist)
    )
    return response['Items']


def fetch_all(table):
    response = table.scan()
    return response['Items']


def fetch_TitleAndYear(table, title, year):
    response = table.scan(
        FilterExpression=Attr('title').eq(title) & Attr('year').eq(year)
    )
    return response['Items']


def fetch_TitleAndArtist(table, title, artist):
    response = table.scan(
        FilterExpression=Attr('title').eq(title) & Attr('artist').eq(artist)
    )
    return response['Items']


def fetch_YearAndArtist(table, year, artist):
    response = table.scan(
        FilterExpression=Attr('year').eq(year) & Attr('artist').eq(artist)
    )
    return response['Items']


def fetch_InfoByTitle(table, title):
    response = table.scan(
        FilterExpression=Attr('title').eq(title)
    )
    return response['Items']


def fetch_InfoByYear(table, year):
    response = table.scan(
        FilterExpression=Attr('year').eq(year)
    )
    return response['Items']


def fetch_InfoByArtist(table, artist):
    response = table.scan(
        FilterExpression=Attr('artist').eq(artist)
    )
    return response['Items']


if __name__ == "__main__":
    app.run(host='0.0.0.0')
