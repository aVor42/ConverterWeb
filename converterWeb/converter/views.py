import os
from uuid import uuid4
from zipfile import ZipFile

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound, HttpRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
from transliterate import translit
import ffmpy

format_contenttypes = {
    "zip": "application/zip",
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "avi": "video/x-msvideo",
    "mp4": "video/mp4",
    "mkv": "video/x-matroska"
}

audio_formats = ["wav", "mp3", "ogg"]

video_formats = ["avi", "mp4", "mkv"]

video_format_convert_params = {
    "avi": "-f avi",
    "mp4": "-f mp4",
    "mkv": "-c:v vp9 -c:a libvorbis"
}


def index(request):
    return render(request, template_name="converter/index.html")


def audio_converter(request):
    return render(request, template_name="converter/audioConverter.html")


def video_converter(request):
    return render(request, template_name="converter/videoConverter.html")


def audiofile_convert(filename: str, format: str, path: str):
    name = filename.rsplit(".", 1)[0]
    old_format = filename.rsplit(".", 1)[1]

    file_path = f"{path}\\{filename}"
    if old_format == "wav":
        file = AudioSegment.from_wav(file_path)
    elif old_format == "mp3":
        file = AudioSegment.from_mp3(file_path)
    elif old_format == "ogg":
        file = AudioSegment.from_ogg(file_path)
    else:
        file = None

    new_filename = f"{name}.{format}"
    i = 0
    while os.path.isfile(f"{path}\\{new_filename}"):
        i += 1
        new_filename = f"{name}_{i}.{format}"

    file.export(f"{path}\\{new_filename}", format)
    return new_filename


@csrf_exempt
def audio_convert(request: HttpRequest):
    if request.method == "POST" and is_valid_audio_request(request):
        try:
            if len(request.FILES) == 1:
                filename = single_audio_convert(request.FILES.get("file 0"), request.POST['format'])
                out_format = request.POST['format']
            else:
                filename = multy_audio_convert(request.FILES.items(), request.POST['format'])
                out_format = "zip"
            fs = FileSystemStorage()
            file = open(f"{fs.base_location}\\{filename}", "rb")
            response = HttpResponse()
            response.write(file.read())
            response['Content-Type'] = format_contenttypes[out_format]
            response['Content-Length'] = os.path.getsize(f"{fs.base_location}\\{filename}")
            response['Content-Disposition'] = f"attachment;filename*=UTF-8''{translit(filename, language_code='ru', reversed=True)}"
            #  fs.delete(filename)
        except IOError:
            response = HttpResponseNotFound("Неизвестная ошибка")
        return response
    return HttpResponseNotFound("Неизвестная ошибка")


def is_valid_audio_request(request: HttpRequest):
    is_valid_format = False
    for format in audio_formats:
        if format == request.POST["format"]:
            is_valid_format = True
            break

    for _, file in request.FILES.items():
        is_valid_file = False
        for format in audio_formats:
            if format == os.path.splitext(file.name)[1][1:]:
                is_valid_file = True
                break
        if not is_valid_file:
            return False

    return is_valid_format and len(request.FILES) != 0


def single_audio_convert(file, format):
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    new_filename = audiofile_convert(filename, format, fs.base_location)
    fs.delete(filename)
    return new_filename


def multy_audio_convert(files, format):
    fs = FileSystemStorage()
    zip_name = str(uuid4())
    zipfile = ZipFile(f"{fs.base_location}\\{zip_name}.zip", "w")
    for key, file in files:
        new_filename = single_audio_convert(file, format)
        zipfile.write(f"{fs.base_location}\\{new_filename}", arcname=new_filename)
        fs.delete(new_filename)
    return f"{zip_name}.zip"


@csrf_exempt
def video_convert(request):
    if request.method == "POST":
        try:
            if len(request.FILES) == 1:
                filename = single_video_convert(request.FILES.get("file 0"), request.POST['format'])
                out_format = request.POST['format']
            else:
                filename = multy_video_convert(request.FILES.items(), request.POST['format'])
                out_format = "zip"
            fs = FileSystemStorage()
            file = open(f"{fs.base_location}\\{filename}", "rb")
            response = HttpResponse()
            response.write(file.read())
            response['Content-Type'] = format_contenttypes[out_format]
            response['Content-Length'] = os.path.getsize(f"{fs.base_location}\\{filename}")
            response['Content-Disposition'] = f"attachment;filename*=UTF-8''{translit(filename, language_code='ru', reversed=True)}"
            #  fs.delete(filename)
        except IOError:
            response = HttpResponseNotFound("Неизвестная ошибка")
        return response
    return HttpResponseNotFound("Неизвестная ошибка")


def single_video_convert(file, format):
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    new_filename = videofile_convert(filename, format, fs.base_location)
    if new_filename != filename:
        fs.delete(filename)
    return new_filename


def multy_video_convert(files, format):
    fs = FileSystemStorage()
    zip_name = str(uuid4())
    zipfile = ZipFile(f"{fs.base_location}\\{zip_name}.zip", "w")
    for key, file in files:
        new_filename = single_video_convert(file, format)
        zipfile.write(f"{fs.base_location}\\{new_filename}", arcname=new_filename)
        fs.delete(new_filename)
    return f"{zip_name}.zip"


def videofile_convert(filename, format, path):
    name = filename.rsplit(".", 1)[0]
    new_filename = f"{name}.{format}"
    i = 0
    while os.path.isfile(f"{path}\\{new_filename}"):
        i += 1
        new_filename = f"{name}_{i}.{format}"
    if new_filename == filename:
        return new_filename
    ff = ffmpy.FFmpeg(
        inputs={f"{path}\\{filename}": None},
        outputs={f"{path}\\{new_filename}": video_format_convert_params[format]}
    )
    ff.run()
    return new_filename


def is_valid_video_request(request: HttpRequest):
    is_valid_format = False
    for format in video_formats:
        if format == request.POST["format"]:
            is_valid_format = True
            break

    for _, file in request.FILES.items():
        is_valid_file = False
        for format in video_formats:
            if format == os.path.splitext(file.name)[1][1:]:
                is_valid_file = True
                break
        if not is_valid_file:
            return False

    return is_valid_format and len(request.FILES) != 0
