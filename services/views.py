from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.exceptions import ValidationError
from main.models import Assessment, Experiment, Deployment
from main.serializers import (
    AssessmentSerializer,
    ExperimentSerializer,
    DeploymentSerializer,
)
from main.views import responsedata


# Assessments


class AssessmentList(generics.ListAPIView):
    """To list assessments"""

    search_fields = ["name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return Assessment.objects.all().order_by("name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        instance = self.filter_queryset(self.get_queryset())
        assessment_list = list(instance.values())

        pagenumber = request.GET.get("page", 1)
        paginator = Paginator(assessment_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class CreateAssessment(APIView):
    """To create an assessment"""

    def post(self, request):

        if (
            request.data.get("name")
            and request.data.get("description")
            and request.data.get("duration")
            and request.data.get("link")
        ):
            serializer = AssessmentSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    responsedata(
                        True, "Assessment created successfully", serializer.data
                    ),
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                responsedata(False, "Details not provided"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class AssessmentDetail(APIView):
    """Retrieve, update or delete an assessment"""

    def get(self, request, pk):
        assessment = Assessment.objects.filter(uuid=pk)
        serializer = AssessmentSerializer(assessment, many=True)
        return Response(
            responsedata(True, "Assessment retrieved successfully", serializer.data),
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        assessment = Assessment.objects.filter(uuid=pk).first()
        serializer = AssessmentSerializer(assessment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                responsedata(True, "Assessment updated successfully", serializer.data),
                status=status.HTTP_200_OK,
            )
        return Response(
            responsedata(False, "Something went wrong", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        assessment = Assessment.objects.filter(uuid=pk)
        assessment.delete()
        return Response(
            responsedata(True, "Assessment Deleted"), status=status.HTTP_200_OK
        )


class ExperimentList(generics.ListAPIView):
    """To list Experiments"""

    search_fields = ["name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return Experiment.objects.all().order_by("name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        instance = self.filter_queryset(self.get_queryset())
        experiment_list = list(instance.values())

        pagenumber = request.GET.get("page", 1)
        paginator = Paginator(experiment_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class CreateExperiment(APIView):
    """To create an Experiment"""

    def post(self, request):

        if (
            request.data.get("name")
            and request.data.get("description")
            and request.data.get("link")
        ):
            serializer = ExperimentSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    responsedata(
                        True, "Experiment created successfully", serializer.data
                    ),
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                responsedata(False, "Details not provided"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class ExperimentDetail(APIView):
    """Retrieve, update or delete an Experiment"""

    def get(self, request, pk):
        experiment = Experiment.objects.filter(uuid=pk)
        serializer = ExperimentSerializer(experiment, many=True)
        return Response(
            responsedata(True, "Experiment retrieved successfully", serializer.data),
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        experiment = Experiment.objects.filter(uuid=pk).first()
        serializer = ExperimentSerializer(experiment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                responsedata(True, "Experiment updated successfully", serializer.data),
                status=status.HTTP_200_OK,
            )
        return Response(
            responsedata(False, "Something went wrong", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        experiment = Experiment.objects.filter(uuid=pk)
        experiment.delete()
        return Response(
            responsedata(True, "Experiment Deleted"), status=status.HTTP_200_OK
        )


# Deployments


class DeploymentList(generics.ListAPIView):
    """To list Deployments"""

    search_fields = ["name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return Deployment.objects.all().order_by("name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        instance = self.filter_queryset(self.get_queryset())
        deployment_list = list(instance.values())

        pagenumber = request.GET.get("page", 1)
        paginator = Paginator(deployment_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class CreateDeployment(APIView):
    """To create an Deployment"""

    def post(self, request):

        if (
            request.data.get("name")
            and request.data.get("description")
            and request.data.get("repository")
        ):
            serializer = DeploymentSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    responsedata(
                        True, "Deployment created successfully", serializer.data
                    ),
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                responsedata(False, "Details not provided"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class DeploymentDetail(APIView):
    """Retrieve, update or delete an Deployment"""

    def get(self, request, pk):
        deployment = Deployment.objects.filter(uuid=pk)
        serializer = DeploymentSerializer(deployment, many=True)
        return Response(
            responsedata(True, "Deployment retrieved successfully", serializer.data),
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        deployment = Deployment.objects.filter(uuid=pk).first()
        serializer = DeploymentSerializer(deployment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                responsedata(True, "Deployment updated successfully", serializer.data),
                status=status.HTTP_200_OK,
            )
        return Response(
            responsedata(False, "Something went wrong", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        deployment = Deployment.objects.filter(uuid=pk)
        deployment.delete()
        return Response(
            responsedata(True, "Deployment Deleted"), status=status.HTTP_200_OK
        )
