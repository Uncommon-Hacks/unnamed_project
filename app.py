from flask import Flask, render_template  # Import render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')  # Render the login.html template


def redirect():
    return render_template('redirect.html')


if __name__ == '__main__':
    app.run(debug=True)