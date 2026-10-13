# InternSight

A Django web app for discovering internships. InternSight pulls live Google Jobs listings through SerpAPI, reads skills from your uploaded PDF resume, and ranks recommended internships by how well they match your skills.

## Features

- **User accounts:** sign up, log in and log out with Django's built-in authentication. Pages other than login and signup require a login.
- **Resume upload:** upload a PDF resume at signup.
- **Skill extraction:** the resume text is read with PyPDF2 and matched against a list of common technical skills (Python, Java, SQL, Django, React and others). The skills are saved to your profile.
- **Live internship listings:** fetches current results from Google Jobs through the SerpAPI `google_jobs` engine and shows company, role, location and job details.
- **Recommended jobs:** builds a search from your extracted skills, scores each listing by how many of your skills appear in its title and description, and shows the best matches first with a match-score badge.
- **Pages:** home, about, dashboard, listings, login and signup, with a shared header and footer.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Database | SQLite |
| Templates and styling | Django templates, HTML, CSS |
| Resume parsing | PyPDF2 |
| Job data | SerpAPI (Google Jobs engine) via `requests` |

## Project structure

```
internsight/
├── manage.py
├── requirements.txt
├── internsight/          # project settings and root URLs
├── internsight_app/      # views, models (Profile), app URLs
└── templates/            # HTML templates and shared partials
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- A free SerpAPI account and API key from https://serpapi.com

### Setup

1. Clone the repo and open the project folder:
   ```
   git clone https://github.com/aarushivaish/internsight.git
   cd internsight
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   On macOS or Linux, use `source venv/bin/activate` instead.

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Add your keys. Create a file named `.env` next to `manage.py`:
   ```
   SERPAPI_KEY=your-serpapi-key
   DJANGO_SECRET_KEY=your-random-secret-key
   ```
   You can also set them as environment variables in your terminal. The `.env` file is listed in `.gitignore` and must never be committed.

5. Create the database tables:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/ in your browser, sign up with a PDF resume, and open the Listings page.

## How the recommendations work

1. On the first visit to Listings, the resume PDF is read and its text is matched against a list of known skills.
2. The matched skills are stored on the user's profile.
3. For the Recommended view, the skills are used to build a Google Jobs query, such as `python django sql internships India`.
4. Each returned job is scored by counting how many of the user's skills appear in its title and description. Jobs with no matching skills are dropped and the rest are sorted by score.

## Known limitations and planned work

- The dashboard currently shows placeholder data. Tracking saved listings and applications is planned.
- The filter chips on the listings page (Software, AI/ML, Remote, Paid) are not functional yet.
- Skill matching uses simple keyword search, so short skill names can produce false matches. Word-boundary matching is planned.
- Only PDF resumes can be parsed.
- Listings are fetched from SerpAPI on every page load, so results should be cached to save API quota.
- Only Google Jobs is used as a data source.

## Security notes

- API keys and the Django secret key are read from environment variables and are not stored in the repository.
- `DEBUG` is on in the default settings. Turn it off and set `ALLOWED_HOSTS` before deploying anywhere public.

