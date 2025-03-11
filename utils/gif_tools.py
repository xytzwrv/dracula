from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence

def overlay_text_on_gif(gif_data: bytes, font_path: str, overlay_text: str, font_size: int = 20, text_color: str = "black", padding: int = 10) -> BytesIO:
    """
    Overlays the specified text on top of a GIF image.
    Returns a BytesIO object containing the new GIF.
    
    :param gif_data: The original GIF data in bytes.
    :param font_path: Path to the .ttf font file.
    :param overlay_text: The text to overlay on the GIF.
    :param font_size: Size of the font.
    :param text_color: Color of the text.
    :param padding: Padding around the text.
    """
    gif_bytes = BytesIO(gif_data)
    try:
        original_gif = Image.open(gif_bytes)
    except Exception as e:
        raise ValueError("Invalid GIF data provided") from e
    
    # Try to load the specified font, fallback to default if it fails.
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
    
    # Determine the size needed for the text overlay.
    bbox = font.getbbox(overlay_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    bar_height = text_height + 2 * padding
    
    frames = []
    durations = []
    
    is_animated = getattr(original_gif, "is_animated", False) and getattr(original_gif, "n_frames", 1) > 1
    if is_animated:
        for frame in ImageSequence.Iterator(original_gif):
            frame = frame.convert("RGBA")
            width, height = frame.size
            new_frame = Image.new("RGBA", (width, height + bar_height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(new_frame)
            # Center the text in the top bar.
            text_x = (width - text_width) // 2
            text_y = (bar_height - text_height) // 2
            draw.text((text_x, text_y), overlay_text, font=font, fill=text_color)
            new_frame.paste(frame, (0, bar_height), frame)
            final_frame = new_frame.convert("P", palette=Image.ADAPTIVE)
            frames.append(final_frame)
            durations.append(frame.info.get('duration', 100))
    else:
        frame = original_gif.convert("RGBA")
        width, height = frame.size
        new_frame = Image.new("RGBA", (width, height + bar_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(new_frame)
        text_x = (width - text_width) // 2
        text_y = (bar_height - text_height) // 2
        draw.text((text_x, text_y), overlay_text, font=font, fill=text_color)
        new_frame.paste(frame, (0, bar_height), frame)
        final_frame = new_frame.convert("P", palette=Image.ADAPTIVE)
        frames.append(final_frame)
        durations.append(original_gif.info.get('duration', 100))
    
    output_buffer = BytesIO()
    if len(frames) > 1:
        frames[0].save(
            output_buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=durations,
            disposal=2
        )
    else:
        frames[0].save(output_buffer, format="GIF")
    
    output_buffer.seek(0)
    return output_buffer
