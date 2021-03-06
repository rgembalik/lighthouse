# (c) Crown Owned Copyright, 2016. Dstl.

import csv
from datetime import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import make_aware

from django_webtest import WebTest

from ..models import Link
from testing.common import make_user, login_user
from haystack.management.commands import rebuild_index


class LinkSearchResults(WebTest):
    def setUp(self):
        self.user = make_user()
        self.link = Link.objects.create(
            name='Google',
            destination='https://google.com',
            description='Internet search',
            owner=self.user,
            is_external=False,
        )

        self.link.categories.add('search')

        self.other_link = Link.objects.create(
            name='Google Mail',
            destination='https://mail.google.com',
            description='Internet email',
            owner=self.user,
            is_external=True,
        )

        self.other_link.categories.add('email')
        self.other_link.categories.add('search')

        self.third_link = Link.objects.create(
            name='Google Chat',
            destination='https://chat.google.com',
            description='Internet chat',
            owner=self.user,
            is_external=True,
        )

        self.third_link.categories.add('chat')

        self.fourth_link = Link.objects.create(
            name='Bing Translate',
            destination='https://translate.bing.com',
            description="Bing's a pretty good translation service. Run, yeah?",
            owner=self.user,
            is_external=True,
        )

        self.fourth_link.categories.add('language')
        self.assertTrue(login_user(self, self.user))

        rebuild_index.Command().handle(interactive=False, verbosity=0)

    def test_search_for_tool_shows_both(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            search_url = '%s?q=google' % reverse('link-list')
            response = self.app.get(search_url)

        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 3)

    def test_search_for_broad_match_shows_three(self):
        search_url = '%s?q=google' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 3)
        self.assertIn('Google', search_results_list.text)
        self.assertIn('Google Mail', search_results_list.text)
        self.assertIn('Google Chat', search_results_list.text)

    def test_search_for_category_query_matches_on_categories(self):
        search_url = '%s?q=language' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Bing Translate', search_results_list.text)

    def test_search_for_internal_query_matches_on_categories(self):
        search_url = '%s?q=internal' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        self.assertIsNotNone(search_results_list)
        results = search_results_list.findAll('li')
        # Two because of Lighthouse
        self.assertEquals(len(results), 3)
        self.assertIn('Google', search_results_list.text)

    def test_search_for_external_query_matches_on_categories(self):
        search_url = '%s?q=external' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        self.assertIsNotNone(search_results_list)
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 3)
        self.assertIn('Google Mail', search_results_list.text)
        self.assertIn('Google Chat', search_results_list.text)
        self.assertIn('Bing Translate', search_results_list.text)

    def test_search_for_first_shows_one(self):
        search_url = '%s?q=search' % reverse('link-list')
        response = self.app.get(search_url)
        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 2)
        self.assertIn('Google', results[0].text)
        self.assertIn('Google Mail', results[1].text)

    def test_search_for_second_shows_one(self):
        search_url = '%s?q=email' % reverse('link-list')
        response = self.app.get(search_url)
        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Google Mail', results[0].text)

    def test_search_for_desc_conjugated_word_shows_one(self):
        search_url = '%s?q=running' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        self.assertIsNotNone(search_results_list)
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Bing Translate', results[0].text)

    def test_search_for_title_conjugated_word_shows_one(self):
        search_url = '%s?q=chatting' % reverse('link-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='link-results')
        self.assertIsNotNone(search_results_list)
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Google Chat', results[0].text)

    def test_search_for_flibble_shows_none(self):
        search_url = '%s?q=flibble' % reverse('link-list')
        response = self.app.get(search_url)
        self.assertIsNone(response.html.find(id='link-results'))

    def test_search_twice_with_different_terms(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            search_url = '%s?q=flibble' % reverse('link-list')
            response = self.app.get(search_url)
            self.assertIsNone(response.html.find(id='link-results'))

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 2, 0))
            search_url = '%s?q=chat' % reverse('link-list')
            response = self.app.get(search_url)

        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 1)

        response = self.app.get(reverse('search-stats'))

        csv_download_link = response.html.find(
            None,
            {"id": "csv-download-all"}
        )

        self.assertEquals(
            reverse('search-stats-csv'),
            csv_download_link.get('href')
        )
        self.assertIsNotNone(csv_download_link)

    def test_search_with_no_query_is_valid(self):
        empty_search_url = reverse('link-list')
        response = self.app.get(empty_search_url)
        form = response.form

        self.assertEquals(response.status_code, 200)
        self.assertEquals(form['q'].value, '')

    def test_search_with_empty_query_is_valid(self):
        empty_search_url = '%s?q=' % reverse('link-list')
        response = self.app.get(empty_search_url)
        form = response.form

        self.assertEquals(response.status_code, 200)
        self.assertEquals(form['q'].value, '')

    def test_search_stats_csv(self):
        self.test_search_twice_with_different_terms()

        response = self.app.get(reverse('search-stats-csv'))
        lines = response.body.decode().split("\r\n")
        dialect = csv.Sniffer().sniff(response.body.decode())
        reader = csv.DictReader(lines, dialect=dialect)

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Date': '2016-03-01 10:00:00',
            'Term': 'flibble',
            'Number of Results': '0',
        })

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Date': '2016-03-01 10:02:00',
            'Term': 'chat',
            'Number of Results': '1',
        })
