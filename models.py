from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, post_load
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()

class Data(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    price = db.Column(db.Integer)
    description = db.Column(db.String(5000))
    category = db.Column(db.String(100))
    image = db.Column(db.String(100))
    rating_id = db.Column(db.Integer, db.ForeignKey("rating.rating_id"))

    rating = db.relationship("Rating", back_populates="data")

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float)
    count = db.Column(db.Integer)

    data = db.relationship("Data", back_populates="rating")

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    file_name = db.Column(db.String(100))
    file_description = db.Column(db.String(100))
    file_path = db.Column(db.String(100))

class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    changes = db.Column(db.String(100))
    time_stamp = db.Column(db.String(100))
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))


class RatingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rating
    @post_load
    def load_obj(self, data, **kwargs):
        return Rating(**data)    


class DataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Data

    rating = fields.Nested(RatingSchema) 

    @post_load
    def load_obj(self, data: dict, **kwargs):
        dataObj = Data(**data)

        return dataObj

class FileSchema(ma.SQLAlchemyAutoSchema):
    class meta:
        model = File 
    def load_obj(self, data, **kwargs):
        return File(**data)   