# import sys
# sys.path.insert(0, '/Users/isabellehan/Desktop/Clean')

import os

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import joinedload
from database import Base, Gallery, Exhibition, Artist, Artwork
from cnn import find_closest_images

Base = Base
Gallery = Gallery
Exhibition = Exhibition
Artist = Artist
Artwork = Artwork


app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'mini.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)
db.Model = Base

@app.route('/')
def home():
    return render_template('app.html')

@app.route('/artworks', methods=['GET'])
def get_artworks():
    artworks = db.session.query(Artwork).options(joinedload(Artwork.artist), joinedload(Artwork.exhibition)).all()
    return jsonify([artwork.serialize for artwork in artworks])

@app.route('/artwork/<string:artwork_id>', methods=['GET'])
def get_artwork(artwork_id):
    artwork = db.session.query(Artwork).options(joinedload(Artwork.artist), joinedload(Artwork.exhibition)).filter_by(id=artwork_id).first()
    if artwork:
        artwork_data = artwork.serialize
        return jsonify(artwork_data)
    else:
        return jsonify({'message': 'Artwork not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_image():

    if 'image' not in request.files:
        return jsonify({'message': 'No image uploaded'}), 400

    image = request.files['image']

    if image.filename == '':
        return jsonify({'message': 'No image selected'}), 400

    if image:
        filepath = "temporary.jpg"
        image.save(filepath)
        # dataset_path = "../Database/dataset/"
        # closest_images = cnn.find_closest_images(filepath, dataset_path)

        closest_images = find_closest_images(filepath)
        if closest_images:
            cleaned_images = []
            for image in closest_images:
                cleaned_images.append(os.path.basename(image))
            print(cleaned_images)

            exhibition_info = []
            for image_name in cleaned_images:
                artwork = db.session.query(Artwork).filter_by(image_name=image_name).first()
                if artwork: 
                    exhibition_info.append(artwork.serialize)

            return jsonify("Recommended Exhibitions:", exhibition_info)
        else:
            return jsonify({'message': 'No closest images found'}), 404
    
    else:
        return jsonify({'message': 'No image found'}), 400

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    # app.run(debug=True)

    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

    # app.run(host='0.0.0.0', port=000)
