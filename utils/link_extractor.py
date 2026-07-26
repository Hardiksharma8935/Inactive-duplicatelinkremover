import re

# Matches standard t.me, telegram.me, and joinchat variants
TELEGRAM_LINK_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/(?:joinchat/|\+)?([\w\d_-]+)",
    re.IGNORECASE
)

def extract_telegram_links(text: str) -> list[str]:
    if not text:
        return []
    matches = TELEGRAM_LINK_REGEX.findall(text)
    # Normalize by converting to lowercase to ensure case-insensitivity
    return [match.lower() for match in matches]
  
