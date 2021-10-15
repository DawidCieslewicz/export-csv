from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http.response import HttpResponse
from django.shortcuts import render

from blood_tests.utils.csv_handlers import BloodTestHandler


class UploadFileForm(forms.Form):
    file = forms.FileField()


def handle_uploaded_file(file: InMemoryUploadedFile):
    csv_file = BloodTestHandler(blood_test_file=file)

    csv_file.handle_request()


def upload_file(request):

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponse("wysłano")
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})
