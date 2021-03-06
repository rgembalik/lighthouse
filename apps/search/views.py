# (c) Crown Owned Copyright, 2016. Dstl.

import csv
from datetime import timedelta

from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, View

from .models import SearchQuery


class SearchStats(TemplateView):
    model = SearchQuery
    template_name = 'search/search_stats.html'

    def get_context_data(self, **kwargs):
        context = super(SearchStats, self).get_context_data(**kwargs)
        today = timezone.now().replace(hour=0, minute=0, second=0)
        month_ago = today - timedelta(days=30)

        queries_last_30_days = SearchQuery.objects.filter(
            when__gt=month_ago
        ).values(
            'term',
            'term__query'
        )
        top_queries = queries_last_30_days.annotate(
            total_searches=Count('term')
        )

        top_queries = top_queries.order_by('-total_searches')
        context['top_searches'] = top_queries[:10]
        context['top_unfulfilled_searches'] = queries_last_30_days.exclude(
            results_length__gt=0
        ).values(
            'term',
            'term__query'
        ).annotate(
            total_searches=Count('term')
        ).order_by('-total_searches')

        return context


class SearchStatsCSV(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        date = timezone.now().strftime('%Y_%m_%d')
        response['Content-Disposition'] = \
            'attachment; filename="lighthouse_search_full_%s.csv"' % date

        writer = csv.writer(response)
        writer.writerow(['Date', 'User', 'Term', 'Number of Results'])
        for query in SearchQuery.objects.all():
            writer.writerow([
                query.when.strftime("%Y-%m-%d %H:%M:%S"),
                query.user.userid,
                query.term,
                query.results_length
            ])

        return response
