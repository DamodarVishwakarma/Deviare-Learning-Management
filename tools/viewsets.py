import datetime
import uuid
import pytz
from rest_framework.viewsets import ModelViewSet

import traceback
from rest_framework import status as S, serializers

from tools.decorators import data_response, ResponseWrapper
from tools.pagination import RestPagination

from datetime import datetime

from django.db import models


class BaseModelViewSet(ModelViewSet):

    response_class = ResponseWrapper
    pagination_class = RestPagination
    list_serializer_class = None
    # permission_classes = [IsAuthenticated]

    @data_response
    def create(self, request, *args, **kwargs):
        if type(request.data) in (list, tuple):
            serializer = serializers.ListSerializer(
                data=request.data,
                child=self.serializer_class(
                    context=self.get_serializer_context()
                )
            )
        else:
            serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return dict(
                data=serializer.data,
                status=S.HTTP_201_CREATED,
                headers=headers,
                msg='Successfully Created Entry'
            )
        else:
            return dict(success=False, msg="Incorrect Data")

    def perform_create(self, serializer):
        serializer.save()

    @data_response
    def update(self, request, *args, **kwargs):
        data = request.data
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', True)
            print(instance, data, str(partial))
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return dict(data=serializer.data, status=S.HTTP_202_ACCEPTED, success=True, msg='Data Saved')
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            return dict(success=False, msg=str(e), status=406)

    def flatten_data(self, result, request, *args, **kwargs):
        # flatten = request.query_params.get('flatten', kwargs.get('flatten', False))
        # if flatten is not False:
        #     result = list(map(as_lookup, result)) if type(result) in (list, tuple, ReturnList) else as_lookup(result)
        return result

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.request is not None:
            if self.request.method == 'GET':
                if self.list_serializer_class and kwargs.get('many', False):
                    return self.list_serializer_class(*args, **kwargs)
        return serializer_class(*args, **kwargs)

    def get_paginated(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert isinstance(self.paginator, RestPagination)
        return self.paginator.get_paginated(data)
    # def filter_queryset(self, queryset):

    def list_data(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated(
                self.flatten_data(serializer.data, request, *args, **kwargs)
            )

        serializer = self.get_serializer(queryset, many=True)
        return self.flatten_data(serializer.data, request, *args, **kwargs)

    @data_response
    def list(self, request, *args, **kwargs):

        if not self.request:
            self.request = request
        try:
            result = self.list_data(request, *args, **kwargs)
        except Exception as e:
            raise dict(success=False,  msg=str(e), status=404)
        return dict(data=result, success=True, msg='Got records', status=S.HTTP_200_OK)

    def retrieve_data(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.flatten_data(serializer.data, request, *args, **kwargs)

    @data_response
    def retrieve(self, request, *args, **kwargs):
        result = self.retrieve_data(request, *args, **kwargs)
        return dict(data=result, success=True, msg='Data Found', status=S.HTTP_200_OK)

    @property
    def auth_role(self):
        if self.auth_user:
            return self.auth_user.role
        return 'Anonymous'

    @property
    def auth_user(self):
        if self.request is not None:
            user = self.request.userAuth
            if user is not None:
                return user
        return None