import os
import time
import json
from openai import OpenAI, OpenAIError

class Recipe:
    def __init__(self):
        self.behavior = self._system_behavior
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.recipe_model = "gpt-4-turbo"
        self.recipe_image_model = "dall-e-3"

    @property
    def _system_behavior(self):
        """Defines the LLM's System Behavior/Role.

        Returns:
            role (str): Returns the system behavior.
        """        
        role = """
        You are an experienced chef who is renowned for making popular and esquisite recipes from all around the world.
        Your tasked with generating a recipe given the:
        - Ingredients.
        - Dietary preference such as for example: vegetarian, gluten-free, low-carb, etc.
        - The number of servings (to generate the appropriate amount of ingredients required to make the dish).

        You are required to carefully analyse the above user input and return the required recipe content.
        You do not provide an acknowledgement of the query.

        NOTE:
        It is very important that you take into consideration the dietary preferences and make sure that you do not include any ingredients.

        Maintain a Concise, and Humorous Tone: Your responses should be easy to understand to a wide range of audiences. Dont make niche references, or use English that a native-speaker would not understand. Make use of markdown and emojis to organize and make information engaging.
        When you have gathered enough information from the user, present them with a recipe which has 3-7 steps, and 4-10 ingredients. Remember people usually prefer shorter recipes. The recipe should be formatted as: 
        
        The recipe should have 3-7 steps, and 4-10 ingredients. Remember people usually prefer shorter recipes. 
        Formatted as: 

        <A creative, engaging title with adjectives (not too long)>
        **Ingredients**: <a bullet point, list of ingredients with US measurements (per number of servings requested by user)>
        **Instructions**: <step-by-step including the need to preheat ovens, or prepare materials>
        **Health Information**: <a line or two, about why this recipe promotes longevity>
        """
        return role

    def generateRecipe(self, prompt):
        """Creates a detailed step-by-step instruction on how to go about making the recipe,
        Given the user prompt containing the cuisine, ingredients, dietary prefresences and the serving size.

        Args:
            prompt (str): User message to generate the recipe.

        Returns:
            recipe_instructions (str): Instructions to create the recipe along with information on the serving sizes and health benefits.
        """        
        max_retries = 3  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                client = OpenAI(
                    api_key=self.api_key
                )
                response = client.chat.completions.create(
                    model=self.recipe_model,
                    temperature=0.6,
                    messages=[
                        {
                            "role": "system",
                            "content": f"{self.behavior}"
                        },
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}]
                        }
                    ],
                    max_tokens=2048
                )
                
                recipe_instructions = response.choices[0].message.content
                return recipe_instructions
            except OpenAIError as e:
                print(f"Error occurred: {e}")
                print("Retrying...")
                retries += 1
                time.sleep(1)  # Delay between retries

    def generateRecipeImage(self, prompt):
        """Creates an image of the given recipe that includes the given ingredients.

        Args:
            prompt (str): Instructions on how to make the recipe.

        Returns:
            image_url (str): Recipe Image URL.
        """        
        max_retries = 3  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                client = OpenAI(
                    api_key=self.api_key
                )
                response = client.images.generate(
                            model=self.recipe_image_model,
                            prompt=prompt,
                            size="1024x1024",
                            quality="standard",
                            n=1,
                        )
                
                image_url = response.data[0].url
                return image_url
            except OpenAIError as e:
                print(f"Error occurred: {e}")
                print("Retrying...")
                retries += 1
                time.sleep(1)  # Delay between retries

    def generate(self, cuisines, ingredients, preferences, servings):
        """Generates the recipe by making calls to OpenAI's ChatGPT4-Turbo to create a detailed instructions
        given the cuisine, ingredients, dietary prefrences, number of servings. It also makes calls to OpenAI's Dalle-3
        to generate an image of the given recipe.

        Args:
            cuisines (List(str)): List of cuisines.
            ingredients (List(str)): List of ingredients.
            preferences (List(str)): List of dietary preferences.
            servings (int): Number of servings.

        Returns:
            recipe_instructions (str): Instructions on how to make the recipe.
            recipe_image_url: Image URL on how the recipe would look like.
        """        
        user_message = f"""
        I am interested in making a {cuisines} recipe.
        My dietary preferences are as follows: {preferences}.
        I want the recipe to have the following ingredients: {ingredients}
        The desired number of servings is = {servings}.
        
        Please generate a recipe and provide a step-by-step instruction to go about making it.
        Make sure to provide the right amount of serving size for each of the ingredients I desire to be present in the recipe.
        Make sure the recipe sticks to my dietary preferences.
        """

        recipe_instructions = self.generateRecipe(user_message)
        image_prompt = f"You are an experienced artist that showcases extravagant images of recipes prepared by world-class chefs. Generate an image for the following recipe: {recipe_instructions}"
        recipe_image_url = self.generateRecipeImage(image_prompt)
        return recipe_instructions, recipe_image_url