import re


MENTION_RE = re.compile(r'@\w+')
HASHTAG_RE = re.compile(r'#\w+')
URL_RE = re.compile(r'(https?://\S+)')


EMOJI_RE = re.compile(
    r'[\u2600-\u27BF'          
    r'\U0001F300-\U0001F5FF'   
    r'\U0001F600-\U0001F64F'   
    r'\U0001F680-\U0001F6FF'   
    r'\U0001F1E0-\U0001F1FF'   
    r'\U0001F900-\U0001F9FF'   
    r'\U0001FA70-\U0001FAFF'   
    r']+'
)

TOKEN_RE = re.compile(
    r'(https?://\S+)|(@\w+)|(#\w+)|([\u2600-\u27BF'
    r'\U0001F300-\U0001F5FF\U0001F600-\U0001F64F'
    r'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF'
    r'\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF])|([^\s]+)'
)

def extract_mentions(text):
    return MENTION_RE.findall(text)

def extract_hashtags(text):
    return HASHTAG_RE.findall(text)

def extract_urls(text):
    return URL_RE.findall(text)

def extract_emojis(text):
    return EMOJI_RE.findall(text)


def normalize_text(text):
    lowered = text.lower()
    collapsed = re.sub(r'\s+', ' ', lowered)
    return collapsed.strip()

def tokenize(text):
    tokens = []
    for m in TOKEN_RE.finditer(text):
        for g in m.groups():
            if g:  
                tokens.append(g)
                break
    return tokens

def extract_all(text):
    
    return {
        "mentions": extract_mentions(text),
        "hashtags": extract_hashtags(text),
        "urls": extract_urls(text),
        "emojis": extract_emojis(text),
        "tokens": tokenize(text),
        "normalized": normalize_text(text),
    }