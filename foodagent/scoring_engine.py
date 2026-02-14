from typing import Dict, Optional, List


def compute_hidden_gem_score(place: Dict) -> float:
    """
    Hidden Gem Score Logic:
    - High rating
    - Not too many reviews
    """
    rating = place.get("rating", 0)
    user_ratings_total = place.get("user_ratings_total", 0)

    rating_score = rating * 2

    if user_ratings_total < 200:
        review_factor = 3
    elif user_ratings_total < 500:
        review_factor = 1
    else:
        review_factor = -2

    score = rating_score + review_factor
    return round(max(0, min(10, score)), 2)


def compute_night_score(place: Dict) -> float:
    """
    Night Spot Score Logic:
    - Is open now
    - Closes late (after 11 PM)
    """
    opening_hours = place.get("opening_hours", {})

    if not opening_hours.get("open_now"):
        return 0.0

    periods = opening_hours.get("periods", [])

    # Check if closes after 11 PM
    for period in periods:
        close_time = period.get("close", {})
        time_str = close_time.get("time", "")

        if time_str:
            try:
                hour = int(time_str[:2])
                if hour >= 23 or hour < 6:  # After 11 PM or early morning
                    return 5.0
            except (ValueError, IndexError):
                continue

    return 1.0


def compute_hygiene_score(reviews: Optional[List[Dict]]) -> float:
    """
    Hygiene Score using NLP on reviews
    """
    if not reviews:
        return 5.0  # Default middle score

    positive_keywords = [
        "clean", "hygienic", "fresh", "well maintained",
        "spotless", "immaculate", "organized", "neat"
    ]

    negative_keywords = [
        "dirty", "smell", "flies", "food poisoning",
        "unhygienic", "messy", "unkempt", "stale", "unclean"
    ]

    score = 0

    for review in reviews:
        review_text = review.get("text", "").lower()

        for keyword in positive_keywords:
            if keyword in review_text:
                score += 1

        for keyword in negative_keywords:
            if keyword in review_text:
                score -= 2

    # Normalize score to 0-10
    score = max(0, min(10, score))
    return round(score, 2)


def compute_veg_confidence(place: Dict, reviews: Optional[List[Dict]]) -> float:
    """
    Veg / Non-Veg Detection
    Check place types and review keywords
    """
    veg_keywords = [
        "pure veg", "vegetarian", "vegan", "eggless",
        "jain", "veg only", "plant-based"
    ]

    non_veg_keywords = [
        "meat", "chicken", "seafood", "fish", "non-veg",
        "mutton", "beef", "halal"
    ]

    place_types = place.get("types", [])
    name = place.get("name", "").lower()

    veg_score = 0
    non_veg_score = 0

    # Check place name for veg keywords
    for keyword in veg_keywords:
        if keyword in name:
            veg_score += 3

    # Check reviews
    if reviews:
        for review in reviews:
            review_text = review.get("text", "").lower()

            for keyword in veg_keywords:
                if keyword in review_text:
                    veg_score += 1

            for keyword in non_veg_keywords:
                if keyword in review_text:
                    non_veg_score += 2

    # Calculate confidence
    total = veg_score + non_veg_score
    if total == 0:
        return 50.0  # No evidence, neutral

    veg_confidence = (veg_score / total) * 100
    return round(veg_confidence, 2)


def generate_label(hidden_gem: float, night: float, hygiene: float, veg: float) -> str:
    """
    Generate a descriptive label based on scores
    """
    if hidden_gem >= 8 and hygiene >= 7:
        return "Local Favorite"
    elif night >= 4:
        return "Night Spot"
    elif veg >= 80:
        return "Vegetarian Paradise"
    elif hygiene >= 8.5:
        return "Hygiene Champion"
    elif hidden_gem >= 7:
        return "Hidden Gem"
    else:
        return "Good Choice"


def generate_summary(place: Dict, hidden_gem: float, night: float, hygiene: float) -> str:
    """
    Generate a human-readable summary
    """
    parts = []

    if hidden_gem >= 8:
        parts.append("Highly rated by locals")

    if hygiene >= 7:
        parts.append("good hygiene standards")

    if night >= 4:
        parts.append("best after 9PM")

    opening_hours = place.get("opening_hours", {})
    if opening_hours.get("open_now"):
        parts.append("currently open")

    if not parts:
        rating = place.get("rating", 0)
        if rating >= 4:
            parts.append(f"Well-rated restaurant ({rating}★)")
        else:
            parts.append("Worth checking out")

    summary = ", ".join(parts) + "."
    return summary.capitalize()
