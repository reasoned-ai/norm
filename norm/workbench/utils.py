from typing import Dict
from dash.dependencies import MATCH


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
) -> Dict[str, str]:
    return dict(
        index=module_name,
        type=name
    )


def match_id(name: str) -> Dict:
    return dict(
        type=name,
        index=MATCH
    )


def tid(
    module_name: str,
    name: str
) -> str:
    return r'\{\"index\"\:\"' + module_name + r'\"\,\"type\"\:\"' + name + r'\"\}'
