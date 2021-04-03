from django.contrib.admin.views.main import ChangeList
from django.db import connections

class RawChangeList(ChangeList):
    """
    Extended Django ChangeList to be able show data from RawQueryset.
    """
    def get_count(self):
        connection = connections[self.queryset.db]
        with connection.cursor() as c:
            if connection.vendor == 'microsoft':  # CTE in subquery is not working in SQL Server
                c.execute(self.queryset.raw_query)
                c.execute('SELECT @@ROWCOUNT')
            else:
                query = 'SELECT COUNT(*) FROM ({query}) AS sq'
                c.execute(query.format(query=self.queryset.raw_query))

            return c.fetchone()[0]

    def get_queryset_slice(self):
        connection = connections[self.queryset.db]
        if connection.vendor == 'microsoft':
            # SQL Server needs ordered query for slicing
            if hasattr(self.queryset, 'ordered') and self.queryset.ordered:
                query = '{query}'
            else:
                query = '{query} ORDER BY 1'
            query += ' OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY'
        else:
            query = '{query} LIMIT {limit} OFFSET {offset}'

        return self.queryset.model.objects.raw(
            query.format(
                query=self.queryset.raw_query,
                offset=self.page_num * self.list_per_page,
                limit=(self.page_num + 1) * self.list_per_page - self.page_num * self.list_per_page,
            )
        )

    def get_queryset(self, request):
        """
        Overriding to avoid applying filters in ChangeList because RawQueryset has not filter method.
        So any filters has to be applied manually for now.
        """
        qs = self.root_queryset
        if not hasattr(qs, 'count'):
            qs.count = lambda: self.get_count()
        return qs

    def get_results(self, request):
        if self.show_all:
            qs = self.queryset
        else:
            qs = self.get_queryset_slice()

        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)

        self.result_count = paginator.count
        self.show_full_result_count = False
        self.show_admin_actions = True
        self.full_result_count = 0
        self.result_list = list(qs)
        self.can_show_all = True
        self.multi_page = True
        self.paginator = paginator