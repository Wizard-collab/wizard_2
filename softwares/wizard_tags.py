import os


ENV_TAG_KEYS = ["category", "asset", "variant", "stage"]


def get_env_tags() -> list:
    """ Get the tags from the environment variables.
    
    Returns:
        list: A list of tags from the environment variables.
        
    """

    tags = []

    for key in ENV_TAG_KEYS:
        val = os.getenv(f"wizard_{key}_name", "")

        if not val:
            continue

        tags.append(f"{key.upper()}={val}")

    return tags
