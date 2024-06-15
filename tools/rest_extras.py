from rest_framework import serializers
import pandas as pd


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):

        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        self.url_field_name = 'uuid'
        self.oid = 'DFMS:'

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        # print(dir(self.Meta))
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    # @classmethod
    # def serializer_qs(cls):
    #     return


class DataFrameListSerializer(serializers.ListSerializer):
    """
    A ModelSerializer that uses internal DataFrame
    """
    @property
    def df(self):
        d = self.data
        return d if isinstance(d, pd.DataFrame) else pd.DataFrame(d)

