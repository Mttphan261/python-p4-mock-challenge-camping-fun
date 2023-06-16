from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    # serialize_rules = ('-signups.activity',)
    serialize_only = ('id', 'name', 'difficulty')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate = db.func.now())

    #****RELATIONSHIP****
    signups = db.relationship('Signup', back_populates='activity')


    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    serialize_rules = ('-signups.camper',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate = db.func.now())

    #****RELATIONSHIP****
    signups = db.relationship('Signup', back_populates='camper')
    activities = association_proxy('signups', 'activity')

    # Add validations to the Camper model:
    # must have a name
    # must have an age between 8 and 18
    @validates('name')
    def validate_name(self, key, name_str):
        if not name_str:
            raise ValueError('Camper must have a name.')
        return name_str
    @validates('age')
    def validates_age(self, key, age):
        if not 8 <= age <= 18:
            raise ValueError('Age must be between 8 and 18')
        return age

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'
    
class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules = ('-activity.signups', '-camper.signups',)

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate = db.func.now())    

    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))

    
    #****RELATIONSHIP****    
    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')

    # Add validations to the Signup model:
    # must have a time between 0 and 23 (referring to the hour of day for the activity)

    @validates('time')
    def validate_time(self, key, time):
        if not 0 <= time <= 23:
            raise ValueError('Time must be between 0 and 23')
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need. 