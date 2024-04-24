from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re
from django.conf import settings
import os
import assemblyai as aai
from .utils import generate
from .models import BlogPost

#Suprusrpw: user4321

def yt_title(link):
	yt = YouTube(link)
	title = yt.title
	return title


# def download_audio(link):
# 	yt = YouTube(link)
# 	video = yt.streams.filter(only_audio=True).first()
# 	out_file = video.download(output_path=settings.MEDIA_ROOT)
# 	base, ext = os.path.splitext(out_file)
# 	new_file = base + '.mp3'
# 	os.rename(out_file, new_file)
# 	return new_file

# def get_transcription(link):
# 	audio_file = download_audio(link)
# 	aai.settings.api_key = "1e1669e6ac4240329338aa1af7bac90e"

# 	transcriber = aai.Transcriber()
# 	transcript = transcriber.transcribe(audio_file)

	# return transcript.text

def get_video_id(link):
    regex = r"(?:v=|youtu\.be/)([\w\-_]+)"
    match = re.search(regex, link)
    return match.group(1) if match else None

def get_transcript(video_id):
	try:
		transcript = YouTubeTranscriptApi.get_transcript(video_id)
		if transcript:
			# Initialize an empty list to store transcript text
			transcript_text = []

			# Loop through each line of the transcript
			for line in transcript:
				# Extract the text from each line
				text = line['text']
				transcript_text.append(text)

			# Return the list containing all transcript text lines
			return transcript_text

	except Exception as e:
		print(f"Error fetching transcript: {e}")
		return None

@login_required
def index(request):
	return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			yt_link = data['link']
		except (KeyError, json.JSONDecodeError):
			return JsonResponse({'error': 'Invalid data sent'}, status=400)
		
		#Get Youtbe title
		title = yt_title(yt_link)

		#Get Video id
		video_id = get_video_id(yt_link)

		#Get Transcript
		transcript = get_transcript(video_id)
		if not transcript:
			return JsonResponse({'error': "Failed to get transcrpt"}, status = 500)
		

		#Write a function to delete audio
		#Write a function to generate image for blog post
		#Word by word generation into output

		#Use Open AI to generate the blog
		blog_content = generate(transcript)
		if not blog_content:
			return JsonResponse({'error': "Failed to generate blog article"}, status=500)

		#Save blog aritcle to database
		new_blog_article = BlogPost.objects.create(
			user=request.user,
			youtube_title= title,
			youtube_link=yt_link,
			generated_content=blog_content
		)
		new_blog_article.save()

		#Return blog article as response
		return JsonResponse({'content': blog_content})


	else:
		return JsonResponse({'error': 'Invalid request'}, status=405)


def blog_list(request):
	blog_articles = BlogPost.objects.filter(user=request.user)
	return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
	blog_article_detail = BlogPost.objects.get(id=pk)
	if request.user == blog_article_detail.user:
		return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
	else:
		return redirect('/')


def user_login(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect ('/')
		else:
			error_message = "Invalid username or password"
			return render(request, 'login.html', {'error_message': error_message})

	return render(request, 'login.html')


def user_signup(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		repeatPassword = request.POST['repeatPassword']

		if password == repeatPassword:
			try:
				user = User.objects.create_user(username, email, password)
				user.save()
				login(request, user)
				return redirect('/')
			except:
				error_message = 'Error creating account'#Try to create detailed error message
				return render(request, 'signup.html', {'error_message': error_message})
		else:
			error_message = 'Passwords do not match'
			return render(request, 'signup.html', {'error_message': error_message})

	return render(request, 'signup.html')


def user_logout(request):
	logout(request)
	return redirect('/')