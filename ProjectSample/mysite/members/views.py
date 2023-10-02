import cv2
import shutil
from PIL import Image, ImageDraw
from collections import Counter
import pickle
import face_recognition
from pathlib import Path
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Applicant
from django.contrib.auth import authenticate, login
from django.contrib.auth import login


from django.shortcuts import render, redirect, reverse
from django.core.files.uploadedfile import TemporaryUploadedFile
from members.models import Markpresence
from members import views
from django.contrib.auth.models import User, Group

from urllib.request import urlopen
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *


from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login as auth_login
import base64

import sqlite3


from .models import Student, Attendance
import datetime
import face_recognition
import os
from datetime import datetime


# Create your models here.
User = get_user_model()


_DTEC_FRAME_COUNT_LIM__ENCOD_VIDEO = 32
_DTEC_FRAME_COUNT_LIM__DECOD_VIDEO = 32

_BOUNDING_BOX_COLOR = "blue"
_TEXT_COLOR = "white"

DTEC_ALG_CHOICES = ["hog", "cnn"]
_DTEC_ALG_DEFAULT = DTEC_ALG_CHOICES[0]
_DETEC_ALG = DTEC_ALG_CHOICES[0]

DEFAULT_ENCODINGS_PATH = Path("db_facerecog/output/encodings.pkl")
Path("db_facerecog").mkdir(exist_ok=True)
Path("db_facerecog/training").mkdir(exist_ok=True)
Path("db_facerecog/training_video").mkdir(exist_ok=True)
Path("db_facerecog/output").mkdir(exist_ok=True)
Path("db_facerecog/validation").mkdir(exist_ok=True)
Path("db_facerecog/validation_video").mkdir(exist_ok=True)


def _path_object_to_str(obj):
    print(type(obj))
    print(obj.name)
    print(type(obj.name))

    return "db_facerecog/training_video/" + obj.name

    if isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, TemporaryUploadedFile):
        return obj.name
    else:
        return obj


def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding)

    votes = Counter(name for match, name in zip(
        boolean_matches, loaded_encodings["names"]) if match)
    if votes:
        return votes.most_common(1)[0][0]


def _display_face(draw, bounding_box, name):

    top, right, bottom, left = bounding_box

    draw.rectangle(((left, top), (right, bottom)), outline=_BOUNDING_BOX_COLOR)

    text_left, text_top, text_right, text_bottom = draw.textbbox(
        (left, bottom), name)

    draw.rectangle(((text_left, text_top), (text_right,
                   text_bottom)), fill="blue", outline="blue")

    draw.text((text_left, text_top), name, fill="white")


def encode_new_known_face_image(image_file, name, model: str = _DTEC_ALG_DEFAULT, encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:
    loaded_encodings = None

    if encodings_location.is_file():
        with encodings_location.open(mode="rb") as f:
            loaded_encodings = pickle.load(f)
    else:
        loaded_encodings = {"names": [], "encodings": []}

    image = face_recognition.load_image_file(image_file)

    face_locations = face_recognition.face_locations(image, model=model)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    for encoding in face_encodings:
        loaded_encodings["names"].append(name)
        loaded_encodings["encodings"].append(encoding)
        print(name)
        print(len(encoding))

    with encodings_location.open(mode="wb") as f:
        pickle.dump(loaded_encodings, f)
        print('encoding saved to file\n')


def encode_new_known_face_video(video_file, name, model: str = _DTEC_ALG_DEFAULT, encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:
    # open video
    video_capture = cv2.VideoCapture(video_file)
    # Check if camera opened successfully
    if (video_capture.isOpened() == False):
        print("Error opening video  file")

    if encodings_location.is_file():
        with encodings_location.open(mode="rb") as f:
            loaded_encodings = pickle.load(f)
    else:
        loaded_encodings = {"names": [], "encodings": []}

    fr_count = 0
    # Read until video is completed
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if ret == True:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(
                image, model=model)
            face_encodings = face_recognition.face_encodings(
                image, face_locations)

            for encoding in face_encodings:
                loaded_encodings["names"].append(name)
                loaded_encodings["encodings"].append(encoding)
                print(name)
                print(len(encoding))

            if (len(face_encodings) > 0):
                fr_count = fr_count + 1
                if fr_count > _DTEC_FRAME_COUNT_LIM__ENCOD_VIDEO:
                    break
        else:
            break

    video_capture.release()

    with encodings_location.open(mode="wb") as f:
        pickle.dump(loaded_encodings, f)
        print('encoding saved to file\n')


def encode_student_face(image_file, video_file, student_id, model: str = _DTEC_ALG_DEFAULT, encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:

    encode_new_known_face_image(image_file, student_id, model=_DETEC_ALG)
    encode_new_known_face_video(video_file, student_id, model=_DETEC_ALG)


def recognize_faces_image(image_location: str, model: str = _DTEC_ALG_DEFAULT,
                          encodings_location: Path = DEFAULT_ENCODINGS_PATH):

    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)

    input_face_locations = face_recognition.face_locations(
        input_image, model=model)
    input_face_encodings = face_recognition.face_encodings(
        input_image, input_face_locations)

    pillow_image = Image.fromarray(input_image)
    draw = ImageDraw.Draw(pillow_image)

    name_found = []
    for bounding_box, unknown_encoding in zip(input_face_locations, input_face_encodings):
        name = _recognize_face(unknown_encoding, loaded_encodings)
        if not name:
            name = "Unknown"
        else:
            name_found.append(name)

        print(name, bounding_box)

    return name_found


def recognize_faces_video(video_file, model: str = _DTEC_ALG_DEFAULT,
                          encodings_location: Path = DEFAULT_ENCODINGS_PATH):

    print('recognize_faces_video: start')

    # open video
    video_capture = cv2.VideoCapture(video_file)
    # Check if camera opened successfully
    if (video_capture.isOpened() == False):
        print("Error opening video  file, " + video_file)

    name_found = []
    fr_count = 0

    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    # Read until video is completed
    while video_capture.isOpened():
        ret, frame = video_capture.read()

        if ret == True:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(
                image, model=model)
            face_encodings = face_recognition.face_encodings(
                image, face_locations)

            for unknown_encoding in face_encodings:
                name = _recognize_face(unknown_encoding, loaded_encodings)
                if not name:
                    name = "Unknown"
                else:
                    name_found.append(name)

                print(name)

            if (len(face_encodings) > 0):
                fr_count = fr_count + 1
                if fr_count > _DTEC_FRAME_COUNT_LIM__DECOD_VIDEO:
                    break
        else:
            break

    print('recognize_faces_video: end')
    return name_found


def members(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())


def first(request):
    template = loader.get_template('first.html')
    return HttpResponse(template.render())


"""
def login(request):
  template = loader.get_template('login.html')
  return HttpResponse(template.render())
"""


#def register(request):
  #  template = loader.get_template('register.html')
   # return HttpResponse(template.render())


def adminstrator(request):
    tid = request.GET.get('tid', None)
    if tid != None:
        try:
            user = User.objects.get(id=tid)
            user.delete()
            messages.success(request, "Teacher Delete Successfully")
            # Handle successful deletion (e.g., show a success message or redirect)
        except User.DoesNotExist:
            messages.error(request, "Something went wrong")
            pass
        return redirect('/members/adminstrator')
    else:
      teacher_group = Group.objects.get(name='teacher')
      # Get all users in the 'teacher' group
      teachersx = User.objects.filter(groups__in=[teacher_group])
      # Pass the context data directly to the render() function
      return render(request, 'adminstrator.html', {'teachers': teachersx})


def student(request):
    template = loader.get_template('student.html')
    return HttpResponse(template.render())


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())


def about(request):
    template = loader.get_template('about.html')
    return HttpResponse(template.render())


def dashboard(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render())


def course(request):
    template = loader.get_template('course.html')
    return HttpResponse(template.render())


def contact(request):
    template = loader.get_template('contact.html')
    return HttpResponse(template.render())


def blog(request):
    template = loader.get_template('blog.html')
    return HttpResponse(template.render())


def blog_2(request):
    template = loader.get_template('blog-2.html')
    return HttpResponse(template.render())





def event(request):
    template = loader.get_template('event.html')
    return HttpResponse(template.render())


def adRegister(request):
    template = loader.get_template('adRegister.html')
    return HttpResponse(template.render())


def get_teachers(request):
    # Get the 'teacher' group (replace 'Teacher' with your desired group name)
    teacher_group = Group.objects.get(name='Teacher')

    # Get all users in the 'teacher' group
    teachers = User.objects.filter(groups__in=[teacher_group])

    # Now 'teachers' contains all the users in the 'teacher' group
    # You can use this queryset for further processing or pass it to the template

    return render(request, 'teachers.html', {'teachers': teachers})


# def adLogin(request):
#     if request.user.is_authenticated:
#         redirect('members/adminstrator')
#     else:
#         return render(request, "adLogin.html")


def teRegister(request):
    template = loader.get_template('teRegister.html')
    return HttpResponse(template.render())


def teLogin(request):
    template = loader.get_template('teLogin.html')
    return HttpResponse(template.render())

def login_view(request):
    if request.method == 'POST':
        # handle login logic here
        pass
    return render(request, 'login.html')


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Applicant

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Applicant
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Additional Fields
        phone = request.POST['phone']
        gender = request.POST['gender']
        type_ = request.POST['type']
        department = request.POST['department']
        semester = request.POST['semester']
        class_name = request.POST['class_name']
        roll_no = request.POST['roll_no']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return render(request, 'register.html')
        
        # Create a new user and applicant
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password)
        )
        user.save()

        applicant = Applicant(
            user=user,
            phone=phone,
            gender=gender,
            type=type_,
            department=department,
            semester=int(semester),
            class_name=class_name,
            roll_no=roll_no
        )
        applicant.save()

        messages.success(request, 'You have registered successfully!')
        return render(request, 'login.html')

    semesters = range(1, 11)
    context = {
        'semesters': semesters
    }
    return render(request, 'register.html', context)


from django.contrib.auth import authenticate, login as django_login, logout as django_logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            django_login(request, user)
            messages.success(request, 'You have logged in successfully!')
            return render(request, 'recognize.html')  # Redirect to your dashboard or desired page after login
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


def logout_view(request):
    django_logout(request)
    messages.success(request, 'You have logged out successfully!')
    return render(request, 'login.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def adRegister(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "A user with this username already exists.")
            return render(request, "adRegister.html")

        # Check if the two password fields match
        if password1 != password2:
            messages.error(request, "The two password fields do not match.")
            return render(request, "adRegister.html")

        # Create the user
        user = User(username=username, 
                    email=email, 
                    first_name=first_name, 
                    last_name=last_name, 
                    password=make_password(password1))  # Hash the password
        user.save()

        # At this point, the user has been created. 
        # You can log them in and redirect them to the next page
        login(request, user)
        return render(request, 'adminstrator.html')
    else:
        return render(request, 'adRegister.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.models import User

def adLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        userx = authenticate(username=username, password=password)
        print(userx)
        if userx is not None:
            login(request, userx)
            messages.success(
                request, "Your account has been Logged in successfully.")
            return redirect('/adminstrator')
        else:
            messages.error(
                request, "Invalid username or password, please try again.")
            return render(request, 'adLogin.html')
    else:
        if request.user.is_authenticated:
            return redirect('/adminstrator')
        else:
            return render(request, 'adLogin.html')





def teRegister(request):
    if request.method == "POST":
        username = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        department = request.POST['department']
        phone = request.POST['phone']
        gender = request.POST['gender']
        # return render(request, 'template.html', {'ref': ref_value})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            # Note: this should be a named url pattern, not "register.html"
            return redirect('/teRegister')

        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, username=username, password=password1)
        teachers = Teacher.objects.create(
            user=user, department=department, phone=phone, gender=gender, type="admin")

        # Get or create the 'teacher' group (replace 'Teacher' with your desired group name)
        teacher_group, _ = Group.objects.get_or_create(name='teacher')

        # Add the user to the 'teacher' group
        user.groups.add(teacher_group)
        user.save()
        teachers.save()

        messages.success(
            request, "Your account has been successfully created.")
        return render(request, 'adminstrator.html')
    ref_value = request.GET.get('ref', None)
    return render(request, "teRegister.html", {'ref': ref_value})


def teLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        userx = authenticate(username=username, password=password)

        if userx is not None:
            login(request, userx)
            return redirect('/teacher_profile')
        else:
            messages.error(request, "Email & Password is wrong, haha :)")
            return render(request, 'teLogin.html')
    else:
        return render(request, 'teLogin.html')



def teacher_profile(request):
    if request.user.is_authenticated:
        try:
            applicant = Applicant.objects.get(user=request.user)
            print(applicant)
        except Applicant.DoesNotExist:
            applicant = None

        return render(request, 'teacher_profile.html', {'user': request.user, 'applicant': applicant})
    else:
        return redirect('/teLogin')







def markAttendance(request):
    if request.method == "POST":
        img = request.FILES['image']
        vid = request.FILES['video']

        if img is not None or vid is not None:
            mark = Markpresence.objects.create(image=img, video=vid)
            mark.save()
        else:
            messages.error(request, "must provide image and/or video.")
            return render(request, "adminstrator.html")

        if img is not None:
            name_found_img = recognize_faces_image(img)
            counts_name_img = dict(Counter(name_found_img))
            for (name_id, count) in counts_name_img.items():
                id_lst = name_id.split("_")
                student = Student.objects.create(
                    first_name=id_lst[0], last_name=id_lst[1])
                student.save()

        if vid is not None:
            name_found_vid = recognize_faces_video(
                "db_facerecog/validation_video/" + vid.name)
            counts_name_vid = dict(Counter(name_found_vid))
            for (name_id, count) in counts_name_vid.items():
                if count > 5:
                    id_lst = name_id.split("_")
                    student = Student.objects.create(
                        first_name=id_lst[0], last_name=id_lst[1])
                    student.save()

        messages.success(request, "Presence has been successfully marked.")
        return render(request, "adminstrator.html")

    return render(request, "marksAttendance.html")


def camera(request):
    context = dict()  # define context here to be used for GET requests
    if request.method == 'POST':
        webimg = request.POST.get("src")
        if webimg is not None:
            try:
                # split off the "data:image/png;base64," part
                format, imgstr = webimg.split(';base64,')
                # get the file extension (jpeg, png, etc.)
                ext = format.split('/')[-1]

                # decode base64 image
                data = base64.b64decode(imgstr)

                # create a Django ContentFile
                file = ContentFile(data, name='temp.' + ext)
                # create a object of Image type defined in your model
                imgObj = CameraImg.objects.create(image=file)
                imgObj.save()

                name_found_img = recognize_faces_image(imgObj.image.url)
                counts_name_img = dict(Counter(name_found_img))
                for (name_id, count) in counts_name_img.items():
                    id_lst = name_id.split("_")
                    student = Student.objects.create(
                        first_name=id_lst[0], last_name=id_lst[1])
                    student.save()

                # url to image stored in my server/local device
                context["path"] = imgObj.image.url

            except Exception as e:
                print(str(e))  # print the error
        else:
            print("webimg is None")
    return render(request, 'camera.html', context=context)



def some_view(request):
    if request.method == 'GET':
        department = request.GET.get('department', '')
        semester = request.GET.get('semester', '')
        class_name = request.GET.get('class_name', '')
        roll_no = request.GET.get('roll_no', '')

        applicants = Applicant.objects.all()

        if department:
            applicants = applicants.filter(department__icontains=department)
        if semester:
            applicants = applicants.filter(semester=semester)
        if class_name:
            applicants = applicants.filter(class_name__icontains=class_name)
        if roll_no:
            applicants = applicants.filter(roll_no__icontains=roll_no)

    return render(request, 'some_view.html', {'rows': applicants})




def filter_students(request):
   # if request.method == 'POST':
    department = request.get('department')
    semester = request.get('semester')
    class_name = request.get('class_name')
    roll_no = request.get('roll_no')
    print(request.GET)

    applicants = Applicant.objects.all()
    logger.info(f'Initially, found {applicants.count()} applicants.')

    if department:
        applicants = applicants.filter(department=department)

    if semester:
        applicants = applicants.filter(
            semester=int(semester))  # convert semester to int

    if class_name:
        applicants = applicants.filter(class_name=class_name)

    if roll_no:
        applicants = applicants.filter(roll_no=roll_no)

    logger.info(f'After filtering, found {applicants.count()} applicants.')

    return render(request, 'filter_students.html', {'applicants': applicants})

   # return render(request, 'filter_students.html')

import json
import os
import base64
import face_recognition
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from .models import CapturedImage

def capture(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        image_data = data.get('image', '')
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]

        image_file = ContentFile(base64.b64decode(imgstr))

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path_relative = default_storage.save(f'db_facerecog/training_video/webcam_image_{timestamp}.png', image_file)

        file_path_absolute = os.path.join(settings.MEDIA_ROOT, file_path_relative)
        if not os.path.exists(file_path_absolute):
            return JsonResponse({'success': False, 'message': 'File not found: ' + file_path_absolute})

        # Recognize faces in the image
        faces_detected = recognize(file_path_absolute)

        # If no faces are found, delete the image and return an error
        if not faces_detected:
            os.remove(file_path_absolute)
            return JsonResponse({'success': False, 'message': 'No Face found'})

        # Save the image with faces
        captured_image = CapturedImage(image=file_path_relative)
        captured_image.save()

        return JsonResponse({'success': True, 'message': 'You are present'})
    return JsonResponse({'success': False})

def recognize(image_path):
    if not os.path.exists(image_path):
        print("Image not found:", image_path)
        return []

    try:
        with Image.open(image_path) as img:
            image_to_check = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image_to_check)
            return face_locations
    except Exception as e:
        print("Error loading image:", e)
        return []

def recognize_faces_image(request):
    image_dir = 'db_facerecog/training_video/'
    all_attendances = []

    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(image_dir, filename)
            faces_detected = recognize(image_path)
            if faces_detected:
                attendances = Attendance.objects.filter(date=datetime.date.today(), student__first_name__in=[f"face_{idx}" for idx in range(len(faces_detected))])
                all_attendances.extend(attendances)

    return render(request, 'recognize.html', {'attendances': all_attendances})




from django.shortcuts import render
from .models import CapturedImage
from django.utils import timezone
from datetime import datetime  # Make sure to import datetime correctly

def view_images(request):
    date_query = request.GET.get('date', None)
    if date_query:
        date = datetime.strptime(date_query, '%Y-%m-%d')
        start_date = timezone.make_aware(date.replace(hour=0, minute=0, second=0, microsecond=0))
        end_date = timezone.make_aware(date.replace(hour=23, minute=59, second=59, microsecond=999999))
    else:
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    images = CapturedImage.objects.filter(timestamp__range=(start_date, end_date)).order_by('-timestamp')
    for image in images:
        image.timestamp = image.timestamp.strftime('%Y-%m-%d %H:%M:%S') # Format date for display
    return render(request, 'view_images.html', {'images': images, 'date_query': date_query})


