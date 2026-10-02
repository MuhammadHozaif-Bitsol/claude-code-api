import os

from client import add_user_message, chat
from evaluator import PromptEvaluator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "dataset.json")
JSON_OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")
HTML_OUTPUT_FILE = os.path.join(BASE_DIR, "output.html")


PROMPT_TEMPLATE = """
Create a compact, one-day meal plan for the athlete below.

<athlete_info>
- Height (cm): {height}
- Weight (kg): {weight}
- Goal: {goal}
- Dietary restrictions: {restrictions}
</athlete_info>

<nutrition_rules>
1. Calories: estimate maintenance with Mifflin-St Jeor (10 x kg + 6.25 x cm - 125 + 5,
   assuming age 25) times 1.55 for training, or 1.75 for endurance/marathon training.
   - Fat loss: 500-750 kcal below maintenance
   - Muscle gain: 300-500 kcal above maintenance
   - Other goals: at maintenance
2. Protein per kg of body weight:
   - Fat loss: 1.8-2.2 g/kg
   - Muscle gain: at least 2.4 g/kg
   - Endurance: 1.4-1.6 g/kg
3. Carbs: 6-8 g/kg for endurance goals; fill remaining calories with carbs and fat otherwise.
4. Show your calculated daily calories, protein, carbs, and fat. Make the meals add up to these totals.
</nutrition_rules>

<format_rules>
1. Exactly 4 meals/snacks, each with a time of day
2. Make one meal pre-workout and one post-workout, and label them
3. Every food has an exact portion in grams or ml
4. Every meal shows its calories, protein, carbs, and fat
5. Only foods that fit the dietary restrictions
6. Keep it compact: no extra tips, shopping lists, or explanations
</format_rules>

Here is an example of the expected format for a different athlete:

<sample_input>
- Height (cm): 160
- Weight (kg): 60
- Goal: improve sprint speed
- Dietary restrictions: nut allergy
</sample_input>

<sample_output>
# One-Day Meal Plan: Sprint Speed, Nut-Free

## Daily Targets
- Calories: 2,290 kcal (maintenance)
- Protein: 108 g (1.8 g/kg)
- Carbs: 300 g
- Fat: 73 g

## Meals

### Breakfast (7:00 AM)
- Rolled oats: 80 g
- Greek yogurt: 200 g
- Mixed berries: 150 g
- Honey: 15 g
546 kcal | P 30 g | C 75 g | F 14 g

### Pre-Workout Snack (11:00 AM)
- Plain bagel: 90 g
- Banana: 120 g
- Turkey slices: 60 g
443 kcal | P 20 g | C 75 g | F 7 g

### Post-Workout Lunch (2:00 PM)
- Chicken breast: 120 g
- White rice (cooked): 250 g
- Mixed vegetables: 150 g
- Olive oil: 15 ml
698 kcal | P 35 g | C 90 g | F 22 g

### Dinner (7:00 PM)
- Salmon fillet: 100 g
- Sweet potato: 250 g
- Broccoli: 150 g
- Olive oil: 10 ml
602 kcal | P 23 g | C 60 g | F 30 g

Total: 2,289 kcal | P 108 g | C 300 g | F 73 g
</sample_output>
"""


def run_prompt(prompt_inputs):
    prompt = PROMPT_TEMPLATE.format(**prompt_inputs)

    messages = []
    add_user_message(messages, prompt)
    return chat(messages)


if __name__ == "__main__":
    # Start low (like 3) to avoid rate limit errors
    evaluator = PromptEvaluator(max_concurrent_tasks=3)
    """
    dataset = evaluator.generate_dataset(
        task_description="Write a compact, concise 1 day meal plan for a single athlete",
        prompt_inputs_spec={
            "height": "Athlete's height in cm",
            "weight": "Athlete's weight in kg",
            "goal": "Goal of the athlete",
            "restrictions": "Dietary restrictions of the athlete",
        },
        output_file=DATASET_FILE,
        num_cases=3,
    )
    """
    results = evaluator.run_evaluation(
        run_prompt_function=run_prompt,
        dataset_file=DATASET_FILE,
        extra_criteria="""
The output should include:
- Daily caloric total
- Macronutrient breakdown
- Meals with exact foods, portions, and timing
""",
        json_output_file=JSON_OUTPUT_FILE,
        html_output_file=HTML_OUTPUT_FILE,
    )
