import os
import re
import json
from openai import OpenAI
import streamlit as st
# Initialize OpenAI client
client = OpenAI(os.getenv("OPENAI_API_KEY"))
# Environment variables
#openai.api_key = os.getenv("OPENAI_API_KEY")

def contains_english(text):
    # Check if the text contains English characters
    return bool(re.search(r'[a-zA-Z]', text))

def generate_baby_names(last_name, gender, style, length, repetition_syllable):
    # Adjust prompt based on gender, style, and name length
    gender_text = "boy" if gender == "Male" else "girl"
    style_text = "popular" if style == "Popular names" else "unique and memorable"
    length_text = {
        "2 syllables": "two syllables",
        "1 syllable": "one syllable",
        "No preference": "one or two syllables"
    }[length]

    # Include the repetition syllable in the prompt if provided
    if repetition_syllable:
        repetition_text = (
            f"Create 5 names that include the syllable '{repetition_syllable}' either at the beginning or the end of the name. "
            f"Then, select the 5 names that best match with the last name '{last_name}'."
        )
    else:
        repetition_text = ""

    prompt = f"""
    Suggest 5 {gender_text} baby names that go well with the last name '{last_name}' and fit a {style_text} style in JSON format.
    Exclude the last name '{last_name}' in the names and recommend {length_text} names.
    Each name should be meaningful, modern, and have positive associations.
    {repetition_text}
    
    Provide each name as a JSON object in this format:
    {{
        "Name": "Suggested name",
        "Meaning": "Brief meaning or origin of the name",
        "Characteristics": "Explanation of the name's characteristics or related trends"
    }}

    Return the result as a JSON array following the above format.
    """

    # Generate name suggestions using the new OpenAI client and chat completion format
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in recommending baby names. Please suggest suitable names based on the provided criteria."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return completion.choices[0].message.content

def parse_names(json_content):
    try:
        # Extract pure JSON data if additional text surrounds it
        json_start = json_content.find('[')
        json_end = json_content.rfind(']') + 1
        pure_json = json_content[json_start:json_end]

        # Parse JSON string into a Python list
        parsed_names = json.loads(pure_json)
        return parsed_names
    except json.JSONDecodeError as e:
        st.error("Invalid JSON format. Please provide a valid JSON array.")
        st.error(e)
        return []

st.set_page_config(page_title="AI Baby Name Recommendation Service", page_icon="👶", layout="wide")

st.title("👶 AI Baby Name Recommendation Service")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    last_name = st.text_input("Please enter the last name:")
    gender = st.selectbox("Select the baby's gender:", ("Male", "Female"))
    style = st.selectbox("Choose a name style:", ("Popular names", "Unique names"))
    length = st.selectbox("Select the name length:", ("2 syllables", "1 syllable", "No preference"))
    repetition_syllable = st.text_input("Enter a repeated syllable (optional):")

    if st.button("Get Name Suggestions"):
        # Check if there are any English characters
        if not contains_english(last_name):
            st.error("Please enter the last name in English.")
        elif last_name:
            with st.spinner("Generating names..."):
                baby_names_json = generate_baby_names(last_name, gender, style, length, repetition_syllable)
                parsed_names = parse_names(baby_names_json)
                st.session_state.names = parsed_names
                st.success("Name suggestions generated successfully!")
        else:
            st.warning("Please enter a last name.")

with col2:
    if 'names' in st.session_state:
        for i, name in enumerate(st.session_state.names, 1):
            with st.expander(f"**Recommended Name {i}:** {name.get('Name', '')}"):
                st.markdown(f"**Meaning:** {name.get('Meaning', '')}")
                st.markdown(f"**Characteristics:** {name.get('Characteristics', '')}")
        
        st.markdown("---")
        st.info("These names are recommended by AI. For personalized naming, consider consulting a naming expert.")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>Developer Info: <a href='mailto:pavun9848@gmail.com'>pavun9848@gmail.com</a> | <a href='https://github.com/Pavun-KumarCH' target='_blank'>GitHub Profile</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
