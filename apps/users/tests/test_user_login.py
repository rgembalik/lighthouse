# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.users.models import User


class UserWebTest(WebTest):
    def test_can_login_as_existing_user(self):
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Now go to the user profile page
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001com'}
            )
        )
        #   Check that we have the user slug in the name in the nav bar
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
