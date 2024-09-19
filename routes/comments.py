from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, Post, db
from models import db, Comment, CommentSchema
from sqlalchemy import and_

comments_bp = Blueprint('comments', __name__)

#initialize schemas

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

@comments_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'message': 'Comment content required'}), 400
    
    new_comment = Comment(content=data['content'], user_id=user_id, post_id=post.id)
    
    db.session.add(new_comment)
    db.session.commit()

    #serialize new comment
    comment_schema = CommentSchema()
    result = comment_schema.dump(new_comment)
    return jsonify({
        'message': 'Comment added successfully',
        'comment':result}), 201


#get comments

@comments_bp.route('/comments', methods=['GET'])
def get_comments():
    try:
        comments = Comment.query.all()
        comment_schema = CommentSchema(many=True)
        result = comment_schema.dump(comments)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while getting posts: {str(e)}")
        return jsonify({'message': 'An error occurred while getting the posts'}), 500
    

# get specific comment

@comments_bp.route('/comments/<int:post_id>', methods=['GET'])
def get_comment(post_id):
    # post = Post.query.get(post_id)
    comment = Comment.query.get_or_404(post_id)

    #serialize comment
    comment_schema = CommentSchema()
    result = comment_schema.dump(comment)
    return jsonify(result)

#delete specific comment

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200


#delete duplicate comment

    
