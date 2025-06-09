import time
import random


def load_profiles():
    """Reads reference profiles from a text file and returns a list of dictionaries."""
    profiles = []
    with open("reference_profiles.txt", "r") as file:
        current_profile = {}
        collecting_description = False

        for line in file:
            line = line.strip()

            # Detect the start of a new profile
            if line.startswith("# Group Name:"):
                if current_profile:
                    profiles.append(current_profile)
                current_profile = {"name": line.split(":")[1].strip(), "description": ""}
                collecting_description = False

            # Convert the score pattern string into integers
            elif line.startswith("# Score Pattern:"):
                scores = line.split(":")[1].strip()
                current_profile["pattern"] = [int(x) for x in scores.split(",")]

            # Next lines are part of the description
            elif line.startswith("# Description:"):
                collecting_description = True

            # Skip comment lines or empty lines
            elif line.startswith("#") or line == "":
                continue

            # Collect multiline description
            elif collecting_description:
                current_profile["description"] += line + "\n"

        if current_profile:
            profiles.append(current_profile)
    return profiles


def find_age_group(age, age_data):
    """Returns the age group dictionary matching the user's age."""
    for entry in age_data:
        group = entry["group"]
        if "–" in group:
            start, end = map(int, group.split("–"))
            if start <= age <= end:
                return entry
        elif "+" in group:
            lower = int(group.replace("+", ""))
            if age >= lower:
                return entry
    return None


# Survey questions — designed to probe beliefs on free will and determinism
questions = [
    "People are always capable of choosing differently, no matter their past.",
    "Most of our thoughts and actions happen without conscious control.",
    "We are responsible for what we do, even if our choices were influenced.",
    "Our genes and early life experiences shape who we become more than our choices.",
    "Understanding someone’s past can reduce how much we blame them.",
    "Even when we think we’re choosing freely, our brain has already made the decision.",
    "No one is truly free — we are shaped by forces we can’t control.",
    "Moral responsibility doesn’t depend on whether we have free will.",
    "Free will and determinism can both be true at the same time.",
    "Our choices are more automatic than we like to admit."
]

# Final reflections — one will be shown at random to prompt deeper thought
reflections = [
    "🧠 Reflection: Do your answers reflect your beliefs — or the world you've been shaped by?",
    "🧭 Consider this: If you answered the same questions tomorrow, would your answers change?",
    "🔍 Question: Are your choices really yours, or are they part of a larger pattern you’re only starting to notice?",
    "🌀 Thought: What does it mean to be accountable, if our choices are shaped before we make them?",
    "🧠 Nietzsche: 'In every real man, a child is hidden that wants to play.' What part of your answers felt instinctive?",
    "🧬 Sapolsky: 'We are biology. That's not a reductionist view, it's the most wondrous one.' How much of your belief in control is grounded in your biology?",
    "🕰️ Consider this: If you rewound the tape of your life, would you really act differently?"
]


def main():
    """Main logic for survey interaction, analysis, and results display."""
    print("\n" + "="*70)
    print("Are You the Author?".center(70))
    print("="*70)
    
    print("""
    A brief self-reflection survey on human behaviour, free will,
    and the forces that shape our choices.

    You'll be asked 10 short questions. It takes about 5 minutes.

    Let's see where your beliefs place you in the great debate
    between free will — the idea that we control our actions — and determinism,
    which suggests our choices are shaped by biology, how we were raised, and life circumstances.
    """)


    # Get initial user input
    user_input = input("Are you ready? (yes/no): ").strip().lower()
    no_count = 0

    # Keep prompting the user until they agree or exit
    while True:
        if user_input in ["yes", "y"]:
            print("Great! Let's begin.")
            break
        else:
            no_count += 1
            if no_count == 1:
                print("Come on... don't you want to know if you're really in control?")
            elif no_count == 2:
                print("That's fine. But remember — refusing to take the quiz... might not even be your choice to make.")
            else:
                print("Okay, I guess you're not ready. Maybe another time.")
                exit()
            user_input = input("Are you ready? (yes/no): ").strip().lower()

    # Ask for the user's age and validate the input
    while True:
        user_age = input("How old are you? (in years): ").strip()
        try:
            age = int(user_age)
            if 10 <= age <= 120:
                print(f"{age} years of life experience... let's reflect on what you've come to believe.")
                break
            else:
                print("Please enter an age between 10 and 120.")
        except ValueError:
            print("Please enter a valid number like 25.")

    # Ask all survey questions and collect user answers
    answers = []
    for index, question in enumerate(questions):
        while True:
            try:
                # Display the current question
                print(f"\nQ{index+1}: {question}")
                print("How much do you agree?")
                print("[1] Strongly Disagree")
                print("[2] Disagree")
                print("[3] Neutral")
                print("[4] Agree")
                print("[5] Strongly Agree")

                # Get user's score for the question
                response = input("Your answer (1-5): ").strip()
                score = int(response)
                if 1 <= score <= 5:
                    answers.append(score)
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a number like 1, 2, 3, 4, or 5.")

    # Simulate a short pause before results
    print("\nProcessing your results...")
    time.sleep(2)

    # Load profiles from file and compare them to user's answers
    profiles = load_profiles()
    best_match = None
    lowest_difference = float('inf')  # Start with the largest possible number

    for profile in profiles:
        # Calculate the total difference between user answers and profile pattern
        total_difference = sum(abs(answers[i] - profile["pattern"][i]) for i in range(len(answers)))
        if total_difference < lowest_difference:
            lowest_difference = total_difference
            best_match = profile

    # Convert the raw score into a % match (lower difference means higher similarity)
    max_possible_difference = len(answers) * 4  # max score difference per question is 4
    match_percent = round(100 - (lowest_difference / max_possible_difference * 100))

    # Display the user's matched belief profile
    print("\n" + "="*70)
    print(f"🔎 Your Belief Profile: {best_match['name']} ({match_percent}% match)" .center(70))
    print("="*70)
    print(best_match["description"])

    # Short pause before age insights
    print("\nProcessing age insights...")
    time.sleep(2)

    # Load data about age-based belief trends
    age_data = []
    with open("age_attitudes.txt", "r") as file:
        next(file)  # Skip CSV header
        for line in file:
            group, fw, ad = line.strip().split(",")  # Split the comma-separated line
            age_data.append({
                "group": group,
                "free_will": fw,
                "anti_determinism": ad
            })

    # Display insights for the user's age group
    user_age_group = find_age_group(age, age_data)
    if user_age_group:
        print("\n📊 Your Age Group Insights:")
        print(f"Age Group: {user_age_group['group']}")
        print(f"{user_age_group['free_will']}% in your group believe in Free Will — regardless of determinism.")
        print(f"{user_age_group['anti_determinism']}% lean against the idea that we're fully shaped by outside forces.")

    # Display one final reflection prompt
    print("\n" + random.choice(reflections))


if __name__ == '__main__':
    main()
