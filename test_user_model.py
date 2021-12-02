"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask import g
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///twitter_db_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data



class UserModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(self):
        """Create test client, adds sample data."""
        db.create_all() 
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url='null'
        )
        
        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url='null'
        )
        
        
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()



    @classmethod
    def tearDownClass(self):
        """Cleans up test **DB** after tests are complete"""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()
        db.drop_all()
    
    
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
        db.session.delete(u)
        db.session.commit()
        
        
        
    def test_following(self):
        """Tests the following functions"""
        u1 = User.query.get(1)
        u2 = User.query.get(2)
    
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_followed_by(u1))
        
        follow1 = Follows( user_being_followed_id=2, user_following_id=1)
        db.session.add(follow1)
        db.session.commit()
        
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))
        
    def test_signup(self):
        """Tests the signup method for success and failures"""
        with self.assertRaises(TypeError):
            User.signup('bob', 'bob@gmail.com', 'bob123')
            
        
        u3 = User.signup('bob', 'bob@gmail.com', 'bob123','null')
        
        self.assertIsInstance(u3, User)
        
    def test_authentication(self):
        """Tests user authentication"""
        #Tests for invalid username
        user = User.authenticate('testuser', 'HASHED_PASSWORD')

        self.assertFalse(user)
        
        #Tests for invalid password
        user = User.authenticate('testuser', 'NOT_MY_PASSWORD')

        self.assertFalse(user)

        #Tests for valid authentication
        user2 = User.authenticate('testuser1', 'HASHED_PASSWORD')

        self.assertIsInstance(user2, User)
        
        