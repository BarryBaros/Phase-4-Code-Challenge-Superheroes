from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata naming conventions for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Define relationship with HeroPower
    hero_powers = relationship('HeroPower', back_populates='hero', cascade="all, delete-orphan")

    # Define association proxy for powers
    powers = association_proxy('hero_powers', 'power')

    # Define serialization rules
    serialize_rules = ('-hero_powers.hero', '-hero_powers.power.hero',)

    def __repr__(self):
        return f'<Hero {self.id} {self.name}({self.super_name})>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Define relationship with HeroPower
    hero_powers = relationship('HeroPower', back_populates='power', cascade="all, delete-orphan")

    # Define serialization rules
    serialize_rules = ('-hero_powers',)

    # Validate description
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        return description

    def __repr__(self):
        return f'<Power {self.id} {self.name}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    strength = db.Column(db.String, nullable=False)

    # Define relationships
    hero = relationship('Hero', back_populates='hero_powers')
    power = relationship('Power', back_populates='hero_powers')

    # Define serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # Validate strength
    @validates('strength')
    def validate_strength(self, key, strength):
        allowed_strengths = ['Strong', 'Weak', 'Average']
        if strength not in allowed_strengths:
            raise ValueError(f"Strength must be one of {allowed_strengths}.")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
