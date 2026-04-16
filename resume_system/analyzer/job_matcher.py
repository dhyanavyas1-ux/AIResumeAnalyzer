import requests

def get_real_time_jobs(skills_query):
    """Fetches verified jobs from JSearch API."""
    url = "https://jsearch.p.rapidapi.com/search"

    if isinstance(skills_query, str):
        query = skills_query
    else:
        query = f"{' '.join(skills_query[:3])} jobs in India" if skills_query else "Junior Developer jobs in India"

    headers = {
        "X-RapidAPI-Key": "YOUR_API_KEY_HERE",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"query": query, "num_pages": "1"})
        if response.status_code == 200:
            data = response.json().get('data', [])
            return [
                {
                    'title': j.get('job_title', 'Untitled Role'),
                    'company': j.get('employer_name', 'Unknown Company'),
                    'link': j.get('job_apply_link', '#'),
                    'location': j.get('job_city', 'India')
                }
                for j in data[:5]
            ]
    except Exception:
        pass
    return []