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
        
        
        
    def test_signup_view(self):
        """Tests user signup view"""
        ##### TESTS GET #####
                    
        resp = self.client.get('/signup')
        html = resp.get_data(as_text=True)

        self.assertTrue(resp.status_code == 200)
        self.assertIn('Join Warbler today.</h2>', html)
        
        
        
        ##### TESTS POST #####
        
        resp = self.client.post('/signup',data=dict(username='testuser4',
                                password='HASHED_PASSWORD',
                                email='test4@test.com',
                                image_url='null',
                                form=''),
                                follow_redirects=True
                                )
        html = resp.get_data(as_text=True)
        
        new_user = User.query.filter_by(username='testuser4').first()
        self.assertIsInstance(new_user, User)
        self.assertTrue(resp.status_code == 200)
        self.assertIn('<p>@testuser4</p>', html)
        
        
        
    ##############################################################################
        
        
        
    def test_login_view(self):
        """Tests user login view"""
        
        ##### TESTS GET #####
        resp = self.client.get('/login')
        html = resp.get_data(as_text=True)
        
        self.assertTrue(resp.status_code == 200)
        self.assertIn('<form method="POST" id="user_form">', html)
        
        
        
        ##### TESTS POST #####
        
        ### Tests successful login ###
        resp = self.client.post('/login',
                                data = dict(username="testuser1", password="HASHED_PASSWORD", form=''),
                                follow_redirects=True
                                )
        html = resp.get_data(as_text=True)
            
        
        self.assertTrue(resp.status_code == 200)
        self.assertIn('Hello, testuser1', html)

        ### Tests login with invalid credentials ###
        resp = self.client.post('/login',
                                data = dict(username="FAKE_USER", password="FAKE_PASSWORD", form=''),
                                follow_redirects=True
                                )
        html = resp.get_data(as_text=True)
            
        self.assertTrue(resp.status_code == 200)
        self.assertIn('Invalid credentials.', html)
        
    
    
    ##############################################################################
    
    
    
    def test_logout_view(self):
        """Tests the logout functionality"""
        self.login_for_test()
        
        resp2 = self.client.post('/logout', follow_redirects=True)
        
        html = resp2.get_data(as_text=True)
        
        self.assertTrue(resp2.status_code == 200)
        self.assertIn('Sucessfully logged out', html)
        
        
        
    ##############################################################################
        
        
        
    def test_users_view(self):
        """Tests the all/search users view"""
        
        ### Tests when not logged in ###
        resp = self.client.get('/users')
        html = resp.get_data(as_text=True)
        
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        
        ### Tests a logged in user ###
        self.login_for_test()
        
        resp = self.client.get('/users')
        
        html = resp.get_data(as_text=True)
        
        self.assertTrue(resp.status_code == 200)
        self.assertIn('@testuser1', html)
        self.assertIn('@testuser2', html)
        self.assertIn('@testuser3', html)
    
    
    
    ##############################################################################
    
    
    
    def test_user_profile_view(self):
        """Tests user profile view"""
        
        ### Tests when not logged in ###
        resp = self.client.get('/users/1')
        html = resp.get_data(as_text=True)
        
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        
        ### Tests a logged in user ###
        self.login_for_test()
        
        resp = self.client.get('/users/1')

        html = resp.get_data(as_text=True)
        
        self.assertTrue(resp.status_code == 200)
        self.assertIn('Logout', html)
        self.assertIn('<p>Message1</p>', html)
        self.assertIn('<p>Message2</p>', html)
        
        ### Tests for non existent user ###
        resp = self.client.get('/users/60')
        html = resp.get_data(as_text=True)

        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
    
    
    ##############################################################################



    def test_user_following_view(self):
        """Tests the 'user following' view"""
        ### Tests when not logged in ###
        resp = self.client.get('/users/1/following', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)

        ### Tests for logged in user ###
        self.login_for_test()
        
        resp = self.client.get('/users/1/following', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Hello, testuser1!', html)
        self.assertIn('Logout', html)
        self.assertIn('<p>@testuser2</p>', html)
        
        
        
    ##############################################################################



    def test_user_followers_view(self):
        """Tests the 'user followers' view"""
        ### Tests when not logged in ###
        resp = self.client.get('/users/1/followers', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)

        ### Tests for logged in user ###
        self.login_for_test()
        
        resp = self.client.get('/users/1/followers', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Hello, testuser1!', html)
        self.assertIn('Logout', html)
        self.assertIn('<p>@testuser2</p>', html)
            
    
        
    ##############################################################################
    
    
    
    def test_user_add_follow_view(self):
        """Tests the 'add follow' to user view"""

        ### Tests when not logged in ###
        
        resp = self.client.post('/users/follow/3', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        
        ### Tests logged in user ###
        ### Has one of the initally setup users follow the user added in the *test_signup_view* ###
        self.login_for_test()
        
        resp = self.client.post('/users/follow/3', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('<a href="/users/1/following">2</a>', html)
        self.assertIn('Followed testuser3', html)
        self.assertIn('Logout', html)
        self.assertIn('<p>@testuser3</p>', html)
        
    
    
    ##############################################################################
    
    
    
    def test_stop_following_user_view(self):
        """Tests the 'stop following' user view"""

        ### Tests when user not logged in ###
        
        resp = self.client.post('/users/stop-following/3', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        
        ### Tests logged in user ###
        ### Unfollows the user followed in *test_user_add_follow_view* ###
        self.login_for_test()
        self.client.post('/users/follow/3', follow_redirects=True)
        
        resp = self.client.post('/users/stop-following/3', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Logout', html)
        self.assertIn('testuser3 unfollowed.', html)
        self.assertIn('<a href="/users/1/following">1</a>', html)
        
        ### Tests for non existent user ###
        resp = self.client.post('/users/stop-following/60')
        html = resp.get_data(as_text=True)

        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        
        
    ##############################################################################



    def test_edit_user_profile_view(self):
        """Tests updating the user profile"""
        
        ##### Tests when not logged in #####
        
        ### TESTS GET ###
        resp = self.client.get('/users/profile', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### TESTS POST ###
        resp = self.client.post('/users/profile', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ##### Tests when logged in #####
        self.login_for_test()
            
        ### TESTS GET ###
        resp = self.client.get('/users/profile', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Hello, testuser1!', html)
        self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', html)
        
        ### TESTS POST ###
        ## With correct credentials ##
        resp = self.client.post('/users/profile', data=dict(
            username='testuser1', email='test1@test.com',
            image_url='null', header_image_url='null', password='HASHED_PASSWORD', bio='none', form=''),
                                follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Sucessfully updated profile!', html)
        self.assertIn('Logout', html)
        
        ## With incorrect credentials ##
        resp = self.client.post('/users/profile', data=dict(
            username='testuser1', email='test1@test.com',
            image_url='null', header_image_url='null', password='FAKE_PASSWORD', bio='none', form=''),
                                follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Invalid credentials.', html)
        self.assertIn('Logout', html)
        
        
        
    ##############################################################################
    
    
    
    def test_delete_users_view(self):
        """Tests deleting a user profile"""
        ### Tests when not logged in ###
        resp = self.client.post('/users/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        self.client.post('/signup',data=dict(username='testuser4',
                                password='HASHED_PASSWORD',
                                email='test4@test.com',
                                image_url='null',
                                form=''),
                                follow_redirects=True
                                )
        self.client.post('/login',
                                data = dict(username="testuser4", password="HASHED_PASSWORD", form=''),
                                follow_redirects=True
                                )
        resp = self.client.post('/users/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Account deleted succesfully.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        
        
    ##############################################################################

    
    
    def test_add_like_view(self):
        """Tests the add like view"""

        ### Tests when not logged in ###
        resp = self.client.post('/users/add_like/3', follow_redirects=True)
        html = resp.get_data(as_text=True)
       
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        self.login_for_test()
        resp = self.client.post('/users/add_like/3', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('<a href="/users/1/likes">1</a>', html)
        self.assertIn('Logout', html)
        
        ### Tests for non existent message ###
        resp = self.client.post('/users/add_like/60')
        html = resp.get_data(as_text=True)

        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        
    ##############################################################################
    
    
    
    def test_unlike_view(self):
        """Tests unliking a post"""

        ### Tests when not logged in ###
        resp = self.client.post('/users/unlike/3', follow_redirects=True)
        html = resp.get_data(as_text=True)
       
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        self.login_for_test()
        
        resp = self.client.post('/users/unlike/3', follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertIn('Unliked message', html)
        self.assertIn('Logout', html)
        self.assertIn('<a href="/users/1/likes">0</a>', html)
        
        ### Tests for non existent message ###
        resp = self.client.post('/users/unlike/60')
        html = resp.get_data(as_text=True)

        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        
    ##############################################################################
    
    
    
    def test_show_liked_messages(self):
        """Tests the show liked messages view"""

        ### Tests when not logged in ###
        resp = self.client.get('/users/3/likes', follow_redirects=True)
        html = resp.get_data(as_text=True)
       
        self.assertIn('Access unauthorized.', html)
        self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
        self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
        ### Tests when logged in ###
        self.login_for_test()
        resp = self.client.get('/users/1/likes', follow_redirects=True)
        html = resp.get_data(as_text=True)
       
        self.assertIn('01 December 2021', html)
        self.assertIn('@testuser2', html)
        self.assertIn('Logout', html)
        
        ### Tests for non existent user ###
        resp = self.client.get('/users/60/likes')
        html = resp.get_data(as_text=True)

        self.assertIn('404 Not Found', html)
        self.assertTrue(resp.status_code == 404)
        
        
        
        