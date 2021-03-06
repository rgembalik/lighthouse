# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import create_team
from apps.organisations.models import Organisation
from apps.teams.models import Team


class TeamWebTest(WebTest):
    def test_can_click_through_existing_team_link(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        o = Organisation(name='New Org')
        o.save()
        team_name = 'New Team skippity bippity bop'
        t = Team(name=team_name, organisation=o)
        t.save()
        response = self.app.get(reverse('team-list'))
        response = self.app.get(response.html.find(
                'a',
                text=team_name
            ).attrs['href']
        )
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).get_text(strip=True)
        self.assertEquals(org_name, 'Team' + team_name)

    def test_show_number_of_members_two(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(name='two members', num_members=2)
        response = self.app.get(reverse('team-list'))

        self.assertIn(
            t.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'Total members: 2',
            response.html.find('ul', {"class": "team-info"}).text
        )

    def test_show_number_of_members_none(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(name='no members', num_members=0)
        response = self.app.get(reverse('team-list'))

        self.assertIn(
            t.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'This team has no members',
            response.html.find('ul', {"class": "team-info"}).text
        )

    def test_list_members(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(name='two members', num_members=2)
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_items = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('li')

        self.assertEqual(
            len(user_items),
            2
        )

        self.assertIn(
            'Team Member 1',
            user_items[0].text
        )

        self.assertIn(
            'Team Member 2',
            user_items[1].text
        )

    def test_list_members_ordering(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(
            name='two members', num_members=2,
            usernames={0: 'steve', 1: 'bob'}
        )
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_items = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('li')

        self.assertEqual(
            len(user_items),
            2
        )
        self.assertIn(
            'bob',
            user_items[0].text
        )

        self.assertIn(
            'steve',
            user_items[1].text
        )

    def test_list_members_names_link(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(
            name='two members', num_members=1
        )
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_links = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('a')

        self.assertEqual(
            len(user_links),
            1
        )

        response = response.click(user_links[0].text)

        self.assertIn(
            'Team Member 1',
            response.html.find(
                'h1', {"class": "form-title"}
            ).text
        )
