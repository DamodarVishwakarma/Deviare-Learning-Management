from .serializers import (ProjectViewSerializer, Project)
from main.serializers import (
     GCIndexAssessmentSerializer,
     GCIndexReportSerializer
)
from main.models import (
    GCIndexAssessment,
    GCIndexReport,
    GCState
)
from main.tasks import (create_all_gcindex_tokens)
from notification.models import (EmailMessage)
from rest_framework import status as S, filters as rest_filter, serializers
from tools.viewsets import BaseModelViewSet, data_response
from rest_framework.decorators import action
from base64 import b64encode, b64decode
import pandas as pd

from django.http import FileResponse
from io import BytesIO, StringIO


class IsOwnerFilterBackend(rest_filter.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        if request.userAuth:
            if request.userAuth.sub_role in ["gcologist"] or request.userAuth.role in ["gcologist"]:
                return queryset.filter(gcologist=request.userAuth)
            if request.userAuth.role in ["projectadmin", "user", "customeradmin"]:
                return queryset.filter(user=request.userAuth)
        return queryset


class ProjectViewset(BaseModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectViewSerializer


class GCIndexAssessmentViewset(BaseModelViewSet):
    queryset = GCIndexAssessment.objects.all()
    serializer_class = GCIndexAssessmentSerializer
    filter_backends = [IsOwnerFilterBackend]

    @data_response
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @data_response
    def create(self, request, *args, **kwargs):
        if not request.userAuth:
            return dict(success=False, msg='You need to log in')

        if type(request.data) in (list, tuple):
            qs = self.get_queryset()
            existing = qs.values_list('user_id', flat=True)
            to_create = [rec for rec in request.data if rec['user'] not in existing]
            tc = [dict(state_id=1, **{f"{k}_id": v for k, v in rec.items()}) for rec in to_create]
            results = []
            s = [GCIndexAssessment(**kw) for kw in tc]

            for gc in s:
                gc.save()
                results.append(self.get_serializer(gc).data)
            s = GCIndexAssessment.objects.bulk_create(s)
            # serializer = serializers.ListSerializer(
            #     data=tc,
            #     child=self.serializer_class(
            #         context=self.get_serializer_context()
            #     )
            # )
            return dict(
                message='Successfully Created Entry',
                data=results
            )
        else:
            dat = request.data.copy()
            dat['state'] = 1
            serializer = self.get_serializer(data=dat)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            # l = serializer.data
            # if type(l) == list:
            #     s = GCIndexAssessment.objects.bulk_create([GCIndexAssessment(**kw) for l])
            headers = self.get_success_headers(serializer.data)
            create_all_gcindex_tokens.delay()
            return dict(
                data=serializer.data,
                headers=headers,
                message='Successfully Created Entry'
            )
        else:
            return dict(success=False, msg="Incorrect Data")

    @data_response
    @action(detail=False, methods=['GET'])
    def states(self, request, *args, **kwargs):
        return dict(success=True, msg="States Loaded", data=list(GCState.objects.values('id', 'name').order_by('id')))

    @data_response
    @action(detail=True, methods=['GET'])
    def pdf(self, request, *args, **kwargs):
        pipe = BytesIO()
        obj = self.get_object()
        pipe.write(obj.report.first().report)
        pipe.seek(0)
        resp = FileResponse(
            pipe, as_attachment=True,
            filename=f'GC Index Report - {obj.user.userName}.pdf'
        )
        resp['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return resp

    @data_response
    @action(detail=True, methods=['GET', 'POST'])
    def resend(self, request, *args, **kwargs):
        obj = self.get_object()
        em = EmailMessage.objects.filter(reference=str(obj.uuid),
                                         subject='Welcome to your GC Index Assessment',).first()
        em.recipient = kwargs.get('recipient', em.recipient)
        em.save()
        # em.refresh
        em.send()
        return dict(success=True, msg="Sent")


class GCIndexReportViewset(BaseModelViewSet):
    queryset = GCIndexReport.objects.all()
    serializer_class = GCIndexReportSerializer
