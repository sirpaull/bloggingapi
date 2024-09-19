from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post, PostSchema

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    try:
        print ("Reached create_post route")
        user_id = get_jwt_identity()
        #check if request has a body
        if not request.json:
            return jsonify({'message': 'Empty request body'}), 400

        #check if request data is JSON
        if not request.is_json:
            return jsonify({'message': 'Request must be JSON'}), 400
        data = request.get_json()

        #debugging : Print the raw data and headers
        print (f"Raw data: {data}")
        print (f"Headers: {request.headers}")

        #try to parse JSON data
        try:
            data = request.get_json()
        except Exception as e:
            print(f'failed to parse JSON: {str(e)}')
            return jsonify({'message': 'invalid JSON format '}), 400
        
        #Debugging : Print the parsed data
        print (f"Parsed data: {data}")

        # Check if data is none or empty
        if not data:
            return jsonify({'message': 'Empty Json Object'}), 400

        #error checking for required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'Missing or empty required field: {field}'}), 400
           
         # Validate the length of the title and content
        if len(data['title']) > 100:
            return jsonify({'message': 'Title cannot exceed 100 characters'}), 400
        
        if len(data['content']) > 1000:
            return jsonify({'message': 'Content cannot exceed 1000 characters'}), 400

        new_post = Post(title=data['title'], content=data['content'], user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        #serialize the new post
        post_schema = PostSchema()
        result = post_schema.dump(new_post)
        return jsonify({'message': 'Post created!', 'post': result}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while creating a post: {str(e)}")
        return jsonify({'message': 'An error occurred while creating the post'}), 500

@posts_bp.route('/', methods=['GET'])
def get_all_posts():
    try:
        posts = Post.query.all()
        post_schema = PostSchema(many=True)
        result = post_schema.dump(posts)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while getting posts: {str(e)}")
        return jsonify({'message': 'An error occurred while getting the posts'}), 500



@posts_bp.route('/<int:id>', methods=['GET'])
def get_post(id):
    # Implement user authentication here
    post = Post.query.get_or_404(id)
    post_schema = PostSchema()
    result = post_schema.dump(post)
    return jsonify(result), 200



@posts_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(id)

    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    post.title = data['title']
    post.content = data['content']
    db.session.commit()
    
    #serialize the updated post
    post_schema = PostSchema()
    result = post_schema.dump(post)
    return jsonify({'message':'Post Updated!', 'post': result}), 200

@posts_bp.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(id)

    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted!'}), 200
