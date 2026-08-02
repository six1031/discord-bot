from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------

WIDTH = 1600
HEIGHT = 1200

BG_COLOR = (10, 10, 10)          # near-black
GOLD = (212, 175, 55)            # soft gold
NODE_BG = (20, 20, 20)           # dark panel
TEXT_COLOR = GOLD

NODE_WIDTH = 260
NODE_HEIGHT = 70
NODE_RADIUS = 20
LINE_WIDTH = 4

FONT_PATH = "arial.ttf"  # change to your serif font if you have one
FONT_SIZE = 28


# ---------- HELPER: ROUNDED RECT ----------

def rounded_rect(draw: ImageDraw.ImageDraw, xy, radius, outline, fill, width=2):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, outline=outline, fill=fill, width=width)


# ---------- HELPER: CENTERED TEXT ----------

def draw_centered_text(draw: ImageDraw.ImageDraw, xy, text, font, fill):
    x1, y1, x2, y2 = xy
    w = x2 - x1
    h = y2 - y1
    tw, th = draw.textsize(text, font=font)
    tx = x1 + (w - tw) / 2
    ty = y1 + (h - th) / 2
    draw.text((tx, ty), text, font=font, fill=fill)


# ---------- NODE CLASS ----------

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
        rounded_rect(draw, self.rect, NODE_RADIUS, outline=GOLD, fill=NODE_BG, width=LINE_WIDTH)
        draw_centered_text(draw, self.rect, self.label, font, TEXT_COLOR)


# ---------- BUILD TREE LAYOUT ----------

def build_nodes():
    nodes = {}

    # Center
    nodes["you"] = Node("YOU: Alex", (WIDTH // 2, HEIGHT // 2))

    # Caregivers (top)
    nodes["caregiver_sarah"] = Node("Caregiver: Sarah", (WIDTH // 2 - 220, HEIGHT // 2 - 220))
    nodes["caregiver_john"] = Node("Caregiver: John", (WIDTH // 2 + 220, HEIGHT // 2 - 220))

    # Spouse (right)
    nodes["spouse_emily"] = Node("Spouse: Emily", (WIDTH // 2 + 380, HEIGHT // 2))

    # Siblings (left column)
    base_x = WIDTH // 2 - 380
    base_y = HEIGHT // 2 - 40
    spacing = 110
    nodes["sibling_michael"] = Node("Sibling: Michael", (base_x, base_y - spacing))
    nodes["sibling_lisa"] = Node("Sibling: Lisa", (base_x, base_y))
    nodes["sibling_david"] = Node("Sibling: David", (base_x, base_y + spacing))

    # Handler + pets (lower left)
    handler_y = base_y + spacing * 2
    nodes["handler_mark"] = Node("Handler: Mark", (base_x, handler_y))
    nodes["pet_buddy"] = Node("Pet: Buddy", (base_x, handler_y + spacing))
    nodes["pet_luna"] = Node("Pet: Luna", (base_x, handler_y + spacing * 2))

    # Littles (below center)
    mid_y_top = HEIGHT // 2 + 150
    nodes["little_chloe"] = Node("Little: Chloe", (WIDTH // 2 - 150, mid_y_top))
    nodes["little_noah"] = Node("Little: Noah", (WIDTH // 2 + 150, mid_y_top))

    # Middles (below littles)
    mid_y_bottom = mid_y_top + 120
    nodes["middle_ethan"] = Node("Middle: Ethan", (WIDTH // 2 - 150, mid_y_bottom))
    nodes["middle_ava"] = Node("Middle: Ava", (WIDTH // 2 + 150, mid_y_bottom))

    return nodes


def draw_connections(draw, nodes):
    # Caregivers to YOU
    you = nodes["you"]
    sarah = nodes["caregiver_sarah"]
    john = nodes["caregiver_john"]

    def bottom_center(node):
        x1, y1, x2, y2 = node.rect
        return ((x1 + x2) / 2, y2)

    def top_center(node):
        x1, y1, x2, y2 = node.rect
        return ((x1 + x2) / 2, y1)

    def left_center(node):
        x1, y1, x2, y2 = node.rect
        return (x1, (y1 + y2) / 2)

    def right_center(node):
        x1, y1, x2, y2 = node.rect
        return (x2, (y1 + y2) / 2)

    # caregivers merge into a single line to YOU
    sarah_bottom = bottom_center(sarah)
    john_bottom = bottom_center(john)
    merge_y = (sarah_bottom[1] + john_bottom[1]) / 2 + 40
    merge_x = WIDTH // 2

    draw.line([sarah_bottom, (sarah_bottom[0], merge_y)], fill=GOLD, width=LINE_WIDTH)
    draw.line([john_bottom, (john_bottom[0], merge_y)], fill=GOLD, width=LINE_WIDTH)
    draw.line([(sarah_bottom[0], merge_y), (john_bottom[0], merge_y)], fill=GOLD, width=LINE_WIDTH)
    draw.line([(merge_x, merge_y), top_center(you)], fill=GOLD, width=LINE_WIDTH)

    # spouse to YOU
    spouse = nodes["spouse_emily"]
    draw.line([left_center(spouse), right_center(you)], fill=GOLD, width=LINE_WIDTH)

    # siblings column from YOU
    sib_m = nodes["sibling_michael"]
    sib_l = nodes["sibling_lisa"]
    sib_d = nodes["sibling_david"]

    left_col_x = left_center(sib_l)[0] + 40
    draw.line([left_center(you), (left_col_x, left_center(you)[1])], fill=GOLD, width=LINE_WIDTH)
    for sib in [sib_m, sib_l, sib_d]:
        draw.line([(left_col_x, left_center(sib)[1]), left_center(sib)], fill=GOLD, width=LINE_WIDTH)

    # handler + pets from handler
    handler = nodes["handler_mark"]
    pet_b = nodes["pet_buddy"]
    pet_l = nodes["pet_luna"]
    draw.line([bottom_center(handler), top_center(pet_b)], fill=GOLD, width=LINE_WIDTH)
    draw.line([bottom_center(pet_b), top_center(pet_l)], fill=GOLD, width=LINE_WIDTH)

    # littles + middles from YOU
    little_c = nodes["little_chloe"]
    little_n = nodes["little_noah"]
    middle_e = nodes["middle_ethan"]
    middle_a = nodes["middle_ava"]

    center_bottom = bottom_center(you)
    trunk_y = center_bottom[1] + 40
    draw.line([center_bottom, (center_bottom[0], trunk_y)], fill=GOLD, width=LINE_WIDTH)

    # branch to littles
    lc_top = top_center(little_c)
    ln_top = top_center(little_n)
    draw.line([(center_bottom[0], trunk_y), (center_bottom[0], lc_top[1])], fill=GOLD, width=LINE_WIDTH)
    draw.line([(center_bottom[0], lc_top[1]), lc_top], fill=GOLD, width=LINE_WIDTH)
    draw.line([(center_bottom[0], ln_top[1]), ln_top], fill=GOLD, width=LINE_WIDTH)

    # middles under littles
    me_top = top_center(middle_e)
    ma_top = top_center(middle_a)
    draw.line([bottom_center(little_c), me_top], fill=GOLD, width=LINE_WIDTH)
    draw.line([bottom_center(little_n), ma_top], fill=GOLD, width=LINE_WIDTH)


# ---------- MAIN EXPORT ----------

def generate_tree_image(output_path: str = "family_tree.png"):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    nodes = build_nodes()
    draw_connections(draw, nodes)

    for node in nodes.values():
        node.draw(draw, font)

    img.save(output_path)
    return output_path


if __name__ == "__main__":
    generate_tree_image()
