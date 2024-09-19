from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Tag, Post, db, TagSchema, PostSchema

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/', methods=['POST'])
@jwt_required()
def create_tag():
    data = request.get_json()
    # user_id = get_jwt_identity()
    if not data or 'name' not in data:
        return jsonify({'message': 'Tag name is required'}), 400
    
    existing_tag = Tag.query.filter_by(name=data['name']).first()
    if existing_tag:
        return jsonify({'message': 'Tag already exists'}), 400

    new_tag = Tag(name=data['name'])
    db.session.add(new_tag)
    db.session.commit()

    #serialize the new tag
    tag_schema = TagSchema()
    result = tag_schema.dump(new_tag)

    return jsonify({'message': 'Tag created successfully', 'tag':result}), 201

#get all tags
@tags_bp.route('/', methods=['GET'])
def get_all_tags():
    tags = Tag.query.all()

    #serialize all tags
    tag_schema = TagSchema(many=True)
    result = tag_schema.dump(tags)

    return jsonify({'tags': result}), 200

#get specific tag
@tags_bp.route('/<int:id>', methods=['GET'])
def get_tag(id):
    tag = Tag.query.get_or_404(id)

    # serialize the tag
    tag_schema = TagSchema()
    result = tag_schema.dump(tag)
    
    return jsonify({'tag': result}), 200

#update tag route 
@tags_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_tag(id):
    tag = Tag.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'Tag name is required'}), 400
    
    existing_tag = Tag.query.filter(Tag.name == data['name'], Tag.id != id).first()
    if existing_tag:
        return jsonify({'message': 'Tag name already exists'}), 400

    tag.name = data['name']
    db.session.commit()

    #serialize the updated tag
    tag_schema = TagSchema()
    result = tag_schema.dump(tag)
    
    return jsonify({'message': 'Tag updated successfully', 'tag': result}), 200

    
#delete tag route
@tags_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()

    return jsonify({'message': 'Tag deleted successfully'}), 200

# ADD TAG TO POST ROUTE
@tags_bp.route('/post/<int:post_id>/add', methods=['POST'])
@jwt_required()
def add_tag_to_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    
    if not data or 'tag_id' not in data:
        return jsonify({'message': 'Tag ID is required'}), 400

    tag = Tag.query.get_or_404(data['tag_id'])

    if tag in post.tags:
        return jsonify({'message': 'Tag is already associated with this post'}), 400

    post.tags.append(tag)
    db.session.commit()

    #serialize the post with its tags
    post_schema = PostSchema()
    result = post_schema.dump(post)
    
    return jsonify({'message': 'Tag added to post successfully', 'post': result}), 200

#REMOVE TAGS FROM POST
@tags_bp.route('/post/<int:post_id>/remove', methods=['POST'])
@jwt_required()
def remove_tag_from_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    
    if not data or 'tag_id' not in data:
        return jsonify({'message': 'Tag ID is required'}), 400

    tag = Tag.query.get_or_404(data['tag_id'])

    if tag not in post.tags:
        return jsonify({'message': 'Tag is not associated with this post'}), 400

    post.tags.remove(tag)
    db.session.commit()

   #serialize the post with its tags
    post_schema = PostSchema()
    result = post_schema.dump(post)
    
    return jsonify({'message': 'Tag removed from post successfully', 'post': result}), 200

#GET TAGS ASSOCIATED WITH A POST
@tags_bp.route('/post/<int:post_id>', methods=['GET'])
def get_post_tags(post_id):
    post = Post.query.get_or_404(post_id)
    
    #serialize the post with its tags
    post_schema = PostSchema()
    result = post_schema.dump(post)
    
    return jsonify({'post': result}), 200

