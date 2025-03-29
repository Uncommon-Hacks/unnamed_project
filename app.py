from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import random
import shutil
from functools import wraps
import secrets
import glob

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MIN_IMAGES_REQUIRED = 5
AUTH_ROUNDS = 5
IMAGES_PER_ROUND = 9

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_all_users():
    # Get all user folders
    user_dirs = [d for d in os.listdir(app.config['UPLOAD_FOLDER']) 
                if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], d))]
    return user_dirs

def get_user_images(username):
    # Get all images for a specific user
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_dir):
        return []
    
    images = glob.glob(os.path.join(user_dir, '*.*'))
    return [os.path.basename(img) for img in images]

def prepare_auth_rounds(username):
    # Creates 5 rounds of authentication challenges
    auth_rounds = []
    
    all_users = get_all_users()
    if username in all_users:
        all_users.remove(username)
    
    user_images = get_user_images(username)
    
    if not user_images:
        return None
    
    # Create 5 rounds
    for _ in range(AUTH_ROUNDS):
        # Get one random image from the user
        user_image = random.choice(user_images)
        
        # Get 8 random images from other users
        other_images = []
        for _ in range(IMAGES_PER_ROUND - 1):
            if not all_users:
                break
                
            random_user = random.choice(all_users)
            random_user_images = get_user_images(random_user)
            
            if random_user_images:
                other_images.append({
                    'username': random_user,
                    'image': random.choice(random_user_images)
                })
        
        # If we couldn't get enough other images, skip this round
        if len(other_images) < IMAGES_PER_ROUND - 1:
            continue
            
        # Combine user image with others and shuffle
        images = other_images[:IMAGES_PER_ROUND-1]
        correct_index = random.randint(0, IMAGES_PER_ROUND-1)
        images.insert(correct_index, {
            'username': username,
            'image': user_image
        })
        
        auth_rounds.append({
            'images': images,
            'correct_index': correct_index
        })
    
    return auth_rounds

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
    
    return render_template('authenticate.html', 
                           images=images, 
                           round_number=current_round + 1, 
                           total_rounds=AUTH_ROUNDS)

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['user_id']
    return render_template('dashboard.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)