            if not is_temporary_error(exc) or attempt == MAX_RETRIES - 1:
                raise
            # Exponential backoff plus jitter: roughly 2s, 4s, then 8s.
            delay = min(2 ** (attempt + 1), 16) + random.uniform(0, 0.75)
            time.sleep(delay)

    raise RuntimeError("Gemini could not complete the request after retries.") from last_error


st.title("📄 Resume ATS Checker")
st.write("Upload a resume to receive an estimated ATS-readiness score and practical improvement suggestions.")
st.info(
    "Your score is an AI-generated estimate, not a score from a real employer's applicant tracking system. "
    "Results can vary by job and ATS software."
)

with st.sidebar:
    st.header("How it works")
    st.write(
        "1. Upload a PDF, DOCX, or TXT resume.\n"
        "2. Optionally add the job description.\n"
        "3. Get an estimated score and prioritized suggestions."
    )
    st.caption("Keep API keys in Streamlit Secrets or environment variables, never in source code.")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"],
    help="Maximum file size: 5 MB. Scanned PDFs without selectable text may not work.",
)
job_description = st.text_area(
    "Paste the job description (optional)",
    placeholder="Paste the job advertisement here to get a more relevant keyword and job-match review.",
    height=180,
)

if uploaded_file is not None:
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"The file is too large. Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")
    else:
        st.caption(f"Selected file: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

if st.button("Analyze Resume", type="primary", disabled=uploaded_file is None):
    if uploaded_file is None:
        st.warning("Please upload a resume first.")
    elif uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")
    else:
        api_key = get_secret("GEMINI_API_KEY")
        model_name = get_secret("GEMINI_MODEL", DEFAULT_MODEL_NAME) or DEFAULT_MODEL_NAME

        if not api_key:
            st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets or your local environment.")
        else:
            try:
                with st.spinner("Reading your resume and generating feedback. Temporary Gemini overloads will be retried automatically..."):
                    resume_text = extract_resume_text(uploaded_file)
                    basic = estimate_basic_checks(resume_text)
                    review = call_gemini(resume_text, job_description, api_key, model_name)

                st.success("Resume analysis complete")
                col1, col2 = st.columns(2)
                col1.metric("Extracted word count", f"{basic['word_count']:,}")
                col2.metric("Sections detected", f"{sum(basic['sections'].values())} / {len(basic['sections'])}")

                with st.expander("Basic text and section checks", expanded=False):
                    for check, passed in basic["checks"].items():
                        st.write(f"{'✅' if passed else '⚠️'} {check}")
                    st.caption("These basic checks are separate from the AI's estimated score.")

                st.markdown(review)
                st.download_button(
                    "Download feedback as Markdown",
                    data=review,
                    file_name="resume_review.md",
                    mime="text/markdown",
                )
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                message = str(exc).lower()
                if "503" in message or "unavailable" in message or "high demand" in message:
                    st.error(
                        "Gemini is still overloaded after several automatic retries. "
                        "Wait a few minutes and try again. Your resume file is not necessarily the problem."
                    )
                elif "404" in message or "not found" in message:
                    st.error(
                        f"Gemini model '{model_name}' was not found or is unavailable to your API key. "
                        "Check the model ID in Streamlit Secrets under GEMINI_MODEL, or remove that setting to use the default model."
                    )
                elif "429" in message or "quota" in message or "resource_exhausted" in message:
                    st.error("Gemini API quota or rate limit reached. Check your Google AI Studio usage and try again later.")
                elif "401" in message or "403" in message or "api key" in message.lower() or "permission" in message:
                    st.error("Gemini rejected the API key or permissions. Verify GEMINI_API_KEY in Streamlit Secrets.")
                else:
                    st.error("Analysis failed. Check the API key, model setting, connection, and Gemini API availability.")
                # Keep technical details useful but avoid printing the API key.
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")

st.divider()
st.caption("Tip: Tailor your resume honestly for each job. No tool can guarantee an interview or hiring outcome.")
            if not is_temporary_error(exc) or attempt == MAX_RETRIES - 1:
                raise
            # Exponential backoff plus jitter: roughly 2s, 4s, then 8s.
            delay = min(2 ** (attempt + 1), 16) + random.uniform(0, 0.75)
            time.sleep(delay)

    raise RuntimeError("Gemini could not complete the request after retries.") from last_error


st.title("📄 Resume ATS Checker")
st.write("Upload a resume to receive an estimated ATS-readiness score and practical improvement suggestions.")
st.info(
    "Your score is an AI-generated estimate, not a score from a real employer's applicant tracking system. "
    "Results can vary by job and ATS software."
)

with st.sidebar:
    st.header("How it works")
    st.write(
        "1. Upload a PDF, DOCX, or TXT resume.\n"
        "2. Optionally add the job description.\n"
        "3. Get an estimated score and prioritized suggestions."
    )
    st.caption("Keep API keys in Streamlit Secrets or environment variables, never in source code.")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"],
    help="Maximum file size: 5 MB. Scanned PDFs without selectable text may not work.",
)
job_description = st.text_area(
    "Paste the job description (optional)",
    placeholder="Paste the job advertisement here to get a more relevant keyword and job-match review.",
    height=180,
)

if uploaded_file is not None:
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"The file is too large. Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")
    else:
        st.caption(f"Selected file: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

if st.button("Analyze Resume", type="primary", disabled=uploaded_file is None):
    if uploaded_file is None:
        st.warning("Please upload a resume first.")
    elif uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")
    else:
        api_key = get_secret("GEMINI_API_KEY")
        model_name = get_secret("GEMINI_MODEL", DEFAULT_MODEL_NAME) or DEFAULT_MODEL_NAME

        if not api_key:
            st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets or your local environment.")
        else:
            try:
                with st.spinner("Reading your resume and generating feedback. Temporary Gemini overloads will be retried automatically..."):
                    resume_text = extract_resume_text(uploaded_file)
                    basic = estimate_basic_checks(resume_text)
                    review = call_gemini(resume_text, job_description, api_key, model_name)

                st.success("Resume analysis complete")
                col1, col2 = st.columns(2)
                col1.metric("Extracted word count", f"{basic['word_count']:,}")
                col2.metric("Sections detected", f"{sum(basic['sections'].values())} / {len(basic['sections'])}")

                with st.expander("Basic text and section checks", expanded=False):
                    for check, passed in basic["checks"].items():
                        st.write(f"{'✅' if passed else '⚠️'} {check}")
                    st.caption("These basic checks are separate from the AI's estimated score.")

                st.markdown(review)
                st.download_button(
                    "Download feedback as Markdown",
                    data=review,
                    file_name="resume_review.md",
                    mime="text/markdown",
                )
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                message = str(exc).lower()
                if "503" in message or "unavailable" in message or "high demand" in message:
                    st.error(
                        "Gemini is still overloaded after several automatic retries. "
                        "Wait a few minutes and try again. Your resume file is not necessarily the problem."
                    )
                elif "404" in message or "not found" in message:
                    st.error(
                        f"Gemini model '{model_name}' was not found or is unavailable to your API key. "
                        "Check the model ID in Streamlit Secrets under GEMINI_MODEL, or remove that setting to use the default model."
                    )
                elif "429" in message or "quota" in message or "resource_exhausted" in message:
                    st.error("Gemini API quota or rate limit reached. Check your Google AI Studio usage and try again later.")
                elif "401" in message or "403" in message or "api key" in message.lower() or "permission" in message:
                    st.error("Gemini rejected the API key or permissions. Verify GEMINI_API_KEY in Streamlit Secrets.")
                else:
                    st.error("Analysis failed. Check the API key, model setting, connection, and Gemini API availability.")
                # Keep technical details useful but avoid printing the API key.
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")

st.divider()
st.caption("Tip: Tailor your resume honestly for each job. No tool can guarantee an interview or hiring outcome.")

    elif uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")
    else:
        api_key = get_secret("GEMINI_API_KEY")
        model_name = get_secret("GEMINI_MODEL", DEFAULT_MODEL_NAME) or DEFAULT_MODEL_NAME

        if not api_key:
            st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets or your local environment.")
        else:
            try:
                with st.spinner("Reading your resume and generating feedback. Temporary Gemini overloads will be retried automatically..."):
                    resume_text = extract_resume_text(uploaded_file)
                    basic = estimate_basic_checks(resume_text)
                    review = call_gemini(resume_text, job_description, api_key, model_name)

                st.success("Resume analysis complete")
                col1, col2 = st.columns(2)
                col1.metric("Extracted word count", f"{basic['word_count']:,}")
                col2.metric("Sections detected", f"{sum(basic['sections'].values())} / {len(basic['sections'])}")

                with st.expander("Basic text and section checks", expanded=False):
                    for check, passed in basic["checks"].items():
                        st.write(f"{'✅' if passed else '⚠️'} {check}")
                    st.caption("These basic checks are separate from the AI's estimated score.")

                st.markdown(review)
                st.download_button(
                    "Download feedback as Markdown",
                    data=review,
                    file_name="resume_review.md",
                    mime="text/markdown",
                )
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                message = str(exc).lower()
                if "503" in message or "unavailable" in message or "high demand" in message:
                    st.error(
                        "Gemini is still overloaded after several automatic retries. "
                        "Wait a few minutes and try again. Your resume file is not necessarily the problem."
                    )
                elif "404" in message or "not found" in message:
                    st.error(
                        f"Gemini model '{model_name}' was not found or is unavailable to your API key. "
                        "Check the model ID in Streamlit Secrets under GEMINI_MODEL, or remove that setting to use the default model."
                    )
                elif "429" in message or "quota" in message or "resource_exhausted" in message:
                    st.error("Gemini API quota or rate limit reached. Check your Google AI Studio usage and try again later.")
                elif "401" in message or "403" in message or "api key" in message.lower() or "permission" in message:
                    st.error("Gemini rejected the API key or permissions. Verify GEMINI_API_KEY in Streamlit Secrets.")
                else:
                    st.error("Analysis failed. Check the API key, model setting, connection, and Gemini API availability.")
                # Keep technical details useful but avoid printing the API key.
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")

st.divider()
st.caption("Tip: Tailor your resume honestly for each job. No tool can guarantee an interview or hiring outcome.")
