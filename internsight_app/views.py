from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from .models import Profile 
import PyPDF2
import os
import logging
import hashlib
from django.core.cache import cache
import re


logger = logging.getLogger(__name__)

SERPAPI_URL = "https://serpapi.com/search.json"
CACHE_SECONDS=60*60

def fetch_jobs(query):
    """Fetch jobs from SerpAPI. Returns (jobs, error_message)."""
    cache_key = "jobs:" + hashlib.sha256(query.lower().encode()).hexdigest()
    cached_jobs = cache.get(cache_key)
    if cached_jobs is not None:
        return cached_jobs, None
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        logger.error("SERPAPI_KEY is not set")
        return [], "Job search isn't configured yet. Please try again later."

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": api_key,
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=10)
        data = response.json()
    except requests.exceptions.Timeout:
        logger.warning("SerpAPI request timed out")
        return [], "The job search timed out. Please try again."
    except (requests.exceptions.RequestException, ValueError):
        logger.exception("SerpAPI request failed")
        return [], "We couldn't reach the job search service. Please try again later."

    error = data.get("error")
    if error:
        # SerpAPI also uses "error" when a search simply has no results
        if "hasn't returned any results" in error:
            cache.set(cache_key, [], CACHE_SECONDS)
            return [], None
        logger.error("SerpAPI error: %s", error)
        return [], "We couldn't load listings right now. Please try again later."

    jobs = data.get("jobs_results", [])
    cache.set(cache_key, jobs, CACHE_SECONDS)
    return jobs, None

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text.lower()

def contains_skill(text, skill):
    """True if `skill` appears in `text` as a whole word (not inside another word)."""
    pattern = r"(?<![a-z0-9+#.])" + re.escape(skill.lower()) + r"(?![a-z0-9+#])"
    return re.search(pattern, text.lower()) is not None

def extract_skills(text):
    SKILLS_DB = [
    "python", "java", "c", "c++", "sql", "mysql", "postgresql",
    "django", "flask", "html", "css", "javascript", "react",
    "node.js", "machine learning", "deep learning", "data analysis",
    "excel", "power bi", "tableau", "mongodb", "git", "linux",
    "aws", "azure", "nlp"
]

    text = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if contains_skill(text, skill):
            found_skills.append(skill)
    
    return found_skills




# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

def extract_skills_from_text(text):
    skills_list = ["python", "java", "c++", "django", "sql", "html", "css", "javascript"]
    
    found_skills = []
    for skill in skills_list:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills

@login_required
def listings(request):
    API_KEY = os.environ.get("SERPAPI_KEY")
    url = "https://serpapi.com/search.json"

    profile, created = Profile.objects.get_or_create(user=request.user)

    listing_type = request.GET.get("type", "all")

    query = "internships India software"
    skills = []

    if profile.skills:
        skills = [s.strip() for s in profile.skills.split(",") if s.strip()]

    if profile.resume and not skills:
        try:
            with profile.resume.open("rb") as f:
                text = extract_text_from_pdf(f)
                skills = extract_skills(text)

            if skills:
                profile.skills = ",".join(skills)
                profile.save()

        except Exception as e:
            print("Resume parsing error:", e)

    if listing_type == "recommended" and skills:
        query = " ".join(skills) + " internships India"

    jobs, api_error = fetch_jobs(query)

    for job in jobs:
        job_text = (
            job.get("title", "") + " " +
            job.get("description", "")
        ).lower()

        match_count = 0
        matched_skills = []

        for skill in skills:
            if contains_skill(job_text, skill):
                match_count += 1
                matched_skills.append(skill)

        job["match_score"] = match_count
        job["matched_skills"] = matched_skills

    if listing_type == "recommended":
        jobs = [job for job in jobs if job["match_score"] > 0]
        jobs.sort(key=lambda x: x["match_score"], reverse=True)

    if listing_type == "recommended" and skills:
        query = " ".join(skills[:3]) + " internships India"

    print("Listing type:", listing_type)
    print("Query used:", query)
    print("Skills:", skills)
    print("Jobs found:", len(jobs))

    return render(request, "listings.html", {
        "jobs": jobs,
        "saved_skills": skills,
        "query_used": query,
        "listing_type": listing_type,
        "api_error": api_error,
    })

@login_required
def recommended_listings(request):
    API_KEY =os.environ.get("SERPAPI_KEY")
    url = "https://serpapi.com/search.json"

    profile, created = Profile.objects.get_or_create(user=request.user)

    skills = []
    if profile.skills:
        skills = profile.skills.split(",")

    query = " ".join(skills) + " internships India" if skills else "software internships India"

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("Recommended query:", query)
    print("SerpAPI response:", data)

    jobs = data.get("jobs_results", [])

    return render(request, "listings.html", {
        "jobs": jobs,
        "query_used": query,
        "saved_skills": skills
    })

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def about(request):
    return render(request, 'about.html')

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        resume=request.FILES.get("resume")
        if resume and not resume.name.lower().endswith('.pdf'):
            return render(request, "signup.html", {"error": "Please upload a PDF file for your resume."})
        user = User.objects.create_user(username=username, password=password)
        profile=Profile.objects.create(user=user,resume=resume)
        login(request, user)
        return redirect("listings")

    return render(request, "signup.html")

def user_login(request):
    error = None

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid username or password"

    return render(request, "login.html", {"error": error})

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def process_resume(request):
    profile = request.user.profile

    if profile.resume:
        text = extract_resume_text(profile.resume.path)
        skills = extract_skills_from_text(text)

        profile.extracted_text = text
        profile.extracted_skills = skills
        profile.save()

    return redirect("recommended_listings")

def score_job(job, user_skills):
    content = f"{job.get('title', '')} {job.get('description', '')}".lower()
    matches = []

    for skill in user_skills:
        if skill.lower() in content:
            matches.append(skill)

    return {
        "score": len(matches),
        "matched_skills": matches
    }

