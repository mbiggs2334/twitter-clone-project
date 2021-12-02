"""Message model tests"""

import os
from unittest import TestCase
from flask import g
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///twitter_db_test"

from app import app

db.drop_all()

class MessageModelTestCase(TestCase):
    """Contains tests for the message model"""

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
        
        message1 = Message(
            text="Message1",
            timestamp = '12/02/2021',
            user_id=1
        )
        
        message2 = Message(
            text="Message2",
            timestamp = '12/02/2021',
            user_id=1
        )
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        db.session.add(message1)
        db.session.add(message2)
        db.session.commit()



    @classmethod
    def tearDownClass(self):
        """Cleans up test **DB** after tests are complete"""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()
        db.drop_all()
        
    def test_message_add(self):
        """Tests messages being created and added to **DB** """
        message = Message.query.get(1)
        
        self.assertIsInstance(message, Message)
        
    def test_message_likes(self):
        """Tests likes are added and read from **DB** """
        like1 = Likes(user_id=2, message_id=1)
        like2 = Likes(user_id=1, message_id=2)
        db.session.add(like1)
        db.session.add(like2)
        db.session.commit()
        
        u1 = User.query.get_or_404(1)
        m2 = Message.query.get_or_404(2)
        
        self.assertIn(m2, u1.likes)