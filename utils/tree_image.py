from PIL import Image, ImageDraw, ImageFont
import io

# Pastel colours
BACKGROUND = (255, 240, 250)      # soft pink
NODE_BG = (255, 255, 255)         # white bubble
NODE_BORDER = (255, 200, 230)     # pastel pink border
TEXT_COLOR = (120, 80, 120)       # soft purple

FONT_SIZE = 32


def draw_node(draw, x, y, text):
    """Draws a rounded bubble node with text."""
    w, h = 260, 70
    radius = 25

    # Bubble background
    draw.rounded_rectangle(
        (x, y, x + w, y + h),
        radius=radius,
        fill=NODE_BG,
        outline=NODE_BORDER,
        width=4
    )

    # Text
    font = ImageFont.load_default()  # Railway-safe

    # FIXED: Pillow-safe text measurement
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    draw.text(
        (x + (w - tw) / 2, y + (h - th) / 2),
        text,
        fill=TEXT_COLOR,
        font=font
    )


def generate_tree_image(user_name, spouse_name, caregivers, littles, middles, siblings, handler, pets):
    """Creates the pastel JPEG family tree."""
    width = 1600
    height = 1200

    img = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Center positions
    center_x = width // 2 - 130
    center_y = height // 2 - 35

    # --- YOU ---
    draw_node(draw, center_x, center_y, f"YOU: {user_name}")

    # --- SPOUSE ---
    if spouse_name:
        draw_node(draw, center_x + 350, center_y, f"Spouse: {spouse_name}")
        draw.line(
            (center_x + 260, center_y + 35, center_x + 350, center_y + 35),
            fill=NODE_BORDER,
            width=6
        )

    # --- CAREGIVERS (above) ---
    y_offset = center_y - 200
    x_offset = center_x - 300
    for cg in caregivers:
        draw_node(draw, x_offset, y_offset, f"Caregiver: {cg}")
        draw.line(
            (center_x + 130, center_y, x_offset + 130, y_offset + 70),
            fill=NODE_BORDER,
            width=4
        )
        x_offset += 300

    # --- LITTLES (below) ---
    y_offset = center_y + 200
    x_offset = center_x - 300
    for little in littles:
        draw_node(draw, x_offset, y_offset, f"Little: {little}")
        draw.line(
            (center_x + 130, center_y + 70, x_offset + 130, y_offset),
            fill=NODE_BORDER,
            width=4
        )
        x_offset += 300

    # --- MIDDLES (below littles) ---
    y_offset = center_y + 350
    x_offset = center_x - 300
    for mid in middles:
        draw_node(draw, x_offset, y_offset, f"Middle: {mid}")
        draw.line(
            (center_x + 130, center_y + 70, x_offset + 130, y_offset),
            fill=NODE_BORDER,
            width=4
        )
        x_offset += 300

    # --- SIBLINGS (left side) ---
    y_offset = center_y - 100
    x_offset = center_x - 600
    for sib in siblings:
        draw_node(draw, x_offset, y_offset, f"Sibling: {sib}")
        draw.line(
            (center_x, center_y + 35, x_offset + 260, y_offset + 35),
            fill=NODE_BORDER,
            width=4
        )
        y_offset += 120

    # --- HANDLER (bottom-left) ---
    if handler:
        draw_node(draw, center_x - 600, center_y + 450, f"Handler: {handler}")
        draw.line(
            (center_x, center_y + 70, center_x - 340, center_y + 450),
            fill=NODE_BORDER,
            width=4
        )

    # --- PETS (under handler) ---
    y_offset = center_y + 580
    x_offset = center_x - 600
    for pet in pets:
        draw_node(draw, x_offset, y_offset, f"Pet: {pet}")
        draw.line(
            (center_x - 600 + 130, center_y + 450 + 70, x_offset + 130, y_offset),
            fill=NODE_BORDER,
            width=4
        )
        y_offset += 120

    # Save to bytes
    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output
