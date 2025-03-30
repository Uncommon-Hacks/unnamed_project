from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import shutil
from functools import wraps
import secrets
from pprint import pprint

from lib import aiLib
from lib.helpers import *
import re

def strip_markdown(text):
    # Very basic: removes *, _, ` used in Markdown
    return re.sub(r'[*_`]+', '', text)
    
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        
        # Check if username already exists
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
        if os.path.exists(user_dir):
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))
        
        # Create user directory
        os.makedirs(user_dir, exist_ok=True)
        
        # Save uploaded images
        files = request.files.getlist('images')
        valid_images = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_dir, filename))
                valid_images += 1
        
        if valid_images < MIN_IMAGES_REQUIRED:
            # Not enough valid images, remove user directory
            shutil.rmtree(user_dir)
            flash(f'Please upload at least {MIN_IMAGES_REQUIRED} valid images (jpg, png, jpeg, gif).')
            return redirect(url_for('register'))
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        
        # Check if username exists
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
        if not os.path.exists(user_dir):
            flash('Username not found.')
            return redirect(url_for('login'))
        
        # Prepare authentication rounds
        auth_rounds = prepare_auth_rounds(username)
        
        if not auth_rounds or len(auth_rounds) < AUTH_ROUNDS:
            flash('Could not prepare authentication challenges. Please try again.')
            return redirect(url_for('login'))
        
        # Store auth rounds and user info in session
        session['auth_rounds'] = auth_rounds
        session['current_round'] = 0
        session['auth_username'] = username
        
        return redirect(url_for('authenticate'))
    
    return render_template('login.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    # Check if authentication in progress
    if 'auth_rounds' not in session or 'current_round' not in session:
        flash('Authentication session expired.')
        return redirect(url_for('login'))
    
    current_round = session['current_round']
    auth_rounds = session['auth_rounds']
    
    # Check if all rounds completed
    if current_round >= len(auth_rounds):
        # Authentication successful
        session['user_id'] = session['auth_username']
        
        # Clear authentication data
        session.pop('auth_rounds', None)
        session.pop('current_round', None)
        session.pop('auth_username', None)
        
        flash('Authentication successful!')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        selected_index = int(request.form['selected_image'])
        correct_index = auth_rounds[current_round]['correct_index']
        
        if selected_index == correct_index:
            # Correct selection
            session['current_round'] = current_round + 1
            
            if current_round + 1 >= AUTH_ROUNDS:
                # All rounds completed successfully
                session['user_id'] = session['auth_username']
                
                # Clear authentication data
                session.pop('auth_rounds', None)
                session.pop('current_round', None)
                session.pop('auth_username', None)
                
                flash('Authentication successful!')
                return redirect(url_for('dashboard'))
            else:
                # Continue to next round
                return redirect(url_for('authenticate'))
        else:
            # Incorrect selection, authentication failed
            session.pop('auth_rounds', None)
            session.pop('current_round', None)
            session.pop('auth_username', None)
            
            flash('Authentication failed. Incorrect image selection.')
            return redirect(url_for('login'))
    
    # Display current round
    round_data = auth_rounds[current_round]
    images = []
    
    for i, img_data in enumerate(round_data['images']):
        username = img_data['username']
        image = img_data['image']
        path = f"/static/img/{username}/{image}"
        images.append({
            'index': i,
            'path': path
        })
    
    pprint(images)

    return render_template('authenticate.html', 
                           images=images, 
                           round_number=current_round + 1, 
                           total_rounds=AUTH_ROUNDS)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username = session['user_id']
    messages = []
    if request.method == 'POST':
        user_input = request.form['user_input']
        messages = session.get('chat_messages', [])
        messages.append({'sender': 'user', 'text': user_input})
        file_path = "path/to/your/file.txt"

        with open("memories/" + session['user_id'] + ".txt", "r") as file:
            all_data = file.read()

        # Now 'all_data' is a string with the entire file’s content.


        aiLib.add_prompt_to_memory(user_input + "Data " + all_data, username)
        gemini_response = aiLib.generate_gemini_response(user_input, username)
        messages.append({'sender': 'gemini', 'text': gemini_response})

        session['chat_messages'] = messages
    else:
        messages = session.get('chat_messages')
        if messages is None:
            messages = []
            session['chat_messages'] = messages  # ensure persistence

    return render_template('dashboard.html', username=username, messages=messages)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)