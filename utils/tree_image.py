from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

WIDTH = 1600
HEIGHT = 1200

BG_COLOR = (10, 10, 10)          # black background
GOLD = (212, 175, 55)            # gold accents
NODE_BG = (20, 20, 20)           # dark node background
TEXT_COLOR = GOLD

NODE_WIDTH = 260
NODE_HEIGHT = 70
NODE_RADIUS = 20
LINE_WIDTH = 4

FONT_PATH = "arial.ttf"
FONT_SIZE = 28


def rounded_rect(draw, xy, radius, outline, fill, width=2):
    draw.rounded_rectangle(
        xy,
        radius=radius,
        outline=outline,
        fill=fill,
        width=width
    )


def draw_centered_text(draw, xy, text, font, fill):
    x1, y1, x2, y2 = xy

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    draw.text(
        ((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2),
        text,
        font=font,
        fill=fill,
    )


class Node:
    def __init__(self, label, center):
        self.label = label
        self.cx, self.cy = center

    @property
    def rect(self):
        x1 = self.cx - NODE_WIDTH // 2
        y1 = self.cy - NODE_HEIGHT // 2
        x2 = self.cx + NODE_WIDTH // 2
        y2 = self.cy + NODE_HEIGHT // 2
        return (x1, y1, x2, y2)

    def draw(self, draw, font):
        rounded_rect(
            draw,
            self.rect,
            NODE_RADIUS,
            outline=GOLD,
            fill=NODE_BG,
            width=LINE_WIDTH,
        )
        draw_centered_text(
            draw,
            self.rect,
            self.label,
            font,
            TEXT_COLOR,
        )


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
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    nodes = []

    # YOU
    nodes.append(Node(f"YOU: {user_name}", (WIDTH // 2, HEIGHT // 2)))

    # SPOUSE
    if spouse_name:
        nodes.append(
            Node(
                f"Spouse: {spouse_name}",
                (WIDTH // 2 + 380, HEIGHT // 2),
            )
        )

    # CAREGIVERS
    cy = HEIGHT // 2 - 220
    offset = 220
    for i, name in enumerate(caregivers):
        nodes.append(
            Node(
                f"Caregiver: {name}",
                (WIDTH // 2 + (i * offset) - offset, cy),
            )
        )

    # SIBLINGS
    base_x = WIDTH // 2 - 380
    base_y = HEIGHT // 2 - 40
    spacing = 110

    for i, name in enumerate(siblings):
        nodes.append(
            Node(
                f"Sibling: {name}",
                (base_x, base_y + (i * spacing)),
            )
        )

    # HANDLER
    if handler:
        hy = base_y + spacing * len(siblings)

        nodes.append(
            Node(
                f"Handler: {handler}",
                (base_x, hy),
            )
        )

        for i, name in enumerate(pets):
            nodes.append(
                Node(
                    f"Pet: {name}",
                    (base_x, hy + ((i + 1) * spacing)),
                )
            )

    # LITTLES
    little_y = HEIGHT // 2 + 150

    for i, name in enumerate(littles):
        nodes.append(
            Node(
                f"Little: {name}",
                (WIDTH // 2 + (i * 200) - 150, little_y),
            )
        )

    # MIDDLES
    middle_y = little_y + 120

    for i, name in enumerate(middles):
        nodes.append(
            Node(
                f"Middle: {name}",
                (WIDTH // 2 + (i * 200) - 150, middle_y),
            )
        )

    # Draw every node
    for node in nodes:
        node.draw(draw, font)

    # Return image as bytes
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer
