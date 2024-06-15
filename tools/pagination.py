from rest_framework.pagination import LimitOffsetPagination
from tools.responders import ResponseWrapper
from collections import OrderedDict
from django.utils.translation import gettext_lazy as _
from rest_framework.compat import coreapi, coreschema
from rest_framework.utils.urls import remove_query_param, replace_query_param
from django.utils.encoding import force_str


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


def _divide_with_ceil(a, b):
    """
    Returns 'a' divided by 'b', with any remainder rounded up.
    """
    if a % b:
        return (a // b) + 1

    return a // b


class RestPagination(LimitOffsetPagination):
    offset_query_param = 'offset'
    offset_query_description = _('The page number of the results.')
    limit_query_param = 'limit'
    limit_query_description = _('Number of results to return per page.')

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name='page_size',
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Page Size',
                    description=force_str(self.limit_query_description)
                )
            ),
            coreapi.Field(
                name='page',
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Page',
                    description=force_str(self.offset_query_description)
                )
            )
        ]

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated(self, data):
        return OrderedDict([
            ('totalCount', self.count),
            ('pageCount', _divide_with_ceil(self.count, self.limit)),
            ('page', self.page),
            ('page_size', self.limit),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ])

    def get_paginated_response(self, data):
        return ResponseWrapper(self.get_paginated(data))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'totalCount': {
                    'type': 'integer',
                    'example': 123,
                },
                'pageCount': {
                    'type': 'integer',
                    'example': 123,
                },
                'page': {
                    'type': 'integer',
                    'example': 1,
                },
                'page_size': {
                    'type': 'integer',
                    'example': 10,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                },
                'data': schema,
            },
        }

    def get_limit(self, request):
        qp = request.query_params
        val = qp.get(self.limit_query_param, False)
        if val is False:
            val = qp.get('page_size', False)

        if val is not False:
            try:
                return _positive_int(
                    val,
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return None

    def get_offset(self, request):
        qp = request.query_params
        self.page = 1
        try:
            offset = _positive_int(
                qp[self.offset_query_param],
            )
            self.page = min(1, _divide_with_ceil(self.limit, offset)) if offset > 0 else 1
            return offset
        except (KeyError, ValueError):
            pass
        try:
            self.page = _positive_int(
                qp['page'],
            )
            return (self.page - 1) * self.limit
        except (KeyError, ValueError):
            return 0
