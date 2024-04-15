from fpdf import FPDF
import streamlit as st
from generateRecipe import Recipe
from PIL import Image, ImageDraw, ImageFont

## Global variables containing error messages and information for pre-defined cuisines, ingredients, dietary prefrences
ERROR_STRING = "Oops! Something went wrong. We're sorry, but our server is currently experiencing technical difficulties. Please try again later. If the issue persists, feel free to contact support for assistance. Thank you for your understanding."
PREDEFINED_CUSINES = ["Indian", "Italian", "Mexican", "Chinese", "Thai", "Mediterranean", "Greek", "American"]
PREDEFINED_INGREDIENTS = ["Tomato", "Onion", "Garlic", "Chicken", "Beef"]
DIETARY_PREFRENCES = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto", "Nut-Free", "Soy-Free", "Sugar-Free", "Low-Fat", "Organic"]

def getRecipe(cuisines, ingredients, preferences, servings):
    """Makes calls to OpenAI's LLMs (ChatGPT4-Turbo and DALLE-3) to generate a detailed step-by-step instruction
    on how to make the recipe and to create an image of the recipe.

    Args:
        cuisines (List(str)): List of cuisines.
        ingredients (List(str)): List of ingredients.
        preferences (List(str)): List of dietary preferences.
        servings (int): Number of servings.

    Returns:
        recipe_instructions (str): Instructions on how to make the recipe.
        recipe_image_url: Image URL on how the recipe would look like.
    """    
    recipe_obj = Recipe()
    instructions, recipe_image_url = recipe_obj.generate(cuisines, ingredients, preferences, servings)
    if instructions is None:
        return ERROR_STRING
    return f"Here's the {', '.join(cuisines)} recipe for {', '.join(ingredients)} with {', '.join(preferences)} preferences for {servings} servings. \n{instructions}", recipe_image_url

def sync_generate_image(diary):
    out_path = "./recipe.pdf"
    # if (len(diary) < 500):
    #     diary += ' ' * (len(diary) - 500)
    base = Image.open("../resources/base_image.png").convert('RGBA')

    # Define a border size
    border = 200

    # Calculate the new size for the txt image
    txt_size = (base.size[0] - 2*border, base.size[1] - 2*border)
    txt = Image.new('RGBA', txt_size, (255,255,255,0))

    d = ImageDraw.Draw(txt)

    min_font, max_font = 1, 1000  # Define an initial min and max font size

    # Implement binary search for optimal font size
    while min_font < max_font - 1:
        font_size = (min_font + max_font) // 2
        fnt = ImageFont.truetype('../resources/Book Antiqua.ttf', font_size)

        # Calculate line breaks manually and only split lines when they exceed the maximum width
        lines = diary.splitlines(True)
        total_height = 0
        for line in lines:
            if line.strip() == "":
                total_height += font_size  # Adding the height of one line
                continue
            words = line.split(" ")
            new_line = ""
            line_height = 0
            for word in words:
                if new_line != "":
                    word = " " + word
                size = d.textsize(new_line + word, font=fnt)
                if size[0] <= txt_size[0]:  # If it fits, add the word to line
                    new_line += word
                    line_height = size[1]
                else:  # Otherwise, create a new line
                    total_height += line_height
                    new_line = word.strip()
            total_height += line_height

        if total_height <= txt_size[1]:  # Check if the text fits vertically in the image
            min_font = font_size
        else:
            max_font = font_size

    # Use the largest font size that fits
    fnt = ImageFont.truetype('../resources/Book Antiqua.ttf', min_font)

    # Draw the text line by line
    lines = diary.splitlines(True)
    y_text = 0
    for line in lines:
        if line.strip() == "":
            y_text += font_size  # Adding the height of one line
            continue
        words = line.split(" ")
        new_line = ""
        for word in words:
            if new_line != "":
                word = " " + word
            size = d.textsize(new_line + word, font=fnt)
            if size[0] <= txt_size[0]:  # If it fits, add the word to line
                new_line += word
            else:  # Otherwise, draw the line and start a new one
                width, height = d.textsize(new_line, font=fnt)
                d.text((0, y_text), new_line, font=fnt, fill=(0,0,0,255))  # x coordinate is 0 for left alignment
                y_text += height
                new_line = word.strip()
        # Draw the last line
        width, height = d.textsize(new_line, font=fnt)
        d.text((0, y_text), new_line, font=fnt, fill=(0,0,0,255))  # x coordinate is 0 for left alignment
        y_text += height

    # We paste the txt image on top of the base image at the border offset
    base.paste(txt, (border, border), txt)

    base.save(out_path)


def app():
    """A Streamlit app that is used to host the Recipe App and allow the user to generate unique recipes
    based on their choice of cuisine, ingredients, dietary prefrences, serving sizes.
    It is used to also display the image of how the recipe would look like.
    """    
    ## Display the title of the APP
    st.title("Recipe Generator")

    recipe = None
    with st.form("recipe_form"):
        ## Allow the customer to choose the Cuisine from a pre-define list or enter their own choice of Cuisines.
        st.subheader("Select Cuisine")
        cuisines = [cuisine for cuisine in st.multiselect("Predefined Cuisine", PREDEFINED_CUSINES, placeholder="Choose your preferred cuisine")]
        custom_cuisine = st.text_input("Enter custom cuisine")
        if custom_cuisine:
            cuisines.append(custom_cuisine)

        ## Allow the customer to choose the Ingredients from a pre-define list or enter their own choice of Ingredients.
        st.subheader("Select Ingredients")
        ingredients = [ingredient for ingredient in st.multiselect("Predefined Ingredients", PREDEFINED_INGREDIENTS, placeholder="Choose the ingredients")]
        custom_ingredient = st.text_input("Enter custom ingredient")
        if custom_ingredient:
            ingredients.append(custom_ingredient)

        ## Allow the customer to choose the Dietary Preferences from a pre-define list or enter their own choice of Dietary Preferences.
        st.subheader("Dietary Preferences")
        preferences = [preference for preference in st.multiselect("Dietary Preferences", DIETARY_PREFRENCES, placeholder="Choose your dietary preference(s)")]
        custom_dietary_preferences = st.text_input("Enter custom dietary preferences")
        if custom_dietary_preferences:
            DIETARY_PREFRENCES.append(custom_dietary_preferences)

        ## Allow the customer to choose the amount of the Serving Size for the recipe
        st.subheader("Serving Size")
        servings = st.number_input("Number of Servings", min_value=1, value=4)
        
        # Initialize a session state variable to keep track of whether the form has been submitted
        if "submitted" not in st.session_state:
            st.session_state.submitted = False
        submitted = st.form_submit_button("Generate Recipe")

        if submitted:
            st.session_state.submitted = True
            recipe, image_url = getRecipe(cuisines, ingredients, preferences, servings)
            ## Display the instructions on how to make the recipe
            st.success(recipe)

            # Display the recipe image if a valid URL is provided
            if image_url:
                st.image(image_url, caption="Recipe Image", use_column_width=True)

    ## Store the recipe to a pdf and allow the customer to download it!
    if recipe:
        sync_generate_image(
            diary=recipe
        )
        st.success("Click the button below to download the recipe!")
        with open("recipe.pdf", "rb") as f:
            st.download_button("Download Recipe", f, "recipe.pdf")

if __name__ == "__main__":
    app()