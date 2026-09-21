"""Helper functions for building slide dictionaries with strict schema validation."""

def make_title_slide(part, title, subtitle, stats, summary, notes):
    return {
        "type": "title",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "stats": stats,
        "summary": summary,
        "notes": notes
    }

def make_split_cards(part, title, subtitle, card1, card2, notes):
    return {
        "type": "split_cards",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "card1": card1,
        "card2": card2,
        "notes": notes
    }

def make_split_code(part, title, subtitle, codeHeader, codeText, card, notes, accent="#38BDF8"):
    return {
        "type": "split_code",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "codeHeader": codeHeader,
        "codeText": codeText,
        "card": card,
        "accent": accent,
        "notes": notes
    }

def make_three_cards(part, title, subtitle, cards, notes):
    return {
        "type": "three_cards",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "cards": cards,
        "notes": notes
    }

def make_full_code(part, title, subtitle, codeHeader, codeText, bottomCard, notes, accent="#38BDF8"):
    return {
        "type": "full_code",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "codeHeader": codeHeader,
        "codeText": codeText,
        "bottomCard": bottomCard,
        "accent": accent,
        "notes": notes
    }

def make_table_slide(part, title, subtitle, headers, rows, colWidths, notes):
    return {
        "type": "table",
        "part": part,
        "title": title,
        "subtitle": subtitle,
        "headers": headers,
        "rows": rows,
        "colWidths": colWidths,
        "notes": notes
    }
