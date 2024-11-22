import streamlit as st
import openai
from googleapiclient.discovery import build
import requests

# Title of the Web App
st.title("Participant Sourcing and Recruiting")

# Input fields
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
google_api_key = st.sidebar.text_input("Enter your Google API Key", type="password")
cx_key = st.sidebar.text_input("Enter your Google Programmable Search Engine CX Key", type="password")

if not api_key or not google_api_key or not cx_key:
    st.warning("Please enter all API keys to proceed.")
else:
    openai.api_key = api_key

# Project description
st.header("Project Details")
project_description = st.text_area("Describe your research project")

# Research participants requirements
st.header("Research Participant Requirements")
job_title = st.text_input("Job Title")
company_size = st.text_input("Company Size")
country = st.text_input("Country")

if st.button("Find Participants"):
    if not project_description or not job_title or not company_size or not country:
        st.error("Please fill in all fields.")
    else:
        # Function to perform Google search
        def google_search(query, api_key, cx):
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=cx).execute()
            return result.get("items", [])

        # Agent 1: Find participants
        search_query = f"{job_title} at companies with {company_size} employees in {country}"
        st.write(f"Searching for participants matching: {search_query}")

        search_results = google_search(search_query, google_api_key, cx_key)

        participants = []
        for item in search_results:
            title = item.get("title", "No title")
            snippet = item.get("snippet", "No snippet")
            link = item.get("link", "")
            participants.append({"title": title, "snippet": snippet, "link": link})

        st.subheader("Found Participants")
        for p in participants:
            st.write(f"**Name/Title:** {p['title']}")
            st.write(f"**Details:** {p['snippet']}")
            st.write(f"**Profile:** [Link]({p['link']})")
            st.write("---")

        # Agent 2: Generate outreach messages
        if participants:
            st.header("Generate Outreach Messages")
            for participant in participants:
                if st.button(f"Generate Message for {participant['title']}"):
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=(
                            f"Write a professional outreach message to recruit a research participant. "
                            f"The participant's details are: {participant}. "
                            f"The project is about: {project_description}."
                        ),
                        max_tokens=150
                    )
                    st.write(response.choices[0].text.strip())
