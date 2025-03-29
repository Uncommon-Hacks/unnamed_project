from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f'https://{AUTH0_DOMAIN}',
    access_token_url=f'https://{AUTH0_DOMAIN}/oauth/token',
    authorize_url=f'https://{AUTH0_DOMAIN}/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.route('/')
def home():
    user = session.get('user')
    return render_template('home.html', user=user)
@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@app.route('/signup')
def signup():
    return auth0.authorize_redirect(
        redirect_uri=url_for('callback', _external=True),
        screen_hint='signup'  # tells Auth0 to open Sign Up tab
    )

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = auth0.get('userinfo').json()
    session['user'] = {
        'name': userinfo['name'],
        'email': userinfo['email'],
        'picture': userinfo['picture']
    }
    return redirect(url_for('redirect_page'))

@app.route('/redirect')
def redirect_page():
    return render_template('redirect.html', user=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout?returnTo={url_for("home", _external=True)}&client_id={AUTH0_CLIENT_ID}'
    )

if __name__ == '__main__':
    app.run(debug=True)
