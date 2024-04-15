### AI - Powered Recipe Generator

Leveraging OpenAI's ChatGPT4-Turbo and DALLE-3 to generate a detailed step-by-step instruction to go about creating a recipe, given the following parameters:
- Cuisine Preference
- Ingredients
- Dietary Preferences
- Number of Servings

The `generator.py` script incorporates the Streamlit web-app framework to host the Recipe Generator app that allows the User to choose their preferences and generate a unique recipe.

The `Recipe` class in the `generateRecipe.py` script makes calls to `OpenAI's` `ChatGPT4-Turbo and DALLE-3` LLM to generate a detailed step-by-step instructions on how to make the recipe along with the amount of servings required. It also provides information regarding the health benefits of the given recipe.

Once the recipe is generated, the user can save the recipe by clicking on the `Download Recipe` button which saves the information to `recipe.pdf` file.

The `DALLE-3` LLM is leveraged into creating a realistic image of the suggested recipe.

To run and host the app locally, install the various dependencies and libraries as provided in the `requirements.txt` and run the streamlit app using the below command in terminal:  

```
pip install -r requirements.txt
streamlit run generator.py
```

In your browser - go to the below link to access the hosted recipe generator app:
```
http://localhost:8501/
```

The structure of the scripts and files are as follows:

```
├── README.md
├── requirements.txt
├── resources
│   ├── Book Antiqua.ttf
│   └── base_image.png
└── src
    ├── generateRecipe.py
    └── generator.py
```