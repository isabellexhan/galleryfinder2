#-----------------------------------------------------------------------
# database.py
# Adapted from database tutorial of Bob Dondero
#-----------------------------------------------------------------------
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
import base64
#-----------------------------------------------------------------------

Base = declarative_base()

class Gallery (Base):
    __tablename__ = 'galleries'
    id = Column(String, primary_key=True)
    name = Column(String)
    hours = Column(String)
    location = Column(String)
    exhibitions = relationship("Exhibition", back_populates="gallery")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'hours': self.hours,
            'location': self.location,
        }

class Exhibition (Base):
    __tablename__ = 'exhibitions'
    id = Column(String, primary_key=True)
    name = Column(String)
    duration = Column(String)
    gallery_id = Column(String, ForeignKey('galleries.id'))
    gallery = relationship("Gallery", back_populates="exhibitions")
    artworks = relationship("Artwork", back_populates='exhibition')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'gallery_info': {
                'id': self.gallery.id,
                'name': self.gallery.name
            } if self.gallery else None,
            'artworks_info': [{'id': artwork.id, 'name': artwork.name} for artwork in self.artworks]
        }

class Artist (Base):
    __tablename__ = 'artists'
    id = Column(String, primary_key=True)
    name = Column(String)
    artworks = relationship("Artwork", back_populates="artist")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artworks_info': [{'id': artwork.id, 'name': artwork.name} for artwork in self.artworks]
        }

class Artwork (Base):
    __tablename__ = 'artworks'
    id = Column(String, primary_key=True)
    image = Column(LargeBinary)
    image_name = Column(String)
    image_type = Column(String)
    artists_id = Column(Integer, ForeignKey('artists.id'))
    artist = relationship("Artist", back_populates="artworks")
    exhibition_id = Column(Integer, ForeignKey('exhibitions.id'))
    exhibition = relationship("Exhibition", back_populates="artworks")

    @property
    def serialize(self):
        exhibition_info = {
            'id': self.exhibition.id,
            'name': self.exhibition.name,
            'duration': self.exhibition.duration,
            'gallery': {
                'id': self.exhibition.gallery.id,
                'name': self.exhibition.gallery.name,
                'hours': self.exhibition.gallery.hours,
                'location': self.exhibition.gallery.location
            } if self.exhibition and self.exhibition.gallery else None
        } if self.exhibition else None

        artist_info = {
            'id': self.artist.id,
            'name': self.artist.name
        } if self.artist else None

        image_data = base64.b64encode(self.image).decode() if self.image else None
        
        return {
            'id': self.id,
            'name': self.image_name,
            'type': self.image_type,
            'exhibition': exhibition_info,
            'artist': artist_info,
            'image': image_data
        }