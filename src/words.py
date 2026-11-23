"""The app's words, in the phone's language: from its translations
(`i18n/`), which the phone reads; and the page's own words, which its
markup names (`data-t`, `data-t-placeholder`), put in."""

from wit_world.imports import dom, words


def t(key: str, **args: int | str) -> str:
    """The word `key`, given `args` by their names."""
    given = [
        (name, words.Arg_Number(float(value)) if isinstance(value, int) else words.Arg_Text(value))
        for name, value in args.items()
    ]
    return words.word(key, given)


def translate(scope: int) -> None:
    """The words the markup under `scope` names, put in: each `data-t` as an
    element's text, each `data-t-placeholder` as its placeholder."""
    for element in dom.query_all(scope, "[data-t]"):
        dom.set_text(element, t(dom.get_attribute(element, "data-t") or ""))
    for element in dom.query_all(scope, "[data-t-placeholder]"):
        key = dom.get_attribute(element, "data-t-placeholder") or ""
        dom.set_attribute(element, "placeholder", t(key))
