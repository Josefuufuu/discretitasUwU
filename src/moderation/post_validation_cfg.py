from collections.abc import Iterable
from html import escape as html_escape
from typing import Tuple, Any
from textx import metamodel_from_str, TextXSyntaxError

GRAMMAR = r'''
Post:
    text=Text
    hashtag_list=HashtagList?
    link_list=LinkList?
;

HASHTAG: /#[A-Za-z0-9_]+/;
MENTION: /@[A-Za-z0-9_]+/;
LINK: /(https?:\/\/\S+)/;
WORD: /[A-Za-z]+[A-Za-z0-9]*/;
NUMBER: /[0-9]+/;
EMOJI: /[\U0001F300-\U0001FAFF]/;
FORMULABODY: /[^$]+/;

Text:
    parts+=Part+
;

HashtagList:
    hashtags+=Hashtag+
;

LinkList:
    links+=Link+
;

Part: Mention | Enhancement | Word | Number | Emoji;

Enhancement:
      Italic
    | Bold
    | Underline
    | AltFont
    | UpsideDown
    | Formula
;

Italic:      '-'  content=Inline '-' ;
Bold:        '*'  content=Inline '*' ;
Underline:   '_'  content=Inline '_' ;
AltFont:     '//' content=Inline '//' ;
UpsideDown:  '~'  content=Inline '~' ;
Formula:     '$'  expr=FORMULABODY '$' ;

Inline: (Word | Number | Emoji | Mention)+;

Hashtag: token=HASHTAG;
Link:    token=LINK;
Mention: token=MENTION;
Word:    token=WORD;
Number:  token=NUMBER;
Emoji:   token=EMOJI;

Space: /[ \t\r\n]+/;
ignore: Space;
'''

_mm = metamodel_from_str(GRAMMAR)

def parse_post(text: str):
    return _mm.model_from_str(text)

def validate_post(text: str) -> Tuple[bool, Any]:
    try:
        model = parse_post(text)
        return True, model
    except TextXSyntaxError as e:
        return False, e

_flip_map = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
    "ɐqɔpǝɟƃɥᴉɾʞʅɯuodbɹsʇnʌʍxʎz∀qƆpƎℲפHΙſʞ⅂WNOԀΌᴚS⊥∩ΛMXʎZ⇂ᘔƐㄣϛ9ㄥ860"
)

def _render_inline(inline_parts) -> str:
    if hasattr(inline_parts, 'parts'):
        inline_parts = inline_parts.parts

    if inline_parts is None:
        inline_parts = []
    elif isinstance(inline_parts, (str, bytes)):
        inline_parts = [inline_parts]
    elif not isinstance(inline_parts, Iterable):
        inline_parts = [inline_parts]

    out = []
    for p in inline_parts:
        name = p.__class__.__name__
        if name in {'Word', 'Number', 'Emoji', 'Mention'}:
            out.append(p.token)
        else:
            out.append(str(p))
    return ''.join(out)

def render_preview(model) -> str:
    rendered = []
    for part in model.text.parts:
        name = part.__class__.__name__
        if name in {'Word', 'Number'}:
            rendered.append(part.token)
        elif name == 'Emoji':
            rendered.append(part.token)
        elif name == 'Mention':
            rendered.append(part.token)
        elif name == 'Italic':
            rendered.append(f"*{_render_inline(part.content)}*")
        elif name == 'Bold':
            rendered.append(f"**{_render_inline(part.content)}**")
        elif name == 'Underline':
            rendered.append(f"<u>{_render_inline(part.content)}</u>")
        elif name == 'AltFont':
            rendered.append(f"<span style='font-family:monospace'>{_render_inline(part.content)}</span>")
        elif name == 'UpsideDown':
            txt = _render_inline(part.content)
            rendered.append(txt.translate(_flip_map)[::-1])
        elif name == 'Formula':
            rendered.append(f"$ {html_escape(part.expr)} $")
        else:
            rendered.append(str(part))

    if getattr(model, 'hashtag_list', None):
        rendered.append("\n\n**Hashtags:** ")
        rendered.append(' '.join(h.token for h in model.hashtag_list.hashtags))

    if getattr(model, 'link_list', None):
        rendered.append("\n\n**Links:** ")
        rendered.append(' '.join(l.token for l in model.link_list.links))

    return ''.join(rendered)

if __name__ == "__main__":
    txt = "Hi -italic- *bold* _under_ $a^2+b^2=c^2$ @alice #math https://test.com"
    ok, result = validate_post(txt)
    if ok:        
        print("✅ Post válido")
        print(render_preview(result))
    else:
        print("❌ Post inválido:", result)
