from django.urls import path

from blood_tests.views import upload_file

app_name = "blood_tests"
urlpatterns = [
    path("", upload_file, name="file"),
]
