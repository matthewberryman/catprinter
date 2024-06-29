from PIL import Image, ImageDraw, ImageFont
import numpy as np

# get the path of the font file
def get_font_path():
    import os
    return os.path.join(os.path.dirname(__file__), 'Roboto-Regular.ttf')

def text_to_image(text, print_width, font_path=get_font_path(), font_size=20):
    # Set up font and image dimensions
    font = ImageFont.truetype(font_path, font_size)
    lines = []
    words = text.split(' ')
    current_line = []
    current_width = 0

    # Prepare lines of text to fit within print_width
    for word in words:
        word_width = font.getbbox(word + ' ')[2]
        if current_width + word_width <= print_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(' '.join(current_line))

    line_height = font.getbbox('A')[3]
    image_height = line_height * len(lines)

    # Create the image
    img = Image.new('L', (print_width, image_height), 255)
    draw = ImageDraw.Draw(img)

    # Draw the text onto the image
    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=0)
        y += line_height

    # convert the image to something that can be printed using CV2
    img = np.array(img)
    
    # invert the image
    img = 255 - img



    return img