"""Sayfa okuma yardımcıları (plan 0001).

Testler HTML'in etiket yapısına değil, kullanıcının gördüğü içeriğe bakar: tablo hücre metinleri,
bağlantılar, form alanları, metnin rengi. Sayfalar şablonlara taşındığında (refactor) testler
değişmeden kalsın diye.
"""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

_COLOR = re.compile(r"(?:^|;)\s*color\s*:\s*([^;]+)", re.IGNORECASE)
_VOID = set("area base br col embed hr img input link meta source wbr".split())  # kapanışsız


@dataclass
class Page:
    rows: list[list[str]] = field(default_factory=list)  # <td> içeren her satırın hücre metinleri
    headers: list[list[str]] = field(default_factory=list)  # <th> içeren her satırın başlıkları
    links: list[tuple[str, str]] = field(default_factory=list)  # (href, metin)
    options: list[tuple[str, str]] = field(default_factory=list)  # (value, metin)
    fields: list[str] = field(default_factory=list)  # form alanlarının name değerleri
    labels: list[tuple[str, str]] = field(default_factory=list)  # (alanın önündeki metin, name)
    colored: list[tuple[str, str]] = field(default_factory=list)  # (metin, satır içi renk)
    text: str = ""  # görünen metin, boşluklar tekleştirilmiş


def _squash(parts: list[str]) -> str:
    return " ".join("".join(parts).split())


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self._text: list[str] = []
        self._row: list[str] | None = None
        self._head: list[str] = []
        self._cell: list[str] | None = None
        self._last_text = ""  # son boş olmayan metin parçası: bir form alanının etiketi
        self._link: tuple[str, list[str]] | None = None
        self._option: tuple[str, list[str]] | None = None
        self._open: list[tuple[str, str | None]] = []  # açık etiketler ve satır içi renkleri
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: v or "" for k, v in attrs}
        if tag in ("input", "select", "textarea") and attr.get("name"):
            self.page.fields.append(attr["name"])
            self.page.labels.append((self._last_text, attr["name"]))
        if tag in _VOID:
            return
        match = _COLOR.search(attr.get("style", ""))
        self._open.append((tag, match.group(1).strip() if match else None))
        if tag == "style":
            self._in_style = True
        elif tag == "tr":
            self._row = []
            self._head = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "a":
            self._link = (attr.get("href", ""), [])
        elif tag == "option":
            self._option = (attr.get("value", ""), [])

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
        elif tag in ("td", "th") and self._row is not None and self._cell is not None:
            (self._row if tag == "td" else self._head).append(_squash(self._cell))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.page.rows.append(self._row)
            if self._head:
                self.page.headers.append(self._head)
            self._row = None
        elif tag == "a" and self._link is not None:
            self.page.links.append((self._link[0], _squash(self._link[1])))
            self._link = None
        elif tag == "option" and self._option is not None:
            self.page.options.append((self._option[0], _squash(self._option[1])))
            self._option = None
        for i in range(len(self._open) - 1, -1, -1):
            if self._open[i][0] == tag:
                del self._open[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_style:
            return
        self._text.append(data)
        if data.strip():
            self._last_text = " ".join(data.split())
        for target in (self._cell, self._link and self._link[1], self._option and self._option[1]):
            if target is not None:
                target.append(data)
        color = next((c for _, c in reversed(self._open) if c), None)
        if color and data.strip():
            self.page.colored.append((data.strip(), color))


def parse(html: str) -> Page:
    parser = _Parser()
    parser.feed(html)
    parser.close()
    parser.page.text = _squash(parser._text)
    return parser.page


def counter(page: Page, label: str) -> int:
    """`Bekleyen: 4` biçimindeki sayacın değeri."""
    match = re.search(rf"{re.escape(label)}:\s*(-?\d+)", page.text)
    if match is None:
        raise LookupError(f"sayaç bulunamadı: {label}")
    return int(match.group(1))
