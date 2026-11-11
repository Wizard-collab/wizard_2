import os


ENV_TAG_KEYS = ["category", "asset", "variant", "stage"]


def get_env_tags() -> list:
    """ Get the tags from the environment variables.
    
    Returns:
        list: A list of tags from the environment variables.
        
    """

    tags = []

    category = os.getenv("wizard_category_name", "")
    asset = os.getenv("wizard_asset_name", "")
    variant = os.getenv("wizard_variant_name", "main")
    stage = os.getenv("wizard_stage_name", "")

    if not category or not asset or not stage:
        return tags

    if category:
        tags.append(f"CATEGORY={category}")
    if asset:
        tags.append(f"ASSET={asset}_{variant}")  # Varianted asset tag
    if variant:
        tags.append(f"VARIANT={variant}")
    if stage:
        tags.append(f"STAGE={stage}")

    return tags


def remove_env_tags(tags: list):
    """ Remove tags that are already present in the environment variables from the given list of tags. 
    
    Args:
        tags (list): A list of tags to be cleaned up.

    """

    for tag in tags:
        key = tag.split("=")[0].lower()

        if key in ENV_TAG_KEYS:
            tags.remove(tag)


def read_tags(tag_string: str) -> list:
    """ Read a string of tags and return a list of tags.

    Args:
        tag_string (str): Comma-separated string of tags.

    Returns:
        list: A list of tags.
    """

    return [tag.strip() for tag in tag_string.split(",") if tag.strip()]


def sorted_tags(tags: list) -> list:
    """ Sort a list of tags based.
    It put first the environment tags, then the other tags in alphabetical order.

    Args:
        tags (list): A list of tags to be sorted.

    Returns:
        list: A sorted list of tags.
    """

    def sort_key(tag):
        """
        Define the sorting key for each tag.
        """
        # 
        key = tag.split("=")[0].lower()
        index = len(ENV_TAG_KEYS)  # Default index for non-environment tags
        if key in ENV_TAG_KEYS:
            index = ENV_TAG_KEYS.index(key)

        return (
            index,
            tag.lower()
        )

    return sorted(tags, key=sort_key)


def generate_tags(tags: list = None) -> str:
    """ Generate a string of tags from the given list of tags.
    It cleans up the tags by removing any residual environement tags.
    
    Args:
        tags (list): A list of tags to be cleaned up and returned as a string.

    Workflow:
        1. Clean up the tags by removing any residual environment tags.
        2. Get the tags from the environment variables.
        3. Combine the environment tags with the cleaned-up tags.
        4. Return the combined tags as a string.
    
    Returns:
        str: A string of tags.
        
    """

    if tags is None:
        tags = []

    _tags = tags.copy()  # We should not modify the original list of tags
    remove_env_tags(_tags)
    env_tags = get_env_tags()

    all_tags = env_tags + _tags
    deduplicated_tags = list(set(all_tags))  # Remove duplicates


    return ",".join(sorted_tags(deduplicated_tags))  # Sort the tags and return as a string
