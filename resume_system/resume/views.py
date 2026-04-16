from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from .forms import ResumeForm
from .models import Resume
from .resume_parser import extract_text
from analyzer.job_matcher import get_real_time_jobs
from analyzer.nlp_engine import clean_universal_text, detect_grammar_errors

# --- 1. Basic Navigation ---
def home(request):
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# --- 2. Authentication Logic (Fixes the login_view error) ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        # Django uses username field for authentication; we use email as username
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            context['error'] = 'Invalid email or password.'
    return render(request, 'login.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    context = {}
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        if User.objects.filter(username=email).exists():
            context['error'] = 'An account with this email already exists.'
        else:
            User.objects.create_user(
                username=email, 
                email=email, 
                password=password, 
                first_name=first_name, 
                last_name=last_name
            )
            context['success'] = 'Account created successfully. Please login.'
            return redirect('login')
    return render(request, 'register.html', context)

# --- 3. Dashboard Logic ---
@login_required(login_url='login')
def dashboard(request):
    resumes = request.user.resumes.order_by('-uploaded_at')
    total = resumes.count()
    
    # Calculate stats for the bar
    avg_score = resumes.aggregate(models.Avg('score')).get('score__avg') or 0
    # Grammar score is calculated as 100 minus penalty for issues
    avg_grammar = resumes.aggregate(models.Avg('grammar_score')).get('grammar_score__avg') or 0

    return render(request, 'dashboard.html', {
        'resumes': resumes,
        'total': total,
        'average_score': avg_score,
        'average_grammar': avg_grammar,
    })

# --- 4. Manual NLP Analysis Logic ---
@login_required(login_url='login')
def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            job_desc = form.cleaned_data.get("job_description", "")
            resume.save()

            # 1. NLP Extraction (Dynamic)
            text = extract_text(resume.file.path)
            resume_tokens = clean_universal_text(text)
            jd_tokens = clean_universal_text(job_desc)

            # 2. Skill Intersection (Matched and Missing)
            matched = sorted(list(set(resume_tokens) & set(jd_tokens)))
            missing = sorted(list(set(jd_tokens) - set(resume_tokens)))
            
            # 3. Dynamic Scoring
            final_score = int((len(matched) / len(jd_tokens) * 100)) if jd_tokens else 0
            
            # 4. Save results to DB
            resume.score = final_score
            resume.save()

            # 5. Job Fetching Logic
            if matched:
                query_str = f"{' '.join(matched[:3])} jobs in India"
            else:
                query_str = "Junior Developer jobs in India"
            real_jobs = get_real_time_jobs(query_str)

            # 6. Pass everything to Result Template
            return render(request, "result.html", {
                "score": final_score,
                "matched": matched,
                "missing": missing[:12],
                "grammar_issues": detect_grammar_errors(text),
                "jobs": real_jobs
            })
    else:
        form = ResumeForm()
    return render(request, "upload.html", {"form": form})