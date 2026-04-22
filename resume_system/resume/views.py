"""
views.py  —  resume app
========================
Handles all HTTP views:
  home            → landing page
  login_view      → email-based authentication
  register        → new user registration (with password confirmation)
  logout_view     → session termination
  dashboard       → user's resume history + stats
  upload_resume   → file upload, NLP analysis, result rendering
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models

from .forms import ResumeForm
from .models import Resume
from .resume_parser import extract_text
from analyzer.job_matcher import get_real_time_jobs
from analyzer.nlp_engine import clean_universal_text, detect_grammar_errors, ai_grammar_integrity_check
from analyzer.suggestions import generate_suggestions


# ── 1. Landing Page ───────────────────────────────────────────────────────────

def home(request):
    """Renders the public landing / marketing page."""
    return render(request, 'index.html')


# ── 2. Authentication ─────────────────────────────────────────────────────────

def logout_view(request):
    """Logs the user out and redirects to the landing page."""
    logout(request)
    return redirect('home')


def login_view(request):
    """
    Email-based login view.

    Django stores users with email as username, so we authenticate
    using the email value in the 'username' field.
    """
    # Already logged-in users are bounced to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {}

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        # Authenticate using email stored as Django username
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Respect any ?next= redirect parameter from @login_required
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            context['error'] = 'Invalid email or password. Please try again.'

    return render(request, 'login.html', context)


def register(request):
    """
    User registration view.

    Validates:
      - Email uniqueness
      - Password length (≥ 8 chars)
      - Password confirmation match
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {}

    if request.method == 'POST':
        first_name       = request.POST.get('first_name', '').strip()
        last_name        = request.POST.get('last_name', '').strip()
        email            = request.POST.get('email', '').strip().lower()
        password         = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # ── Validation ──────────────────────────────────────────────────────
        if not first_name or not email:
            context['error'] = 'First name and email are required.'
        elif password != confirm_password:
            context['error'] = 'Passwords do not match. Please try again.'
        elif len(password) < 8:
            context['error'] = 'Password must be at least 8 characters long.'
        elif User.objects.filter(username=email).exists():
            context['error'] = 'An account with this email already exists.'
        else:
            # ── Create user ──────────────────────────────────────────────────
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            context['success'] = 'Account created successfully! Please log in.'
            return redirect('login')

    return render(request, 'register.html', context)


# ── 3. Dashboard ──────────────────────────────────────────────────────────────

@login_required(login_url='login')
def dashboard(request):
    """
    Displays the authenticated user's resume history, average scores,
    and quick-action buttons.
    """
    resumes    = request.user.resumes.order_by('-uploaded_at')
    total      = resumes.count()
    avg_score  = resumes.aggregate(models.Avg('score')).get('score__avg') or 0
    avg_grammar = resumes.aggregate(models.Avg('grammar_score')).get('grammar_score__avg') or 0

    # Best score for the "personal best" stat card
    best_score = resumes.aggregate(models.Max('score')).get('score__max') or 0

    return render(request, 'dashboard.html', {
        'resumes':       resumes,
        'total':         total,
        'average_score': round(avg_score, 1),
        'average_grammar': round(avg_grammar, 1),
        'best_score':    best_score,
    })


# ── 4. Resume Upload & Analysis ───────────────────────────────────────────────

@login_required(login_url='login')
def upload_resume(request):
    """
    Handles resume upload and full NLP analysis pipeline:

    1. Parse the uploaded PDF/DOCX → extract raw text
    2. Tokenize resume text + job description using clean_universal_text()
    3. Compute matched & missing skill tokens
    4. Calculate final match score as: matched / jd_tokens * 100
    5. Run grammar integrity check → save grammar_score to DB
    6. Generate AI suggestions using suggestions.py
    7. Fetch live job listings via JSearch API (or static fallback)
    8. Persist all results to DB
    9. Render result.html with full context
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            # ── Save basic record ────────────────────────────────────────────
            resume = form.save(commit=False)
            resume.user = request.user
            job_desc = form.cleaned_data.get('job_description', '')
            resume.job_description = job_desc
            resume.save()

            # ── Step 1: Extract raw text from uploaded file ──────────────────
            text = extract_text(resume.file.path)

            # ── Step 2: NLP tokenisation of resume + JD ─────────────────────
            resume_tokens = clean_universal_text(text)
            jd_tokens     = clean_universal_text(job_desc)

            # ── Step 3: Skill intersection & gap ─────────────────────────────
            matched  = sorted(list(set(resume_tokens) & set(jd_tokens)))
            missing  = sorted(list(set(jd_tokens) - set(resume_tokens)))

            # ── Step 4: Match score ───────────────────────────────────────────
            final_score = int((len(matched) / len(jd_tokens)) * 100) if jd_tokens else 0

            # ── Step 5: Grammar check ─────────────────────────────────────────
            grammar_result = ai_grammar_integrity_check(text)
            grammar_issues = detect_grammar_errors(text)
            grammar_score  = grammar_result.get('grammar_score', 100)

            # ── Step 6: AI Suggestions ────────────────────────────────────────
            suggestions = generate_suggestions(
                score=final_score,
                missing_skills=missing,
                grammar_issues=grammar_issues,
                resume_text=text,
            )

            # ── Step 7: Live job fetch ────────────────────────────────────────
            query_str = (
                f"{' '.join(matched[:3])} jobs in India"
                if matched
                else "Junior Developer jobs in India"
            )
            real_jobs = get_real_time_jobs(query_str)

            # ── Step 8: Persist results ───────────────────────────────────────
            resume.score          = final_score
            resume.grammar_score  = grammar_score
            resume.matched_skills = ', '.join(matched)
            resume.missing_skills = ', '.join(missing[:12])
            resume.ai_suggestions = json.dumps(suggestions)
            resume.save()

            # ── Step 9: Render result page ────────────────────────────────────
            return render(request, 'result.html', {
                'score':         final_score,
                'grammar_score': grammar_score,
                'matched':       matched,
                'missing':       missing[:12],
                'grammar_issues': grammar_issues,
                'grammar_review': grammar_result.get('review', ''),
                'suggestions':   suggestions,
                'jobs':          real_jobs,
                'resume':        resume,
            })

    else:
        form = ResumeForm()

    return render(request, 'upload.html', {'form': form})