import streamlit as st
import requests
from PIL import Image
import io

# === CONFIG ===
BACKEND_URL = "http://localhost:7071/api"  # adjust on deployment

# === PAGE SETUP ===
st.set_page_config(page_title="What Should I Eat?", layout="centered")
st.title("🍽️ What Should I Eat?")
st.subheader("Take a picture of your fridge, and get a meal suggestion!")

# === STATE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "image_result" not in st.session_state:
    st.session_state.image_result = None

# === IMAGE UPLOAD ===
uploaded_file = st.file_uploader("📷 Upload a photo of your fridge or food items", type=["jpg", "jpeg", "png", "webp", "avif"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Suggest a Meal"):
        with st.spinner("Analyzing your ingredients..."):

            # Send image to backend
            response = requests.post(
                f"{BACKEND_URL}/process-image",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "image/jpg"
                    )
                }
            )


            if response.status_code == 200:
                data = response.json()
                message = data["history"][-1]["content"]
                st.session_state.chat_history = data["history"]
                st.session_state.image_result = message
            else:
                st.error(f"Backend error: {response.text}")


    if st.session_state.image_result:
        st.success("Here's what you could make:")
        st.markdown(st.session_state.image_result)


    # === CHAT SECTION ===
    if st.session_state.image_result:
        st.markdown("---")
        st.subheader("💬 Ask something about the ingredients or recipe")

        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "system":
                continue
            if msg["role"] == "user" and i == 0 or i == 1:
                continue
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


        if prompt := st.chat_input("Ask something..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.spinner("Thinking..."):
                chat_response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "messages": st.session_state.chat_history[:-1],  # history until now
                        "user_message": prompt
                    }
                )

            if chat_response.status_code == 200:
                answer = chat_response.json()["response"]
                with st.chat_message("ai"):
                    st.markdown(answer)
                st.session_state.chat_history.append({"role": "ai", "content": answer})
            else:
                st.error("Chat backend error: " + chat_response.text)

else:
    st.info("Please upload an image and click the button to get started.")
    st.session_state.chat_history = []
    st.session_state.image_result = None

# === FOOTER ===
st.markdown("---")
st.caption("Built with ❤️ for HCIAI")
