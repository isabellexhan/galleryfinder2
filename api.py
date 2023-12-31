#-----------------------------------------------------------------------
# api.py
# Learned from tutorials below:
# Python REST API Tutorial: https://www.youtube.com/watch?v=GMppyAPbLYk&t=3920s
# Python Full Tutorial - Flask, Authentication, Databases: https://www.youtube.com/watch?v=dam0GPOAvVI&t=63s
#-----------------------------------------------------------------------

# for local use
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
# change for heroku
db_path = os.path.join(os.path.dirname(__file__), 'medi.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)
db.Model = Base

@app.route('/')
def home():
    return render_template('app.html')

@app.route('/result')
def result():
    return render_template('result.html')

# for testing
# @app.route('/artworks', methods=['GET'])
# def get_artworks():
#     artworks = db.session.query(Artwork).options(joinedload(Artwork.artist), joinedload(Artwork.exhibition)).all()
#     return jsonify([artwork.serialize for artwork in artworks])

# # for testing
# @app.route('/artwork/<string:artwork_id>', methods=['GET'])
# def get_artwork(artwork_id):
#     artwork = db.session.query(Artwork).options(joinedload(Artwork.artist), joinedload(Artwork.exhibition)).filter_by(id=artwork_id).first()
#     if artwork:
#         artwork_data = artwork.serialize
#         return jsonify(artwork_data)
#     else:
#         return jsonify({'message': 'Artwork not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_image():

    if 'image' not in request.files:
        return jsonify({'message': 'No image uploaded'}), 404

    image = request.files['image']

    # if image.filename == '':
    #     return jsonify({'message': 'No image uploaded'}), 404

    if image:
        filepath = "temporary.jpg"
        image.save(filepath)
        
        # for dynamic dataset
        # dataset_path = "../Database/dataset/"
        # closest_images = cnn.find_closest_images(filepath, dataset_path)

        # for static dataset
        closest_images = find_closest_images(filepath)
        if closest_images:
            cleaned_images = []
            # clean up artwork name
            for image in closest_images:
                cleaned_images.append(os.path.basename(image))
            print(cleaned_images)

            # find exhibition associated with artwork
            exhibition_info = []
            for image_name in cleaned_images:
                artwork = db.session.query(Artwork).filter_by(image_name=image_name).first()
                if artwork: 
                    exhibition_info.append(artwork.serialize)

            return jsonify("Recommended Exhibitions: ", exhibition_info)
        else:
            return jsonify({'message': 'No closest images found'}), 404
    
    else:
        return jsonify({'message': 'No image found'}), 404

if __name__ == "__main__":
    # for local use
    # with app.app_context():
    #     db.create_all()
    # app.run(debug=True)

    # for heroku
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)