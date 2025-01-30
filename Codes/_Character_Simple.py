import os
from PIL import Image, PngImagePlugin

current_directory = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(current_directory, "norm.png") # Path to the image

image = Image.open(image_path)

x = 30
y =  30

metadata = PngImagePlugin.PngInfo()
metadata.add_text("Comment", f"[type:angry;x:{x};y:{y};z-order:0;pivot_x:0.5003;pivot_y:0.4997;]")
metadata.add_text("Comment", f"[type:happy;x:{x};y:{y};z-order:0;pivot_x:0.5003;pivot_y:0.4997;]")
metadata.add_text("Comment", f"[type:norm;x:{x};y:{y};z-order:0;pivot_x:0.5003;pivot_y:0.4997;]")      

output_path = os.path.join(current_directory, "norm_updated.png")
image.save(output_path, "png", pnginfo=metadata)
