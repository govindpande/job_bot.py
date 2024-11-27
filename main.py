# app.py

import streamlit as st
import openai
import os
import requests
from bs4 import BeautifulSoup
import json

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set your Bright Data credentials
BRIGHT_DATA_USER = os.getenv("BRIGHT_DATA_USER")
BRIGHT_DATA_PASSWORD = os.getenv("BRIGHT_DATA_PASSWORD")

def fetch_job_descriptions(query, location, num_jobs=5):
    st.info(f"Fetching job descriptions for '{query}' in '{location}'...")
    # Placeholder for Bright Data API integration
    # This is where you would use Bright Data's API to scrape Indeed
    # For demonstration purposes, we'll use a mocked list of job descriptions
    job_descriptions = []
    for i in range(num_jobs):
        job_descriptions.append(f"Job Description {i+1} for {query} in {location}.")
    return job_descriptions

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
    st.title("Automate Your Job Application with GPT-4 and Bright Data")

    # Profile Section
    st.sidebar.header("Your Profile")
    if "profile" not in st.session_state:
        st.session_state.profile = {}

    # Dynamically add profile questions
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
        st.session_state.profile[key] = st.sidebar.text_input(question, st.session_state.profile.get(key, ""))

    st.header("Job Search Parameters")
    query = st.text_input("Job Title or Keywords")
    location = st.text_input("Location")

    if st.button("Fetch Job Descriptions"):
        if query and location:
            job_descriptions = fetch_job_descriptions(query, location)
            st.session_state.job_descriptions = job_descriptions
            st.success(f"Fetched {len(job_descriptions)} job descriptions.")
        else:
            st.error("Please provide both job title/keywords and location.")

    if "job_descriptions" in st.session_state:
        for idx, jd in enumerate(st.session_state.job_descriptions):
            st.subheader(f"Job {idx+1}")
            st.write(jd)

            if st.button(f"Customize Resume and Cover Letter for Job {idx+1}"):
                with st.spinner("Generating customized resume and cover letter..."):
                    profile_str = "\n".join(f"{k}: {v}" for k, v in st.session_state.profile.items())
                    customized_resume = generate_custom_resume(profile_str, jd)
                    cover_letter = generate_cover_letter(profile_str, jd)
                st.success("Generated customized documents.")

                st.header("Customized Resume")
                st.write(customized_resume)

                st.header("Cover Letter")
                st.write(cover_letter)

                # Placeholder for job application submission
                if st.button(f"Apply for Job {idx+1}"):
                    st.info("Submitting application...")
                    # Here you would add code to submit the application
                    st.success("Application submitted.")

                    # Dynamically add new questions if encountered
                    # For example, if the job application asks for a portfolio link
                    new_question_key = f"portfolio_link_{idx+1}"
                    new_question = f"Portfolio Link for Job {idx+1}"
                    if new_question_key not in st.session_state.profile:
                        st.session_state.additional_questions = st.session_state.get("additional_questions", {})
                        st.session_state.additional_questions[new_question_key] = new_question
                        st.warning(f"New question added to profile: {new_question}")

    # Save the updated profile
    st.session_state.profile_json = json.dumps(st.session_state.profile)

if __name__ == "__main__":
    main()
