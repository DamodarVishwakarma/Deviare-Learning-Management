from rest_framework.routers import DefaultRouter
from main.viewsets import (TMForumUserResponseViewset, TMForumAssessmentUserDocument, TMForumAssessment, TMForumUserViewset, TMForumAssessmentDocumentExcel)
from django.urls import path, include
router = DefaultRouter()

router.register(r'user_assessment', TMForumUserViewset, basename='user_assessment',)
router.register(r'response', TMForumUserResponseViewset, basename='user_response',)

urlpatterns = router.urls
urlpatterns.extend([
    path(r'form/', TMForumAssessment.as_view()),
    path(r'user_doc/', TMForumAssessmentUserDocument.as_view()),
    path(r'excel_download/', TMForumAssessmentDocumentExcel.as_view())
])
