import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Recipe Manager", page_icon="🍳", layout="wide")

st.title("Recipe Manager")
st.markdown("full-stack app")

tab1, tab2 = st.tabs(["📚 View Recipes", "➕ Add New Recipe"])

# ---- Tab 1: View recipes ----

with tab1:
    st.header("Your Recipes")
    try:
        response = requests.get(f"{API_URL}/recipes/")
        if response.status_code == 200:
            recipes = response.json()
            if not recipes:
                st.info("No Recipes Found. Please add one!")
            else:
                for recipe in recipes:
                    with st.expander(f"🍽️ {recipe['title']} (Rating: {recipe['rating']}/5)"):
                        if recipe['image_path']:
                            st.image(f"{API_URL}/{recipe['image_path']}", width=300)
                        st.subheader("Ingredients")
                        st.write(recipe['ingredients'])
                        st.subheader("Instructions")
                        st.write(recipe['instructions'])
        else:
            st.error("Failed to fetch Recipes")
    except requests.exceptions.ConnectionError:
        st.error("Connection Error")


# ----- Tab 2: Add recipe -----

with tab2:
    st.header("Add a new Recipe")

    with st.form("recipe_form", clear_on_submit=True):
        title = st.text_input("Recipe Title*")
        ingredients = st.text_area("Ingredients*")
        instructions = st.text_area("Instructions*")
        rating = st.slider("Rating", 1, 5, 3)
        uploaded_file = st.file_uploader("Upload a Recipe Image", type=["jpg", "jpeg", "png", "webp"])

        submitted = st.form_submit_button("Save Recipe")

        if submitted:
            if not title or not ingredients or not instructions:
                st.error("Please fill in all required fields!")
            else:
                recipe_data = {
                    "title": title,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "rating": rating
                }

                res = requests.post(f"{API_URL}/recipes/", json=recipe_data)

                if res.status_code == 201:
                    new_recipe = res.json()
                    recipe_id = new_recipe["id"]
                    st.success(f"Recipe '{title}' created successfully!")

                    if uploaded_file is not None:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}  # type: ignore
                        img_res = requests.post(f"{API_URL}/recipes/{recipe_id}/image", files=files)

                        if img_res.status_code == 200:
                            st.success("Image uploaded successfully!")
                        else:
                            st.error(f"Image upload failed: {img_res.text}")
                else:
                    st.error(f"Failed to create recipe: {res.text}")