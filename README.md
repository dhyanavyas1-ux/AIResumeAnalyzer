# AI Resume Analyzer & Skill Gap Engine

## Overview
The AI Resume Analyzer is a comprehensive full-stack web application designed to bridge the gap between job seekers and Applicant Tracking Systems (ATS). By leveraging Natural Language Processing (NLP) and custom taxonomy filtering, the system evaluates uploaded resumes against specific job roles. 

It provides users with a data-driven compatibility score, explicitly identifies missing technical skills, offers actionable grammar and content suggestions, and connects users directly with real-time, relevant job listings.

## 🚀 Core Features
* **Intelligent Skill Extraction & Matching:** Utilizes a custom Regex-powered NLP engine combined with a comprehensive JSON skills taxonomy to accurately extract multi-word technical skills (e.g., "Machine Learning", "Data Structures") while filtering out generic, non-technical nouns.
* **Automated Gap Analysis:** Calculates a precise ATS match percentage by comparing the parsed resume data against industry-standard requirements for the user's selected job role, generating distinct lists of "Matched" and "Missing" skills.
* **Real-Time Job Board Integration:** Connects seamlessly with the JSearch API to fetch and display live, role-specific job application links directly on the results dashboard.
* **Fault-Tolerant Architecture:** Implements a robust static fallback mechanism for the job search API, ensuring uninterrupted user experience even in the event of API rate limits or network failures.
* **Rule-Based Grammar & Tone Checking:** Analyzes resume text for common spelling errors and grammatical inconsistencies using low-latency regex and curated dictionaries, generating an overall grammar score and targeted improvement tips.
* **Secure User Authentication:** Features a custom Django authentication system utilizing an email-as-username login approach, complete with session management, password strength meters, and a secure user dashboard.
* **Dynamic UI/UX:** Built with a responsive, modern dark-themed interface featuring interactive statistics, custom CSS, and visually intuitive result cards to provide a seamless user experience.

## 💻 Technology Stack
* **Backend Framework:** Python, Django
* **Database:** SQLite
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Django Templates
* **AI & NLP Processing:** NLTK (Natural Language Toolkit), Python `re` (Regular Expressions)
* **External APIs:** RapidAPI (JSearch)
* **Security & Configuration:** `python-dotenv` for secure environment variable management

