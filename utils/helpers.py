import re
import urllib.parse

def valid_gif_url_in_text(text: str) -> bool:
    """
    Returns True if at least one URL in the text either ends with .gif 
    or is from a known GIF hosting service (e.g. tenor.com, giphy.com).
    """
    urls = re.findall(r'https?://\S+', text)
    known_gif_domains = ['tenor.com', 'giphy.com']
    for url in urls:
        cleaned_url = url.rstrip('.,;!?)')
        parsed_url = urllib.parse.urlparse(cleaned_url)
        if parsed_url.scheme in ('http', 'https'):
            if parsed_url.path.lower().endswith('.gif'):
                return True
            if any(domain in parsed_url.netloc.lower() for domain in known_gif_domains):
                return True
    return False

def get_emoji_str(emoji):
    """
    Standardizes the string representation of an emoji.
    """
    import discord  # Local import to avoid circular dependency issues.
    if isinstance(emoji, str):
        return emoji
    elif isinstance(emoji, (discord.PartialEmoji, discord.Emoji)):
        return f"<:{emoji.name}:{emoji.id}>" if emoji.id else emoji.name
    return str(emoji)

def censor(message):
    """
    Replace non-space characters with '*' in message.content
    """
    return ''.join('*' if not char.isspace() else char for char in message.content)
