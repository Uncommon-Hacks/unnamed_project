import os
import random
import glob

# Configuration
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MIN_IMAGES_REQUIRED = 5
AUTH_ROUNDS = 1 # change this to 5 in prod 
IMAGES_PER_ROUND = 9

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_all_users():
    # Get all user folders
    user_dirs = [d for d in os.listdir(UPLOAD_FOLDER) 
                if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
    return user_dirs

def get_user_images(username):
    # Get all images for a specific user
    user_dir = os.path.join(UPLOAD_FOLDER, username)
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