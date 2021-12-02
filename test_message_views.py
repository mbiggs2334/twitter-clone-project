"""Tests User Views"""
import os
import flask
from flask import session
from unittest import TestCase
from models import db, User, Message, Follows
from forms import UserAddForm, LoginForm, MessageForm, EditProfileForm

os.environ['DATABASE_URL'] = "postgresql:///twitter_db_test"

from app import CURR_USER_KEY, app

db.drop_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def login_for_test(self):
        """Logs a user into the test enviornment"""
        self.client.post('/login',
                        data = dict(username="testuser1", password="HASHED_PASSWORD", form='')
                        )
    
    @classmethod
    def setUpClass(self):
        """Create test client, adds sample data."""
        db.create_all() 
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
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
        
        u3 = User.signup(
            email="test3@test.com",
            username="testuser3",
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
        
        message3 = Message(
            text="Message3",
            timestamp = '12/01/2021',
            user_id=2
        )
        
        follow1 = Follows(user_being_followed_id=1, user_following_id=2)
        follow2 = Follows(user_being_followed_id=2, user_following_id=1)
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        db.session.add(follow1)
        db.session.add(follow2)
        db.session.add(message1)
        db.session.add(message2)
        db.session.add(message3)
        db.session.commit()



    @classmethod
    def tearDownClass(self):
        """Cleans up test **DB** after tests are complete"""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()
        db.drop_all()
        
        
        
        
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'bubbles'
        self.client = app.test_client()
    
    
    
    def tearDown(self):
        self.client.post('/logout')
        
        
        
    ##############################################################################
    
    
    
    def test_add_message_view(self):
        """Tests the add message view"""

        ### Tests when not logged in ###

        ## TESTS GET ##
        resp = self.client.get('/messages/new', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ## TESTS POST ##
        resp = self.client.post('/messages/new', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        
        ## TESTS GET ##
        self.login_for_test()

        resp = self.client.get('/messages/new', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Hello, testuser1!', html)
        self.assertIn('<form method="POST">', html)
        
        ## TESTS POST ##
        resp = self.client.post('/messages/new', data=dict(text='blue', form=''),
                                follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('@testuser1', html)
        self.assertIn('<p>blue</p>', html)
        
        
        
    ##############################################################################
    
    
    
    def test_show_message_view(self):
        """Tests the show message view"""

        ### Tests when not logged in ###
        resp = self.client.get('/messages/1', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        self.assertIn('<a href="/users/1">', html)
        self.assertIn('Message1', html)
        
        ### Tests when logged in ###
        self.login_for_test()
        resp = self.client.get('/messages/1', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Logout', html)
        self.assertIn('<a href="/users/1">', html)
        self.assertIn('Message1', html)
        
        ### Tries to grab non existent message ###
        resp = self.client.get('/messages/60', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        
    ##############################################################################
    
    
    
    def test_delete_messages(self):
        """Tests the delete message view"""
        
        ### Tests when not logged in ###
        resp = self.client.post('/messages/1/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        self.login_for_test()
        
        resp = self.client.post('/messages/2/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Message Deleted', html)
        self.assertIn('Logout', html)
        
        ### Tries to grab non existent message ###
        resp = self.client.post('/messages/60/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        