from django.urls import path, include
from main import views
from main.viewsets import TMForumAssessment, UserHasReport
urlpatterns = [
    # Auth Module
    path("authorize", views.Authorize.as_view()),
    path("customerlogo/<str:pk>", views.CustomerLogo.as_view()),
    path("forgetpassword", views.ForgetPassword.as_view()),
    path("resetpassword", views.ResetPassword.as_view()),
    path("myprofile", views.MyProfile.as_view()),
    path("editprofile", views.EditProfile.as_view()),
    path("changepassword", views.ChangePassword.as_view()),
    path("contactus", views.ContactUs.as_view()),
    # Administrator APIs
    path("superadmindashboard", views.SuperAdminDashboard.as_view()),
    path("superadminlist", views.SuperAdminList.as_view()),
    path("superadmincreate", views.SuperAdminCreate.as_view()),
    path("superadmindetail/<str:pk>", views.SuperAdminDetail.as_view()),
    path("disableaccount", views.DisableAccount.as_view()),
    # Customer APIs
    path("gcologistdashboard", views.GCologistDashboard.as_view()),
    path("gcologistdashboard/", views.GCologistDashboard.as_view()),
    path("customeradmindashboard", views.CustomerAdminDashboard.as_view()),
    path("projectadmindashboard", views.CustomerAdminDashboard.as_view()),
    path("customerlist", views.CustomerList.as_view()),
    path("customercreate", views.CustomerCreate.as_view()),
    path("customerdetail/<str:pk>", views.CustomerDetail.as_view()),
    # User APIs
    path("userdashboard", views.UserDashboard.as_view()),
    path("userlist", views.UserList.as_view()),
    path("usercreate", views.UserCreate.as_view()),
    path("userdetail/<str:pk>", views.UserDetail.as_view()),
    path("bulkuploadtemplate", views.BulkUploadTemplate.as_view()),
    path("bulkstorage", views.BulkStorage.as_view()),
    # Course APIs
    path("courselist", views.CourseList.as_view()),
    path("coursecreate", views.CourseCreate.as_view()),
    path("coursedetail/<str:pk>", views.CourseDetail.as_view()),
    path("simplilearncourses", views.SimpliLearnCourses.as_view()),
    path("coursedata", views.CourseData.as_view()),
    # path("microsoftcourses", views.MicrosoftCourses.as_view()),
    path("addusertocourse", views.CourseUserAssigmentAPIView.as_view()),
    path("gotocourse/<str:pk>", views.UserGoToCourseAPIView.as_view()),
    path("userstatusincourse", views.UserStatusInCourseAPIView.as_view()),
    # Drop-Downs
    path("countrylist", views.countrylist),
    path("customerdropdown", views.CustomerDropDown.as_view()),
    path("customeradmindropdown", views.CustomerAdminDropDown.as_view()),
    path("coursedropdown", views.CourseDropDown.as_view()),
    path("assessmentdropdown", views.AssessmentDropDown.as_view()),
    path("apprenticeshipdropdown", views.ApprenticeshipDropDown.as_view()),
    # TMForumconst
    path(r'tmforum/', include("main.tmforum_assessment.urls")),
    path(r'tmforum/struct', TMForumAssessment.as_view()),

    path(r"user_has_reports/", UserHasReport.as_view()),
    # PDF Reports 

    path(r"user_progress", views.user_progress),
    path(r"user_progress/pdf", views.UserProgressReport.as_view()),
    path(r"digital_readiness", views.digital_readiness),
    path(r"digital_readiness/pdf", views.CustomerDigitalReadinessReport.as_view()),
    path(r"user_learning_path/pdf", views.UserLearningPathReport.as_view()),
    # VGA
    path("vga", views.VGA.as_view()),
]
