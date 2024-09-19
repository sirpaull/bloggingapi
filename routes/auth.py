# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token
# from models import User, db

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()

#     print ("Received data:", data)


#     # Validate the input data
#     if not data:
#         return jsonify({'message': 'No input data provided'}), 400
    
#     #validate that 'username', 'email' and 'password' are in the payload

#     if 'username' not in data or 'email' not in data or 'password' not in data:
#         return jsonify({'message': 'Missing username, email or password'}), 400

#     hashed_password = generate_password_hash(data['password'], method = 'pbkdf2:sha256')
    
#     new_user = User(username=data['username'], email=data['email'], password=hashed_password)
#     db.session.add(new_user)

#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error: {str(e)}")
#         return jsonify({'message': 'An error occurred while registering the user'}), 500
    
#     return jsonify({'message': 'User registered successfully!'}), 201

    

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data['username']).first()

#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({'message': 'Invalid credentials'}), 401

#     access_token = create_access_token(identity=user.id)
#     return jsonify({'access_token': access_token}), 200

from flask import Flask
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import User, db, UserSchema

import re

app = Flask(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print ("Received data:", data)
    app.logger.info("Received data: %s", data)

    # Validate the input data
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing {field}'}), 400
        

    # Validate email format if necessary (simple regex check)
 
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        return jsonify({'message': 'Invalid email format'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()

        # Serialize the newly created user
        user_schema = UserSchema()
        result = user_schema.dump(new_user)
        return jsonify({'message': 'User registered successfuly!', 'user': result}), 201
    
    except Exception as e:
        db.session.rollback()
        app.logger.error("Error during user registration: %s", str(e))
        return jsonify({'message': 'An error occurred while registering the user'}), 500
    

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print ("Received data:", data)
    
    #ensure that data contains username and password
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username or password'}), 400
    

    #query the database for the user
    user = User.query.filter_by(username=data['username']).first()

    
    #check if user exists and password is correct
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    #generate an access token for the user
    access_token = create_access_token(identity=user.id)
    #serialize the user
    user_schema = UserSchema()
    result = user_schema.dump(user)
    return jsonify({'message': 'Logged in successfully!', 'user' : result, 'access_token': access_token}), 200
   

@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        user_schema = UserSchema(many=True)
        result = user_schema.dump(users)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while getting posts: {str(e)}")
        return jsonify({'message': 'An error occurred while getting the posts'}), 500
