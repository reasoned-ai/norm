from typing import Dict, Union
from dash.dependencies import MATCH
from norm.config import ENABLE_PATTERN_MATCH


def panel_style(vw: int):
    return dict(
        height='91.4vh' if vw > 2000 else '78vh',
        width='100%'
    )


label_style = {
    'fontSize': '1.2em'
}


def mid(
    module_name: str,
    name: str
) -> Union[str, Dict[str, str]]:
    if ENABLE_PATTERN_MATCH:
        return dict(
            index=module_name,
            type=name
        )
    else:
        return name


def match_id(name: str) -> Union[str, Dict]:
    if ENABLE_PATTERN_MATCH:
        return dict(
            type=name,
            index=MATCH
        )
    else:
        return name


def tid(
    module_name: str,
    name: str
) -> str:
    if ENABLE_PATTERN_MATCH:
        return r'\{\"index\"\:\"' + module_name + r'\"\,\"type\"\:\"' + name + r'\"\}'
    else:
        return name
