# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation

import re


class UserTest(TestCase):
    def setUp(self):
        u = User(slug='user0001')
        u.save()

    def test_can_create_user(self):
        u = User(slug='user0002')
        u.save()
        self.assertTrue(u.slug)

    def test_cannot_create_duplicate_user(self):
        u = User(slug='user0002')
        u.save()
        self.assertTrue(u.slug)
        u = User(slug='user0001')
        with self.assertRaises(IntegrityError):
            u.save()

    def test_user_can_have_multiple_teams_which_have_multiple_users(self):
        o = Organisation(name='New Org')
        o.save()

        t1 = Team(name='Team Awesome', organisation=o)
        t1.save()
        t2 = Team(name='Team Great', organisation=o)
        t2.save()

        u1 = User(slug='teamplayer')
        u1.save()

        u1.teams.add(t1)
        u1.teams.add(t2)
        u1.save()

        u2 = User(slug='teamplayer2')
        u2.save()

        u2.teams.add(t2)
        u2.save()

        self.assertIn(u1, t1.user_set.all())
        self.assertIn(u1, t2.user_set.all())
        self.assertNotIn(u2, t1.user_set.all())
        self.assertIn(u2, t2.user_set.all())

        self.assertEqual(len(t1.user_set.all()), 1)
        self.assertEqual(len(t2.user_set.all()), 2)


class UserWebTest(WebTest):

    def test_cannot_create_slugless_user(self):
        form = self.app.get(reverse('login-view')).form
        response = form.submit().follow().follow()
        login_label = response.html.find(
            'label',
            attrs={'class': 'form-label-bold', 'for': 'id_slug'}
        )
        self.assertTrue(login_label)
        self.assertEquals(login_label.text.strip(), 'Login with ID.')

    def test_create_new_user(self):
        #   got to the login form, and enter a user ID, this will sign us up.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit().follow()

        #   Now go to the user profile page
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001'}
            )
        )
        #   Check that we have the user slug in the name in the nav bar
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001'}
            )
        )

    def test_can_login_as_existing_user(self):
        u = User(slug='user0001')
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Now go to the user profile page
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001'}
            )
        )
        #   Check that we have the user slug in the name in the nav bar
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001'}
            )
        )

    def test_update_button_shows_on_user_profile(self):
        #   Create the two users
        u1 = User(slug='user0001')
        u1.save()
        u2 = User(slug='user0002')
        u2.save()
        #   Login as the first user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Now goto the profile page for the 1st user and see if the button
        #   exists
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertTrue(button)

        #   Now visit the profile page for the not logged in user
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0002'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertFalse(button)

    #   Test that a user can join an existing team when editing their
    #   own profile
    def test_adding_new_existing_team(self):
        u = User(slug='user0001')
        u.save()
        o = Organisation(name='org0001')
        o.save()
        t = Team(name='team0001', organisation=o)
        t.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        form.submit()

        #   Go to the user's profile page and assert that the team is NOT
        #   showing up in the list of teams they are a member of.
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        self.assertFalse(response.html.find('a', text=re.compile(r'team0001')))

        #   Now go to the update profile page and check the first team
        #   in the list of teams.
        form = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'})).form
        form.get('team', index=0).checked = True
        form.submit()

        #   Go back to the users profile page to see if the team is now
        #   on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))

    #   Test that the user can join a new team connecting it to an existsing
    #   organisation
    def test_adding_new_team_existing_organisation(self):
        u = User(slug='user0001')
        u.save()
        o = Organisation(name='org0001')
        o.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        form.submit()

        #   Now go to the update profile page and check the first team
        #   in the list of teams.
        form = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'})).form
        form['name'] = 'team0001'
        form['organisation'].value = o.pk
        form.submit()

        #   Go back to the users profile page to see if the team is now
        #   on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))

    #   Test that the user can join a new team connecting it to an existsing
    #   organisation
    def test_adding_new_team_new_organisation(self):
        u = User(slug='user0001')
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        form.submit()

        #   Now go to the update profile page and check the first team
        #   in the list of teams.
        form = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'})).form
        form['name'] = 'team0001'
        form['new_organisation'] = 'org0001'
        form.submit()

        #   Go back to the users profile page to see if the team and
        #   organisation is now on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))
        self.assertTrue(response.html.find('a', text=re.compile(r'org0001')))

    def test_alert_for_missing_username(self):
        #   This user doesn't have a username
        User(slug='user0001').save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'}))

        #   Check that we have an error summary at the top
        self.assertTrue(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )

    def test_alert_for_missing_other_information(self):

        update_page = reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'})
        check_str = 'Please add additional information'

        def find_alert(response):
            return response.html.find(
                        'h1',
                        attrs={'class': 'alert-summary-heading'}
                        )

        #   create the user and log them in
        u = User(slug='user0001', username='User 0001')
        u.save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        # go to the update page and check for the alert
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = 'By phone'
        u.phone = '01777777'
        u.email = ''
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = 'By phone'
        u.phone = ''
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = ''
        u.phone = '01777777'
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = ''
        u.best_way_to_contact = 'By phone'
        u.phone = '01777777'
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

    def test_no_error_alert_for_all_information(self):
        #   This user has all the information
        User(
            slug='user0001',
            username='User 0001',
            best_way_to_find='In the kitchen',
            best_way_to_contact='By phone',
            phone='01777777',
            email='test@test.com',
        ).save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'}))

        #   Check that we don't have an error or alert summary
        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )

        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'alert-summary-heading'}
            )
        )
