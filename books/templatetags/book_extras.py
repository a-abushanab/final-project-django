from django import template

register = template.Library()

AVATAR_COLORS = [
    '#1565c0',  # blue
    '#2e7d32',  # green
    '#e65100',  # deep orange
    '#6a1b9a',  # purple
    '#c62828',  # red
    '#00695c',  # teal
    '#4527a0',  # deep purple
    '#f57f17',  # amber
    '#0277bd',  # light blue
    '#558b2f',  # light green
]


@register.filter
def avatar_color(user):
    return AVATAR_COLORS[user.pk % len(AVATAR_COLORS)]


@register.filter
def avatar_initials(user):
    name = user.get_full_name()
    if name:
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return parts[0][0].upper()
    return user.username[0].upper()


CATEGORY_ICONS = [
    'bi-book', 'bi-flask', 'bi-globe2', 'bi-cpu', 'bi-palette',
    'bi-music-note-beamed', 'bi-lightbulb', 'bi-heart', 'bi-trophy', 'bi-camera',
    'bi-graph-up', 'bi-shield-check', 'bi-flower1', 'bi-airplane', 'bi-mortarboard', 'bi-hammer',
]

CATEGORY_COLORS = [
    ('#1565c0', '#e3f0ff'), ('#2e7d32', '#e8f5e9'), ('#e65100', '#fff3e0'),
    ('#6a1b9a', '#f3e5f5'), ('#c62828', '#ffebee'), ('#00695c', '#e0f2f1'),
    ('#4527a0', '#ede7f6'), ('#f57f17', '#fffde7'), ('#0277bd', '#e1f5fe'),
    ('#558b2f', '#f1f8e9'), ('#ad1457', '#fce4ec'), ('#37474f', '#eceff1'),
    ('#6d4c41', '#efebe9'), ('#00838f', '#e0f7fa'), ('#1b5e20', '#f1f8e9'), ('#bf360c', '#fbe9e7'),
]


@register.filter
def category_icon(category):
    return CATEGORY_ICONS[category.pk % len(CATEGORY_ICONS)]


@register.filter
def category_fg(category):
    return CATEGORY_COLORS[category.pk % len(CATEGORY_COLORS)][0]


@register.filter
def category_bg(category):
    return CATEGORY_COLORS[category.pk % len(CATEGORY_COLORS)][1]


@register.filter
def abs(value):
    try:
        return __builtins__['abs'](value) if isinstance(__builtins__, dict) else __import__('builtins').abs(value)
    except Exception:
        return value


@register.filter
def widthpct(value, total):
    """Return percentage of value/total, clamped 0-100."""
    try:
        pct = int(value) / int(total) * 100
        return max(0, min(100, round(pct)))
    except Exception:
        return 0


@register.filter
def star_range(rating):
    """Return list of (filled, half) booleans for 5 stars given a float rating."""
    stars = []
    for i in range(1, 6):
        if rating >= i:
            stars.append('full')
        elif rating >= i - 0.5:
            stars.append('half')
        else:
            stars.append('empty')
    return stars
