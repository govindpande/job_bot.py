# app.py

import streamlit as st
import openai
import os
import json
from linkedin_api import Linkedin
import pandas as pd

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_linkedin_jobs(api, keywords, location, num_jobs=5, posted_in_last_minutes=15):
    st.info(f"Fetching LinkedIn jobs for '{keywords}' in '{location}' posted in the last {posted_in_last_minutes} minutes...")
    try:
        jobs = api.search_jobs(
            keywords=keywords,
            location_name=location,
            listed_at=posted_in_last_minutes * 60,  # Convert minutes to seconds
            limit=num_jobs
        )
        return jobs
    except Exception as e:
        st.error(f"Error fetching jobs from LinkedIn: {e}")
        return []

def generate_custom_resume(profile, job_description):
    prompt = f"""
    You are a professional career advisor. Given the user's profile and the job description, tailor the resume to highlight relevant skills and experiences.

    User Profile:
    {profile}

    Job Description:
    {job_description}

    Customized Resume:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    customized_resume = response.choices[0].message.content.strip()
    return customized_resume

def generate_cover_letter(profile, job_description):
    prompt = f"""
    You are an expert career coach. Based on the user's profile and the job description, write a tailored cover letter for the job application.

    User Profile:
    {profile}

    Job Description:
    {job_description}

    Cover Letter:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )

    cover_letter = response.choices[0].message.content.strip()
    return cover_letter

def main():
    st.title("Automate Your Job Application with GPT-4 and LinkedIn API")

    # LinkedIn Credentials
    st.sidebar.header("LinkedIn Credentials")
    linkedin_username = st.sidebar.text_input("LinkedIn Username (Email)", type="default")
    linkedin_password = st.sidebar.text_input("LinkedIn Password", type="password")

    if not linkedin_username or not linkedin_password:
        st.warning("Please enter your LinkedIn credentials to proceed.")
        return

    # Initialize LinkedIn API
    try:
        api = Linkedin(linkedin_username, linkedin_password)
    except Exception as e:
        st.error(f"Failed to authenticate with LinkedIn: {e}")
        return

    # Profile Section
    st.sidebar.header("Your Profile")
    if "profile" not in st.session_state:
        st.session_state.profile = {}

    # Predefined profile questions
    profile_questions = {
        "full_name": "Full Name",
        "email": "Email Address",
        "phone": "Phone Number",
        "address": "Address",
        "summary": "Professional Summary",
        "skills": "Skills (comma-separated)",
        "education": "Education",
        "experience": "Work Experience",
    }

    # Load any new questions encountered during job applications
    if "additional_questions" in st.session_state:
        profile_questions.update(st.session_state.additional_questions)

    for key, question in profile_questions.items():
        st.session_state.profile[key] = st.sidebar.text_area(question, st.session_state.profile.get(key, ""), height=100)

    st.header("Job Search Parameters")
    keywords = st.text_input("Job Title or Keywords")
    location = st.text_input("Location")
    num_jobs = st.number_input("Number of Jobs to Fetch", min_value=1, max_value=100, value=5)
    posted_in_last_minutes = st.number_input("Posted in Last (minutes)", min_value=1, max_value=1440, value=15)

    if st.button("Fetch LinkedIn Jobs"):
        if keywords and location:
            with st.spinner("Fetching jobs from LinkedIn..."):
                jobs = fetch_linkedin_jobs(api, keywords, location, num_jobs, posted_in_last_minutes)
            if jobs:
                st.session_state.jobs = jobs
                st.success(f"Fetched {len(jobs)} jobs from LinkedIn.")
            else:
                st.error("No jobs found. Try adjusting your search parameters.")
        else:
            st.error("Please provide both job title/keywords and location.")

    if "jobs" in st.session_state:
        jobs = st.session_state.jobs
        for idx, job in enumerate(jobs):
            st.subheader(f"Job {idx+1}: {job['title']} at {job['companyDetails']['com.linkedin.voyager.deco.jobs.web.shared.WebCompactCompany']['name']}")
            st.write(f"**Location**: {job.get('formattedLocation', 'N/A')}")
            st.write(f"**Job URL**: https://www.linkedin.com/jobs/view/{job['dashEntityUrn'].split(':')[-1]}")
            st.write(f"**Description**:\n{job.get('description', 'No description available.')}")

            if st.button(f"Customize Resume and Cover Letter for Job {idx+1}"):
                with st.spinner("Generating customized resume and cover letter..."):
                    profile_str = "\n".join(f"{k}: {v}" for k, v in st.session_state.profile.items())
                    job_description = job.get('description', '')
                    customized_resume = generate_custom_resume(profile_str, job_description)
                    cover_letter = generate_cover_letter(profile_str, job_description)
                st.success("Generated customized documents.")

                st.header("Customized Resume")
                st.write(customized_resume)

                st.header("Cover Letter")
                st.write(cover_letter)

                st.info("Please review your resume and cover letter before applying.")

                # Dynamically add new questions if encountered
                # For example, if the job application asks for a portfolio link
                # This is a placeholder example
                new_question_key = f"portfolio_link"
                new_question = f"Portfolio Link"
                if new_question_key not in st.session_state.profile:
                    st.session_state.additional_questions = st.session_state.get("additional_questions", {})
                    st.session_state.additional_questions[new_question_key] = new_question
                    st.warning(f"New question added to profile: {new_question}")

        # Save the updated profile
        st.session_state.profile_json = json.dumps(st.session_state.profile)

if __name__ == "__main__":
    main()
