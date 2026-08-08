from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Base HD resolution (will expand dynamically)
BASE_WIDTH = 2400
BASE_HEIGHT = 1600

GOLD = (212, 175, 55)
NODE_BG = (20, 20, 20)
TEXT_COLOR = GOLD

BASE_FONT_SIZE = 48

NODE_PADDING_X = 60
NODE_PADDING_Y = 40


def auto_font(label, base_size):
    """Safe font loader that NEVER crashes on Railway."""
    # We use Pillow's built-in font only.
    return ImageFont.load_default()


def measure_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_node(draw, x, y, text, font):
    tw, th = measure_text(draw, text, font)
    node_w = tw + NODE_PADDING_X
    node_h = th + NODE_PADDING_Y

    x1 = x - node_w // 2
    y1 = y - node_h // 2
    x2 = x + node_w // 2
    y2 = y + node_h // 2

    draw.rounded_rectangle(
        (x1, y1, x2, y2),
        radius=25,
        outline=GOLD,
        fill=NODE_BG,
        width=4,
    )

    draw.text((x - tw / 2, y - th / 2), text, font=font, fill=TEXT_COLOR)


def generate_tree_image(
    user_name,
    spouse_name,
    caregivers,
    littles,
    middles,
    siblings,
    handler,
    pets,
):
    # Build node list
    nodes = []

    nodes.append(("YOU: " + user_name, "center"))

    if spouse_name:
        nodes.append(("Spouse: " + spouse_name, "center"))

    for name in caregivers:
        nodes.append(("Caregiver: " + name, "care"))

    for name in siblings:
        nodes.append(("Sibling: " + name, "sib"))

    if handler:
        nodes.append(("Handler: " + handler, "handler"))

    for name in pets:
        nodes.append(("Pet: " + name, "pet"))

    for name in littles:
        nodes.append(("Little: " + name, "little"))

    for name in middles:
        nodes.append(("Middle: " + name, "middle"))

    # Dynamic canvas size
    total_nodes = len(nodes)
    width = BASE_WIDTH + (total_nodes * 120)
    height = BASE_HEIGHT + (total_nodes * 80)

    # Load teddy bear cloud background
    background = Image.open("utils/tree_bg.jpg").convert("RGB")
    background = background.resize((width, height))
    img = background.copy()
    draw = ImageDraw.Draw(img)

    # Soft dark overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 60))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)

    # Layout rows
    rows = {
        "care": [],
        "sib": [],
        "handler": [],
        "pet": [],
        "center": [],
        "little": [],
        "middle": [],
    }

    for label, group in nodes:
        rows[group].append(label)

    # Dynamic Y positions
    y_positions = {
        "care": height * 0.20,
        "sib": height * 0.35,
        "handler": height * 0.45,
        "pet": height * 0.55,
        "center": height * 0.50,
        "little": height * 0.65,
        "middle": height * 0.75,
    }

    # Draw nodes
    for group, labels in rows.items():
        if not labels:
            continue

        y = int(y_positions[group])
        spacing = width // (len(labels) + 1)

        for i, label in enumerate(labels):
            x = spacing * (i + 1)
            font = auto_font(label, BASE_FONT_SIZE)
            draw_node(draw, x, y, label, font)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer
