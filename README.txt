source /home/tehseen/Documents/FaceRecogProj/envproj/bin/activate


python manage.py makemigrations members
the above command will create a file in migrations folder under members
members/migrations/xxxx_initial.py
where xxxx are digits

python manage.py sqlmigrate members xxxx

python manage.py migrate
python manage.py runserver


https://askubuntu.com/questions/4875/how-can-i-use-my-webcam-with-ubuntu-running-in-virtualbox


def adRegister(request):
    if request.method=="POST":   
        username = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        gender = request.POST['gender']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password1)
                applicants = Applicant.objects.create(user=user, phone=phone, gender=gender, type="admin")

                user.save()
                applicants.save()

                messages.success(request, "Your account has been successfully created.")
                return redirect('login')
        else:
            messages.info(request, 'Both passwords are not matching')
            return redirect('register')
            
            
            

def register(request):
    if request.method=="POST":   
        print(request)
        username = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        department = request.POST['department']
        semester = request.POST['semester']
        gender = request.POST['gender']
        class_name = request.POST['class_name']
        roll_no = request.POST['roll_no']
        image = request.FILES['image']
        video = request.FILES['video']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register.html')  # Note: this should be a named url pattern, not "register.html"
        
        if image is not None or video is not None:
          user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password1)
          applicants = Applicant.objects.create(user=user, department=department, semester=semester, class_name=class_name, roll_no=roll_no, phone=phone, gender=gender, image=image, video=video, type="applicant")
          
          user.save()
          applicants.save()
        else:
          messages.error(request, "must provide image and/or video.")
          return redirect('register.html')  # Note: this should be a named url pattern, not "register.html"
                
        print(image)
        print(video)        
        
        name_id = first_name + "_" + last_name
        if image is not None:
          encode_new_known_face_image(image, name_id)
        
        if video is not None:
          encode_new_known_face_video("db_facerecog/training_video/"+video.name, name_id)
        
        messages.success(request, "Your account has been successfully created.")
        return render(request, "adminstrator.html")

    return render(request, "register.html")
    
    
    
    
    
    
    
    
    
    
      <header class="header_four">
        <!-- Preloader -->
        <div id="preloader">
            <div id="status">&nbsp;</div>
        </div>
        <div class="header_top">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 col-sm-12 col-lg-12">
                        <div class="info_wrapper">
                            <div class="contact_info">
                                <ul class="list-unstyled">
                                    <li><i class="flaticon-phone-receiver"></i>+000-2356-222</li>
                                    <li><i class="flaticon-mail-black-envelope-symbol"></i>contact@yourdomain.com</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="edu_nav">
            <div class="container">
                <nav class="navbar navbar-expand-md navbar-light bg-faded col-md-12 col-sm-12 col-lg-12>">
                    <a class="navbar-brand" href="{% url 'members:index'%}"><img src="{% static 'images/logo.png' %}"
                            alt="logo"></a>
                    <div class="collapse navbar-collapse main-menu" id="navbarSupportedContent">
                        <ul class="navbar-nav nav lavalamp ml-auto menu">
                            <li class="nav-item"><a href="{% url 'members:index'%}" class="nav-link active">Home</a>
                            </li>
                            <li class="nav-item"><a href="{% url 'members:about'%}" class="nav-link">About</a></li>
                            <li class="nav-item"><a href="{% url 'members:course'%}" class="nav-link">Courses</a>
                            </li>
                            <li class="nav-item"><a href="{% url 'members:blog'%}" class="nav-link">Blog</a>
                            </li>
                            <li class="nav-item"><a href="{% url 'members:dashboard'%}" class="nav-link">Dashboard</a>
                            </li>
                            <li class="nav-item"><a href="#" class="nav-link">Pages</a>
                                <ul class="navbar-nav nav mx-auto">
                                    <li class="nav-item"><a href="{% url 'members:event'%}" class="nav-link">Events</a>
                                    </li>
                                    <li class="nav-item"><a href="#" class="nav-link">Scholarship</a>
                                    </li>
                                    <li class="nav-item"><a href="{% url 'members:teacher_profile'%}"
                                            class="nav-link">Teachers Profile</a></li>
                                    <li class="nav-item"><a href="forgot-password/" class="nav-link">Forgot Password</a>
                                    </li>
                                </ul>
                            </li>
                            <li class="nav-item"><a href="{% url 'members:contact'%}" class="nav-link">Contact</a></li>
                        </ul>
                    </div>
                    <div class="mr-auto search_area ">
                        <ul class="navbar-nav mx-auto">
                            <li class="nav-item"><i class="search_btn flaticon-magnifier"></i>
                                <div id="search">
                                    <button type="button" class="close">×</button>
                                    <form>
                                        <input type="search" value="" placeholder="Search here...." required />
                                    </form>
                                </div>
                            </li>
                        </ul>
                    </div>
                </nav><!-- END NAVBAR -->
            </div>
        </div>

    </header> <!--  End header section-->
