from django.shortcuts import render, redirect
import requests
import pytesseract
from PIL import Image
from django.core.files.storage import FileSystemStorage
import hashlib
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings  
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
import os
import yt_dlp
import datetime
import pytz
import pycountry 
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
import  random 
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from PIL import Image
from reportlab.pdfgen import canvas
import os
import io
from django.http import FileResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from .models import User  # Assuming you have a User model for MongoDB
from pymongo import MongoClient
import json
import datetime






def index(request):
    return render(request, 'Apps/index.html')

def dashboard(request):
    return render(request, 'Apps/dashboard.html')


from pymongo import MongoClient

client = MongoClient("mongodb+srv://rmariatai57:CEowYbCGnISoDCFw@cluster0.upaqeve.mongodb.net/")
db = client['webofwonders']  
user_collection = db['user'] 
otp_collection = db['OTP']   







# client = MongoClient('localhost', 27017) 
# db = client['webofwonders']
# user_collection = db['User']  
# otp_collection = db['OTP']   

otp_storage = {}  

# Register function
def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email exists
        existing_user = user_collection.find_one({"email": email})
        if existing_user:
            messages.error(request, "This email is already registered.")
            return render(request, 'Apps/register.html')

        # Generate OTP
        otp = random.randint(100000, 999999)
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=10)  # 10-minute validity

        # Store OTP in the database
        otp_collection.insert_one({
            'email': email,
            'otp': str(otp),
            'expires_at': expires_at,
            'created_at': datetime.datetime.now(),
            'is_used': False
        })

        # Prepare email content
        email_subject = "WebOfWonders - OTP Verification"
        email_body = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
                <h2 style="text-align: center; color: #007bff;">WebOfWonders OTP Verification</h2>
                <p>Dear User,</p>
                <p>Thank you for registering with us. Please use the following OTP to verify your email address:</p>
                <h3 style="text-align: center; color: #007bff; font-size: 28px;">{otp}</h3>
                <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                <p>Regards,</p>
                <p>WebOfWonders Team</p>
            </div>
            <p style="color:'blue';">&copy; WebOfWonders 2025</p>
        </body>
        </html>
        """

        try:
            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = "html"
            email_message.send(fail_silently=False)
        except Exception as e:
            messages.error(request, f"Failed to send OTP. Error: {str(e)}")
            return render(request, 'Apps/register.html')

        request.session['email'] = email
        request.session['password'] = password

        return redirect('/otp/')                             

    return render(request, 'Apps/register.html')

def otp_verify(request):
    if request.method == "POST":
        email = request.session.get('email')
        password = request.session.get('password')
        entered_otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '') +
            request.POST.get('otp5', '') +
            request.POST.get('otp6', '')
        )

        if email and entered_otp:
            otp_entry = otp_collection.find_one({"email": email, "is_used": False})

            if not otp_entry:
                messages.error(request, "OTP not found or already used.")
                return redirect('/register/')

            if datetime.datetime.now() > otp_entry['expires_at']:
                messages.error(request, "OTP has expired. Please register again.")
                return redirect('/register/')

            if otp_entry['otp'] == entered_otp:
                hashed_password = make_password(password)

                user_collection.insert_one({
                    'email': email,
                    'password': hashed_password,
                    'auth_provider': 'local',
                    'is_verified': True,
                    'date_joined': datetime.datetime.now(),
                    'last_login': datetime.datetime.now(),
                })

                otp_collection.update_one(
                    {"_id": otp_entry['_id']},
                    {"$set": {"is_used": True}}
                )

                messages.success(request, "Registration successful!")
                return redirect('/sucess/')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'Apps/otp.html')

        else:
            messages.error(request, "Session expired or invalid data. Please register again.")
            return redirect('/register/')

    return render(request, 'Apps/otp.html')



def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("email", None)  

        if email:
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp  

            email_subject = "WebOfWonders - Your OTP Code"
            email_body = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
                    <h2 style="text-align: center; color: #007bff;">WebOfWonders OTP Verification</h2>
                    <p>Dear User,</p>
                    <p>We have generated a new OTP for you. Please use the following OTP to verify your email address:</p>
                    <h3 style="text-align: center; color: #007bff; font-size: 28px;">{otp}</h3>
                    <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p>Regards,</p>
                    <p>WebOfWonders Team</p>
                </div>
                <p style="color:'blue';">&copy; webofwonders 2025</p>
            </body>
            </html>
            """

            try:
                email_message = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email],
                )
                email_message.content_subtype = "html" 
                email_message.send(fail_silently=False)
                messages.success(request, "A new OTP has been sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to resend OTP. Error: {str(e)}")
        else:
            messages.error(request, "No email associated with this session.")

    return redirect('/otp/')  


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        client = MongoClient("mongodb+srv://rmariatai57:CEowYbCGnISoDCFw@cluster0.upaqeve.mongodb.net/")

        # client = MongoClient('localhost', 27017)
        db = client['webofwonders']
        user_collection = db['User']

        user = user_collection.find_one({'email': email})

        if user:
            if check_password(password, user['password']):
                request.session['user'] = email
                messages.success(request, "Login successful!")
                return redirect('/dashboard/')
            else:
                messages.error(request, "Invalid password.")
        else:
            messages.error(request, "No account found with this email.")

    return render(request, 'Apps/login.html')


#sucess

def sucess(request):
    return render(request, 'Apps/sucess.html')


def weather(request):
    if request.method == "POST":
        city = request.POST['city']
        api_key = 'cb92c2105916474a94d60338242112' 
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no'

        response = requests.get(url)
        data = response.json()

        if 'error' not in data:  
            weather_data = {
                'temperature': data['current']['temp_c'],  
                'pressure': data['current']['pressure_mb'], 
                'humidity': data['current']['humidity'],
                'description': data['current']['condition']['text'],
                'city': city
            }
            return render(request, 'Apps/weather.html', {'weather_data': weather_data})
        else:
            error_message = "City not found or invalid API key."
            return render(request, 'Apps/weather.html', {'error_message': error_message})

    return render(request, 'Apps/weather.html')


#ocr
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  

def ocr(request):
    extracted_text = ''

    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        img = Image.open(fs.path(filename))
        extracted_text = pytesseract.image_to_string(img)

        return render(request, 'Apps/ocr.html', {'file_url': file_url, 'extracted_text': extracted_text})

    return render(request, 'Apps/ocr.html')

dynamic_storage = {}


#md5

def md5(request):
    hash_value = None
    original_string = None

    if request.method == "POST":
        if "generate_hash" in request.POST:
            text = request.POST.get("text")
            if text:
                hash_value = hashlib.md5(text.encode()).hexdigest()
                dynamic_storage[hash_value] = text
        
        elif "get_original" in request.POST:
            md5_hash = request.POST.get("md5")
            if md5_hash:
                original_string = dynamic_storage.get(md5_hash, "Original string not found")

    return render(request, 'Apps/md5.html', {
        'hash_value': hash_value,
        'original_string': original_string,
    })



#nearby finder

def nearby(request):
    if request.method == "POST":
        city = request.POST.get('city')
        place = request.POST.get('place')

        if not city or not place:
            return render(request, 'Apps/nearby.html', {'error_message': 'City and Place fields are required.'})

        url = f"https://nominatim.openstreetmap.org/search?format=json&q={place}+in+{city}&limit=20"

        headers = {
            "User-Agent": "NearbyApp/1.0 (ramakrishnant684@gmail.com)"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            data = response.json()

            if not data:
                return render(request, 'Apps/nearby.html', {'error_message': 'No nearby places found.'})

            places = []
            for place_data in data:
                full_name = place_data['display_name']
                
                name = full_name.split(',')[0]

                address = full_name

                lat = place_data['lat']
                lon = place_data['lon']

                google_map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                places.append({
                    "name": name,
                    "address": address,
                    "google_map_link": google_map_link
                })

            if not places:
                return render(request, 'Apps/nearby.html', {'error_message': f'No places found for "{place}" in {city}.'})

            return render(request, 'Apps/nearby.html', {'places': places, 'place': place, 'city': city})

        except requests.exceptions.RequestException as e:
            return render(request, 'Apps/nearby.html', {'error_message': f"Error fetching data from the API: {e}"})

    return render(request, 'Apps/nearby.html')


url_mapping = {}



def shorten_url(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        custom_name = request.POST.get('custom_name')

        if original_url:
            short_code = custom_name if custom_name else get_random_string(length=6)

            if short_code in url_mapping:
                return render(request, 'Apps/shortener.html', {'error': 'This name is already taken!'})

            url_mapping[short_code] = original_url

            short_url = f"{request.scheme}://{request.get_host()}/{short_code}"

            return render(request, 'Apps/shortener.html', {'short_url': short_url})

    return render(request, 'Apps/shortener.html')

def redirect_url(request, short_code):
    original_url = url_mapping.get(short_code)

    if original_url:
        return HttpResponseRedirect(original_url)
    else:
        return render(request, 'Apps/shortener.html', {'error': 'Invalid short URL'})


import os
import re
import yt_dlp
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Helper function to sanitize the file name (removes illegal characters)
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')

        if not video_url:
            return HttpResponse("Please provide a valid video URL.", status=400)

        try:
            # Specify the Downloads folder path
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

            if not os.path.exists(downloads_folder):
                os.makedirs(downloads_folder)

            # Define options for yt-dlp
            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
                'outtmpl': os.path.join(downloads_folder, '%(title).80s.%(ext)s'),  # Sanitize title length
                'format': 'bestaudio/bestvideo',  # Best video and best audio, combined
                'merge_output_format': 'mp4',  # Ensure the output is mp4
            }

            # Use yt-dlp to get video info and download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info, including available formats
                info_dict = ydl.extract_info(video_url, download=False)

                # Get the available formats
                formats = info_dict.get('formats', [])
                
                # Choose the best format: Combine best video + best audio
                best_format = None
                for fmt in formats:
                    if fmt['vcodec'] != 'none' and fmt['acodec'] != 'none':
                        best_format = fmt
                        break  # Select first valid combination

                if best_format is None:
                    best_format = max(formats, key=lambda x: x['height'] if 'height' in x else 0)

                # Download the selected format
                ydl_opts['format'] = best_format['format_id']  # Set the selected format

                # Proceed with the download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_title = sanitize_filename(info_dict.get('title', 'video'))
                    video_duration = info_dict.get('duration', 0)
                    video_description = info_dict.get('description', 'No description available.')

                    # Modify file name to be the first half of the title + 'WoW.mp4'
                    half_title = video_title[:len(video_title) // 2]
                    file_name = f"{half_title}WoW.mp4"

                    # Determine file path
                    downloaded_file_path = os.path.join(downloads_folder, file_name)

            # Format duration into minutes and seconds
            duration_minutes = video_duration // 60
            duration_seconds = video_duration % 60

            # Pass data to success page
            redirect_url = f'/download_success/?file_name={file_name}&video_title={video_title}&video_duration={duration_minutes} minutes {duration_seconds} seconds&video_description={video_description}&downloaded_file_path={downloaded_file_path}'
            return redirect(redirect_url)

        except Exception as e:
            # If any error occurs during download
            return HttpResponse(f"Error downloading video: {str(e)}", status=500)

    return render(request, 'Apps/download_video.html')



def download_success(request):
    file_name = request.GET.get('file_name')
    video_title = request.GET.get('video_title')
    video_duration = request.GET.get('video_duration')
    video_description = request.GET.get('video_description')
    downloaded_file_path = request.GET.get('downloaded_file_path')

    return render(request, 'Apps/downloadsucess.html', {
        'file_name': file_name,
        'video_title': video_title,
        'video_duration': video_duration,
        'video_description': video_description,
        'downloaded_file_path': downloaded_file_path
    })

#stopwatch and international timing

def timing(request):
    return render(request, 'Apps/base.html')

def stopwatch(request):
    return render(request, 'Apps/stopwatch.html')

def timer(request):
    return render(request,'Apps/timer.html')




def get_country_iso(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_2
    except LookupError:
        return None

def international_time(request):
    if request.method == 'POST':
        country_name = request.POST.get('country_name', '').strip()

        iso_code = get_country_iso(country_name)

        if not iso_code:
            return HttpResponse(f"Error: Invalid country name '{country_name}'", status=400)

        try:
            timezone = pytz.country_timezones.get(iso_code)
            if not timezone:
                raise ValueError("No timezone found for the country")

            current_time = datetime.datetime.now(pytz.timezone(timezone[0]))

            digital_time = current_time.strftime('%H:%M:%S')
            analog_time = current_time.strftime('%I:%M:%S %p')
            country_time = current_time.strftime('%H:%M:%S')  
            return render(request, 'Apps/international_time.html', {
                'country_name': country_name.upper(),
                'digital_time': digital_time,
                'analog_time': analog_time,
                'country_time': country_time,  
                'timezone': timezone[0] 
            })
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=400)

    return render(request, 'Apps/international_time_form.html')




def generate_pdf(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Default Title')
        content = request.POST.get('content', 'Default Content')
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, height - 100, title)
        
        p.setFont("Helvetica", 12)
        text_object = p.beginText(100, height - 150)
        text_object.setTextOrigin(100, height - 150)
        text_object.setFont("Helvetica", 12)
        
        for line in content.split('\n'):
            text_object.textLine(line)
        
        p.drawText(text_object)
        p.showPage()
        p.save()
        buffer.seek(0)
        
        response = FileResponse(buffer, as_attachment=True, filename="custom_slide.pdf")
        response['Content-Disposition'] = 'attachment; filename="custom_slide.pdf"'
        return response
    
    return render(request, 'Apps/pdf_form.html')



def upload_file(request):
    if request.method == 'POST' and request.FILES.getlist('file'):
        uploaded_files = request.FILES.getlist('file')
        fs = FileSystemStorage()
        image_paths = []
        
        for uploaded_file in uploaded_files:
            filename = fs.save(uploaded_file.name, uploaded_file)
            image_paths.append(fs.path(filename))
        
        response = convert_images_to_pdf(image_paths)
        
        for path in image_paths:
            os.remove(path) 
        
        return response
    return render(request, 'Apps/pdf.html')



def convert_images_to_pdf(image_paths):
    pdf_path = image_paths[0] + ".pdf"
    standard_width, standard_height = 1000, 600  
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=(standard_width, standard_height))
    
    for image_path in image_paths:
        image = Image.open(image_path)
        image = image.convert('RGB') 
        image = image.resize((standard_width, standard_height)) 
        temp_image_path = image_path + "_resized.jpg"
        image.save(temp_image_path, format='JPEG')
        pdf_canvas.drawImage(temp_image_path, 0, 0, standard_width, standard_height)
        pdf_canvas.showPage()
        os.remove(temp_image_path)  
    
    pdf_canvas.save()
    
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="WoWMaker.pdf"'
    
    os.remove(pdf_path) 
    return response





#janani Space ####
#mp3tomp4



# def music(request):
#     """
#     Render the initial form for MP4 to MP3 conversion.
#     """
#     return render(request, 'Apps/mp4tomp3.html')

# def convert(request):
#     """
#     Handle MP4 to MP3 file conversion.
#     """
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('mp4_file')  # Get the uploaded MP4 file

#         if uploaded_file:
#             # Save the uploaded MP4 file to the media directory
#             input_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
#             with open(input_path, 'wb') as f:
#                 for chunk in uploaded_file.chunks():
#                     f.write(chunk)

#             # Define the output MP3 file path
#             output_filename = f"{os.path.splitext(uploaded_file.name)[0]}  _WOW.mp3"
#             output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

#             try:
#                 # Convert MP4 to MP3 using pydub
#                 audio = AudioSegment.from_file(input_path, format="mp4")
#                 audio.export(output_path, format="mp3")
#             except Exception as e:
#                 # Handle errors during conversion
#                 return HttpResponse(f"Error during conversion: {e}", status=500)

#             # Serve the MP3 file as a downloadable response
#             with open(output_path, 'rb') as mp3_file:
#                 response = HttpResponse(mp3_file.read(), content_type='audio/mpeg')
#                 response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
#                 return response

#         else:
#             # Handle case when no file is uploaded
#             return HttpResponse("No file was uploaded.", status=400)

#     # Render the form if the request method is not POST
#     return render(request, 'Apps/mp4tomp3.html')
    
# tick tac 
def tick_tac(request):
   return render(request, 'Apps/ticktac.html')

#puzzle 
import random
from django.shortcuts import render

def puzzle_game_view(request):
    grid_size = 3
    piece_width = 100
    piece_height = 100

    # Define available images
    images = [
        '/static/images/logo.png',
        '/static/images/chotta.jpg',
        '/static/images/doreman.jpg',


        
    ]
    selected_image = random.choice(images)

    # Create puzzle pieces
    pieces = list(range(grid_size * grid_size))
    random.shuffle(pieces)

    piece_positions = []
    for piece in pieces:
        if piece == 0:
            piece_positions.append(None)  # Empty space
        else:
            x = (piece % grid_size) * piece_width
            y = (piece // grid_size) * piece_height
            piece_positions.append(f"-{x}px -{y}px")

    # Combine pieces and positions
    puzzle_pieces = list(zip(pieces, piece_positions))

    context = {
        'grid_size': grid_size,
        'puzzle_pieces': puzzle_pieces,
        'piece_width': piece_width,
        'piece_height': piece_height,
        'image_url': selected_image,
    }
    return render(request, 'Apps/puzzle_game.html', context)

# brain reaction
def brain_game_view(request):
    return render(request, 'Apps/brain.html')

#guess the number
from django.template.loader import get_template
from django.http import HttpResponse

def guess_number(request):
    try:
        template = get_template('Apps/number.html')  # Try to load the template
        return render(request, 'Apps/number.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {e}")

#sudoko game
def generate_sudoku():
    import random
    base = 3
    side = base * base

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    rows = [g * base + r for g in shuffle(range(base)) for r in shuffle(range(base))]
    cols = [g * base + c for g in shuffle(range(base)) for c in shuffle(range(base))]
    nums = shuffle(range(1, base * base + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    # Remove some numbers to make the puzzle
    puzzle = [[board[r][c] if random.random() > 0.5 else 0 for c in range(side)] for r in range(side)]
    return puzzle, board

def sudoku_view(request):
    if request.method == "POST":
        # Handle submission (not implemented yet)
        pass
    else:
        puzzle, solution = generate_sudoku()
        return render(request, 'Apps/sudoko.html', {'puzzle': puzzle, 'solution': solution})

#dictionary 
import requests
from django.shortcuts import render

def home(request):
    meaning = None
    error = None
    word = None

    if request.method == "POST":
        word = request.POST.get("word")
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            meaning = data[0]  # Extract the first result
        elif response.status_code == 404:
            error = f"No results found for '{word}'."
        else:
            error = f"Error: {response.status_code} - {response.reason}"

    return render(request, "Apps/dictionary.html", {"meaning": meaning, "error": error, "word": word})
    
#password generator
import random
import string
from django.shortcuts import render

def generate_password(request):
    length = int(request.GET.get("length", 12))  # Default length is 12
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(length))
    
    return render(request, "Apps/password.html", {"password": password})

#color picker
from django.http import JsonResponse
from django.shortcuts import render

def color_picker(request):
    if request.method == "POST":
        selected_color = request.POST.get("color", "#000000")
        return JsonResponse({"color": selected_color})

    return render(request, "Apps/color_picker.html")

#qr generator
import qrcode
from django.shortcuts import render
from django import forms
from io import BytesIO
import base64

# Form for user input
class QRForm(forms.Form):
    data = forms.CharField(label='Enter Data', max_length=100)

def generate_qr(request):
    qr_code_img = None

    if request.method == "POST":
        form = QRForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']  # Get the user input

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Create the image from the QR code
            img = qr.make_image(fill='black', back_color='white')

            # Save the image to an in-memory file (BytesIO)
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)

            # Base64 encode the image
            img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

            # Return the base64 string to the template
            qr_code_img = img_base64

        else:
            qr_code_img = None
    else:
        form = QRForm()

    return render(request, 'Apps/qrgenerator.html', {'form': form, 'qr_code_img': qr_code_img})

