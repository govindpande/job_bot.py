# app.py

import streamlit as st
import openai
import os
import json
import csv
from jobspy import scrape_jobs
import pandas as pd

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_job_descriptions(site_names, search_term, location, results_wanted=5, hours_old=72):
    st.info(f"Fetching job descriptions for '{search_term}' in '{location}'...")
    try:
        jobs_df = scrape_jobs(
            site_name=site_names,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
        )
        return jobs_df
    except Exception as e:
        st.error(f"Error fetching job descriptions: {e}")
        return pd.DataFrame()

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
    st.title("Automate Your Job Application with GPT-4 and JobSpy")

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
    site_names = st.multiselect(
        "Select Job Sites to Search",
        options=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
        default=["indeed", "linkedin"]
    )
    search_term = st.text_input("Job Title or Keywords")
    location = st.text_input("Location")
    results_wanted = st.number_input("Number of Jobs to Fetch per Site", min_value=1, max_value=100, value=5)
    hours_old = st.number_input("Max Job Posting Age (in hours)", min_value=1, max_value=168, value=72)

    if st.button("Fetch Job Descriptions"):
        if site_names and search_term and location:
            with st.spinner("Fetching job descriptions..."):
                jobs_df = fetch_job_descriptions(site_names, search_term, location, results_wanted, hours_old)
            if not jobs_df.empty:
                st.session_state.jobs_df = jobs_df
                st.success(f"Fetched {len(jobs_df)} job descriptions.")
            else:
                st.error("No jobs found. Try adjusting your search parameters.")
        else:
            st.error("Please provide job sites, job title/keywords, and location.")

    if "jobs_df" in st.session_state:
        jobs_df = st.session_state.jobs_df
        for idx, job in jobs_df.iterrows():
            st.subheader(f"Job {idx+1}: {job['title']} at {job['company']}")
            st.write(f"**Location**: {job['city']}, {job['state']}")
            st.write(f"**Job Type**: {job['job_type']}")
            st.write(f"**Job URL**: {job['job_url']}")
            st.write(f"**Description**:\n{job['description']}")

            if st.button(f"Customize Resume and Cover Letter for Job {idx+1}"):
                with st.spinner("Generating customized resume and cover letter..."):
                    profile_str = "\n".join(f"{k}: {v}" for k, v in st.session_state.profile.items())
                    customized_resume = generate_custom_resume(profile_str, job['description'])
                    cover_letter = generate_cover_letter(profile_str, job['description'])
                st.success("Generated customized documents.")

                st.header("Customized Resume")
                st.write(customized_resume)

                st.header("Cover Letter")
                st.write(cover_letter)

                # Placeholder for job application submission
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
