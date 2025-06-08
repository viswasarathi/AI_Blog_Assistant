import streamlit as st
import requests
import os

HF_TOKEN = st.secrets['HF_TOKEN']

# 🚀 Changed API_URL to use Llama 3.1 8B Instruct model
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# 🚀 Call HF inference endpoint (no download)
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    
  
    print(f"API Status Code: {response.status_code}")
    print(f"API Response Content: {response.text[:800]}...") 

    try:
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
        return {"error": f"HTTP error from API: {response.text}"}
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"JSON Decode error: {json_err} - Response: {response.text}")
        return {"error": f"Failed to decode JSON from API. Raw response: {response.text[:200]}..."}
    except Exception as err:
        print(f"Other error occurred: {err} - Response: {response.text}")
        return {"error": f"An unexpected error occurred: {err}. Raw response: {response.text[:200]}..."}


# 🧠 Generate blog
def generate_blog(topic, audience, word_limit):
    # Llama 3.1 models are instruction-tuned, so framing the prompt as an instruction is good.
    prompt = f"You are a helpful AI assistant tasked with writing blog posts.\n\nWrite a blog post for {audience} on the topic '{topic}'. Aim for approximately {word_limit} words. Ensure it is engaging and informative."
    
    output = query({
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": word_limit * 2, # Allow more tokens to ensure word limit is met
            "temperature": 0.7,
            "do_sample": True, # Recommended for creative text generation
            "top_p": 0.9 # Recommended for creative text generation
        }
    })

    if isinstance(output, dict) and "error" in output:
        return f"❌ Error: {output['error']}"
        
    # The structure of the output might vary slightly, but often it's a list with a 'generated_text' key
    if isinstance(output, list) and len(output) > 0 and 'generated_text' in output[0]:
        # The model might include the prompt in the output, so we need to trim it.
        # This is a heuristic and might need adjustment based on exact model behavior.
        generated_text = output[0]['generated_text']
        if prompt in generated_text:
            return generated_text.split(prompt, 1)[1].strip()
        return generated_text # If prompt is not found, return full text
    else:
        return f"❌ Unexpected API response format or no generated text: {output}"

# 🌐 Streamlit UI
st.set_page_config(page_title="LLaMA 3.1 Blog Generator (Cloud)", page_icon="🦙")
st.title("🤖AI Blog Assistant")


topic = st.text_input("Enter the blog topic:")
col1, col2 = st.columns(2)

with col1:
    word_limit = st.slider("Select word limit", 50, 1000, 250)

with col2:
    audience = st.selectbox("Target audience", ["General Public", "Students", "Professionals", "Tech Enthusiasts" , "Researcher"])

if st.button("Generate Blog"):
    if not topic:
        st.warning("Please enter a topic.")
    # Check for the placeholder token to remind the user
    elif HF_TOKEN == "hf_YOUR_ACTUAL_TOKEN_HERE": 
        st.error("Please replace 'hf_YOUR_ACTUAL_TOKEN_HERE' with your actual Hugging Face token in the script.")
    else:
        with st.spinner("Generating blog using Llama 3.1 from cloud..."):
            result = generate_blog(topic, audience, word_limit)
            st.success("✅ Blog generated!")
            st.markdown(result)