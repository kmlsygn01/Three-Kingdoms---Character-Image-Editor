import ctypes
import struct
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
from tkinter import ttk, Canvas
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFilter, ImageEnhance, PngImagePlugin # type: ignore
import os
import zlib
import shutil

class ImageEditor(tk.Tk):        
    def __init__(self):
        super().__init__()
        # Values        
        self.title("Image Editor")
        self.resizable(True, True)  # Make the window resizable
        self.image_on_canvas = None
        self.frame = None
        self.frame_start = (0, 0)
        self.frame_size = (100, 100)
        self.frame_created = False
        self.img = None
        self.img_tk = None
        self.original_image_path = None
        self.is_resizable = True  # Initially the frame is resizable
        # Fixed frame sizes
        self.fixed_frame_sizes = {
            "bobbleheads": (84, 138),
            "halfbody_large": (312, 250),
            "halfbody_small": (110, 88),
            "mini": (30, 30),
            "unitcards": (82, 272),
            "large_panel": (10, 10),# to avoid making mistakes
            "small_panel": (10, 10)# to avoid making mistakes
        }
        # Large frame sizes
        self.large_frame_sizes = {
            "bobbleheads": (134, 220),
            "halfbody_large": (499, 400),
            "halfbody_small": (176, 134),
            "mini": (48, 48),
            "unitcards": (131, 435),
            "large_panel": (10, 10), # meaningless
            "small_panel": (10, 10) # meaningless
        }
        
        # Get the screen resolution and calculate 90% of it
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.65)
        window_height = int(screen_height * 0.90)

        # Center the window on the screen initially
        self.geometry(f"{window_width}x{window_height}+{(screen_width - window_width) // 2}+{(screen_height - window_height) // 2}")
                
        # Main frame that will contain all the tools and list
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Toolbar frame (Buttons and RadioButtons) for the top part of the window
        self.toolbar_frame = tk.Frame(self.main_frame)
        self.toolbar_frame.pack(side="top", fill="x", pady=5)
        
        self.toolbar_frame_sub = tk.Frame(self.main_frame)
        self.toolbar_frame_sub.pack(side="top", fill="x")

        # Create Icons (as pixel-based data)
        self.load_icon = PhotoImage(width=16, height=16)
        self.load_icon.put(("red",), to=(0, 0, 16, 16))  # Red square for load button

        self.save_icon = PhotoImage(width=16, height=16)
        self.save_icon.put(("green",), to=(0, 0, 16, 16))  # Green square for save button
        
        # Load Button
        self.load_button = tk.Button(
            self.toolbar_frame, 
            text="Load Image", 
            image=self.load_icon, 
            compound="left", 
            command=self.load_image,
            width=140,  # Adjust width for the button
            height=25,  # Adjust height for the button
            font=("Arial", 10, "bold")  # Adjust font size and make it bold
        )
        self.load_button.pack(side="left", padx=10)

        # Save Button
        self.save_button = tk.Button(
            self.toolbar_frame, 
            text="Save", 
            image=self.save_icon, 
            compound="left", 
            command=self.save_image,
            width=140,  # Adjust width for the button
            height=25,  # Adjust height for the button
            font=("Arial", 10, "bold")  # Adjust font size and make it bold
        )        
        self.save_button.pack(side="left", padx=10)
        
        # Label file name
        self.label_name = tk.Label(self.toolbar_frame, text="File Name :",font=("Arial", 10, "bold"))
        self.label_name.pack(side="left", padx=5) 
        
        # Options label
        self.options_label = tk.Label(self.toolbar_frame_sub, text="Options:")
        self.options_label.pack(side="left", padx=10)

        # RadioButtons for options (Arranged side by side)
        self.options = ["large_panel", "small_panel", "bobbleheads", "halfbody_large", "halfbody_small", "mini", "unitcards"]
        self.selected_option = tk.StringVar(value=self.options[0])  # Default option        
        self.radio_buttons = []
        for option in self.options:
            radio_button = ttk.Radiobutton(self.toolbar_frame_sub, text=option, variable=self.selected_option, value=option, command=self.update_frame_size)
            radio_button.pack(side="left", padx=10)  # Arranged side by side
            
        # Options LabelFrame
        self.options_frame = tk.LabelFrame(self.toolbar_frame_sub, text="Options", padx=10, pady=10)
        self.options_frame.pack(side="left", padx=10)
        
        # Coordinates LabelFrame
        self.coordinates_frame = tk.LabelFrame(self.toolbar_frame, text="Coordinates", padx=10, pady=10)
        self.coordinates_frame.pack(side="left", padx=10)
        # Background Color LabelFrame
        self.bg_color_frame = tk.LabelFrame(self.main_frame, padx=5, pady=5)
        self.bg_color_frame.pack(side="top", fill="x", pady=5)
        
        # Label for textbox1
        self.label1 = tk.Label(self.bg_color_frame, text="X :")
        self.label1.pack(side="left", padx=5)        
        # Textbox 1
        self.textbox1 = tk.Entry(self.bg_color_frame, width=8)
        self.textbox1.insert(0, "0")
        self.textbox1.pack(side="left", padx=10)
        # Label for textbox2
        self.label2 = tk.Label(self.bg_color_frame, text="Y :")
        self.label2.pack(side="left", padx=5)
        # Textbox 2
        self.textbox2 = tk.Entry(self.bg_color_frame, width=8)
        self.textbox2.insert(0, "0")
        self.textbox2.pack(side="left", padx=10)
        # Coordinates label
        self.lebals_label = tk.Label(self.bg_color_frame, text="Coordinates:", font=("Arial", 12, "bold"))
        self.lebals_label.pack(side="left", padx=10)
        
        # Slider for image opacity
        self.opacity_var = tk.DoubleVar(value=100)  # Default value is 100%
        self.opacity_slider = tk.Scale(self.bg_color_frame, from_=0, to=100, orient="horizontal", label="Frame Darkness",variable=self.opacity_var, command=self.change_opacity)
        self.opacity_slider.pack(side="right", padx=10, anchor="e")

        # RGB Sliders LabelFrame
        self.rgb_frame = tk.LabelFrame(self.bg_color_frame, text="RGB Colors", padx=10, pady=10)
        self.rgb_frame.pack(side="right", fill="x", pady=5)
        # Red Slider
        self.red_slider = tk.Scale(self.bg_color_frame, from_=0, to=255, orient="horizontal", label="Red", command=lambda x: update_bg_color(self))
        self.red_slider.set(255)
        self.red_slider.pack(side="right", fill="x", padx=10)        
        # Green Slider
        self.green_slider = tk.Scale(self.bg_color_frame, from_=0, to=255, orient="horizontal", label="Green", command=lambda x: update_bg_color(self))
        self.green_slider.set(255)
        self.green_slider.pack(side="right", fill="x", padx=10)
        # Blue Slider
        self.blue_slider = tk.Scale(self.bg_color_frame, from_=0, to=255, orient="horizontal", label="Blue", command=lambda x: update_bg_color(self))
        self.blue_slider.set(255)
        self.blue_slider.pack(side="right", fill="x", padx=10)
        
        def update_bg_color(self):
            r = self.red_slider.get()
            g = self.green_slider.get()
            b = self.blue_slider.get()
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.config(bg=color) 
          
        
        # Console
        self.checkbox_var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(self.toolbar_frame, text="Console", variable=self.checkbox_var, command=self.toggle_console)
        self.checkbox.pack(side="right", padx=10, anchor="e")
        
        # Hide console
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # Canvas (Area for displaying the image)
        canvas_frame = tk.Frame(self.main_frame)
        canvas_frame.pack(side="top", fill="both", expand=True, pady=1, padx=1, anchor="nw")

        # The canvas itself with a white background
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=window_width, height=window_height)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Mouse operations
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)        
        self.bind("<MouseWheel>", self.on_zoom)        
        self.canvas.bind("<Button-3>", self.on_drag)
        self.canvas.bind("<Button-1>", self.on_click)
        # When the frame is moved or resized, call the update_label function
        self.canvas.bind("<B1-Motion>", lambda event: self.update_label())   
             
    def toggle_console(self):
        # Toggle the visibility of the console window based on the checkbox state
        if self.checkbox_var.get():
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)  # Show console
        else:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  # Hide console

    # Function to change frame opacity
    def change_opacity(self, value):
        if self.frame:
            alpha = int(float(value) * 2.55)  # Convert 0-100 scale to 0-255
            color = f'#{alpha:02x}0000'  # Red color with varying alpha
            self.canvas.itemconfig(self.frame, outline=color)       
            
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if file_path:
            self.img = Image.open(file_path)
            self.img_tk = ImageTk.PhotoImage(self.img)
            self.img_name = os.path.basename(file_path)
            
            self.label_name.config(text=f"File Name : {self.img_name}")
            
            enhancer = ImageEnhance.Sharpness(self.img)
            self.img = enhancer.enhance(2.0)

            # Clear the canvas before adding the new image
            self.canvas.delete("all")

            self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.original_image_path = file_path
            if not self.frame_created:
                self.frame_size = (self.img.width, self.img.height)
                self.frame2 = self.canvas.create_rectangle(self.frame_start[0], self.frame_start[1], 
                                                          self.frame_start[0] + self.frame_size[0], 
                                                          self.frame_start[1] + self.frame_size[1], 
                                                          outline="black", width=2)

    # Function to save the current image with frame and processing
    def save_image(self):
        if not self.img:
            messagebox.showerror("Error", "No image loaded!")
            return

        # Get the frame coordinates (crop area)
        frame_coords = self.canvas.coords(self.frame)
        frame_data = {
            "x": frame_coords[0],
            "y": frame_coords[1],
            "width": frame_coords[2] - frame_coords[0],
            "height": frame_coords[3] - frame_coords[1]
        }
        # Get the selected option from radio buttons
        selected_option = self.selected_option.get()

        x = int(frame_data["x"])
        y = int(frame_data["y"])
        width = int(frame_data["width"])
        height = int(frame_data["height"])

        # Validate the selected option
        if selected_option not in self.fixed_frame_sizes:
            messagebox.showerror("Error", f"Invalid option selected: {selected_option}")
            return

        # Get the corresponding size for the selected option
        img_width , img_height = self.fixed_frame_sizes[selected_option]

        # Define folder structure for saving images
        folder_structure = {
            "composites": ["large_panel", "small_panel"],
            "stills": ["bobbleheads", "halfbody_large", "halfbody_small", "mini", "unitcards"]
        }

        # Open file dialog for the user to choose the save directory
        save_directory = filedialog.askdirectory()
        if not save_directory:
            return

        # Loop through the folder structure to save images in the appropriate directories
        for main_folder, subfolders in folder_structure.items():
            main_path = os.path.join(save_directory, main_folder)
            os.makedirs(main_path, exist_ok=True)

            for subfolder in subfolders:
                if subfolder == selected_option:
                    subfolder_path = os.path.join(main_path, subfolder)
                    os.makedirs(subfolder_path, exist_ok=True)

                    # Create "large" subfolder and save large image
                    large_subfolder_path = os.path.join(subfolder_path, "large")
                    os.makedirs(large_subfolder_path, exist_ok=True)
                    # Handle special processing for "bobbleheads"
                    if selected_option == "bobbleheads":                        
                        mask = Image.new('L', (img_width, img_height), 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, img_width, img_height), fill=255)
                    
                        # Crop the image and apply mask
                        cropped_img = self.img.crop((x, y, x + width, y + height))                        
                        mask = mask.resize(cropped_img.size)                        
                        cropped_img = cropped_img.convert('RGBA')
                        mask = mask.convert('L')                     
                        
                        masked_img = Image.composite(cropped_img, Image.new('RGBA', cropped_img.size, (0, 0, 0, 0)), mask)
                    
                        # Add margins and resize the image
                        left_right_margin = int(img_width * 0.12)
                        top_bottom_margin = int(img_height * 0.145)                    
                        img_with_margin = ImageOps.expand(masked_img, 
                                                          border=(left_right_margin, top_bottom_margin, left_right_margin, top_bottom_margin), 
                                                          fill=(0, 0, 0, 0))
                    
                        # Correct the issue: Ensure large_size is a tuple
                        large_size = (img_width * 2, img_height * 2)  # Ensure the values are integers
                        resized_large_img = img_with_margin.resize(large_size, Image.LANCZOS)  # resize requires a tuple for size
                        large_img_path = os.path.join(large_subfolder_path, self.img_name)
                        resized_large_img.save(large_img_path)
                        print(f"Large image saved in {selected_option}/large size: {large_img_path}")
                    
                        # Resize the image for the selected option
                        resized_img = img_with_margin.resize((img_width, img_height), Image.LANCZOS)
                        img_copy_path = os.path.join(subfolder_path, self.img_name)
                        resized_img.save(img_copy_path)
                        print(f"Image saved in {selected_option} size: {img_copy_path}")
                    
                    else:
                        # For other options, crop and save large image
                        if selected_option != "large_panel" and selected_option != "small_panel":
                            # Save the large size
                            cropped_img = self.img.crop((x, y, x + width, y + height))
                            large_size = int(img_width * 2), int(img_height * 2)  # Ensure the values are integers
                            resized_large_img = cropped_img.resize(large_size, Image.LANCZOS)
                            large_img_path = os.path.join(large_subfolder_path, self.img_name)
                            resized_large_img.save(large_img_path)
                            print(f"Large image saved in {selected_option}/large size: {large_img_path}")
                            
                        if selected_option == "large_panel" or selected_option == "small_panel":
                            for mood in ["happy", "angry", "norm"]:
                                mood_subfolder_path = os.path.join(subfolder_path, mood)
                                os.makedirs(mood_subfolder_path, exist_ok=True)

                                # Crop the image
                                cropped_img = self.img.crop((x, y, x + width, y + height))

                                # Save the image as "noanim.png"
                                img_copy_path2 = os.path.join(mood_subfolder_path, "noanim.png")
                                self.img.save(img_copy_path2)
                                print(f"self.img.crop(({x}, {y}, {x + width}, {y + height})) ")
                                print(f"Image saved in {selected_option} size: {img_copy_path2}")
                                self.add_metadata(img_copy_path2, frame_data, mood)

                                # Save the image as mood
                                img_copy_path_mood = os.path.join(mood_subfolder_path, f"{mood}.png")
                                self.img.save(img_copy_path_mood)
                                print(f"Image saved as {mood} in {selected_option} size: {img_copy_path_mood}")
                                self.add_metadata(img_copy_path_mood, frame_data, mood)
                        else:
                            # For other options, crop and resize image
                            cropped_img = self.img.crop((x, y, x + width, y + height))
                            resized_img = cropped_img.resize((img_width, img_height), Image.LANCZOS)
                            img_copy_path2 = os.path.join(subfolder_path, self.img_name)
                            resized_img.save(img_copy_path2)
                            print(f"self.img.crop(({x}, {y}, {x + width}, {y + height})) ")
                            print(f"Image saved in {selected_option} size: {img_copy_path2}")
                        
        messagebox.showinfo("Success", f"Images saved to {save_directory} directory.")

    # Function to add metadata to the PNG file
    def add_metadata(self, img_path, frame_data, emot):
        try:
            metx = int(frame_data.get('x') + int(self.textbox1.get()))
        except ValueError:
            pass
        try:
            mety = int(frame_data.get('y') + int(self.textbox2.get())) 
        except ValueError:
            pass

        
        # Open the PNG file in binary mode for reading
        with open(img_path, "rb") as f:
            png_data = f.read()
    
        # Check the PNG file header for validity
        assert png_data[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG file!"
    
        # Split the PNG file into chunks for modification
        chunks = []
        i = 8  # Start index, skip first 8 bytes (header)
        while i < len(png_data):
            length = int.from_bytes(png_data[i:i+4], "big")
            chunk_type = png_data[i+4:i+8]
            chunk_data = png_data[i+8:i+8+length]
            chunk_crc = png_data[i+8+length:i+12+length]
            chunks.append((chunk_type, chunk_data))
            i += 12 + length

            # Create the metadata chunk to be added
            metadata_text = f"[type:{emot};x:{metx};y:{mety};z-order:0;pivot_x:0.5000;pivot_y:0.5000;]"
            metadata_chunk = self.create_text_chunk("Comment", metadata_text)

        # Insert the new metadata chunk at the second position
        chunks.insert(1, metadata_chunk)

         # Rewrite the PNG with the new chunk data
        with open(img_path, "wb") as f:
            f.write(png_data[:8])  # PNG başlığını yaz
            for chunk_type, chunk_data in chunks:
                f.write(len(chunk_data).to_bytes(4, "big"))  # Uzunluk
                f.write(chunk_type)  # Chunk türü
                f.write(chunk_data)  # Chunk verisi
                f.write(struct.pack(">I", zlib.crc32(chunk_type + chunk_data)))  # CRC'yi doğru hesapla

    def create_text_chunk(self, key, value):
        chunk_type = b'tEXt'
        chunk_data = key.encode("latin1") + b'\x00' + value.encode("latin1")
        return (chunk_type, chunk_data)
    def update_frame_size(self):
        # Clear the existing frame before creating a new one
        if self.frame_created:
            self.canvas.delete(self.frame)
            if hasattr(self, 'plus_sign'):  # Check if the plus_sign exists before deleting
                self.canvas.delete(self.plus_sign)
            self.frame_created = False
    
        selected_option = self.selected_option.get()
    
        if selected_option in self.fixed_frame_sizes:
            self.is_resizable = False
            self.frame_size = self.fixed_frame_sizes[selected_option]
    
            # Create a circular frame if 'bobbleheads' is selected
            if selected_option == "bobbleheads":
                if "bobbleheads" in self.fixed_frame_sizes:
                    self.frame_size = self.fixed_frame_sizes["bobbleheads"]
    
                radius = self.frame_size[0] // 2
                center_x = self.frame_start[0] + radius
                center_y = self.frame_start[1] + radius
                self.frame = self.canvas.create_oval(center_x - radius, center_y - radius, 
                                                     center_x + radius, center_y + radius, 
                                                     outline="red", width=2)
                # Add the "+" sign at the center of the circle
                self.plus_sign = self.canvas.create_text(center_x, center_y, text="+", font=("Arial", 18), fill="red")
            else:  # Create a rectangular frame for other options
                self.frame = self.canvas.create_rectangle(self.frame_start[0], self.frame_start[1], 
                                                          self.frame_start[0] + self.frame_size[0], 
                                                          self.frame_start[1] + self.frame_size[1], 
                                                          outline="red", width=2)
                center_x = self.frame_start[0] + self.frame_size[0] / 2
                center_y = self.frame_start[1] + self.frame_size[1] / 2
                self.plus_sign = self.canvas.create_text(center_x, center_y, text="+", font=("Arial", 18), fill="red")

            self.frame_created = True
        else:
            self.is_resizable = True  # Resizable frame for other options
            # Ensure frame_size is updated for resizable frames
            self.frame_size = (self.default_width, self.default_height)
            self.frame = self.canvas.create_rectangle(self.frame_start[0], self.frame_start[1], 
                                                      self.frame_start[0] + self.frame_size[0], 
                                                      self.frame_start[1] + self.frame_size[1], 
                                                      outline="red", width=2)
            # Add the "+" sign at the center of the rectangle
            center_x = self.frame_start[0] + self.frame_size[0] / 2
            center_y = self.frame_start[1] + self.frame_size[1] / 2
            self.plus_sign = self.canvas.create_text(center_x, center_y, text="+", font=("Arial", 18), fill="red")
            
            self.frame_created = True
            

    def on_click(self, event):
        # If the frame is created, it should only be movable
        if not self.frame_created:
            return
        if hasattr(self, 'label'):
            self.canvas.delete(self.label)
        #self.frame_start = (event.x, event.y)
    def check_radiobox_selection(self):
        selected_panel = self.selected_option.get()        
        return #selected_panel in ["large_panel", "small_panel"]

    def on_drag(self, event):        
        # Only allow movement if the click is on the canvas (not the toolbar or other widgets)
        if event.widget != self.canvas:
            return  # Do nothing if the click is outside the canvas (on toolbar or elsewhere)

        if self.check_radiobox_selection():
            # Create a new frame from scratch
            self.canvas.delete(self.frame)
            if hasattr(self, 'plus_sign'):  # Ensure plus_sign exists before deletion
                self.canvas.delete(self.plus_sign)
            if hasattr(self, 'label'):  # Ensure label exists before deletion
                self.canvas.delete(self.label)
            self.frame = self.canvas.create_rectangle(self.frame_start[0], self.frame_start[1], event.x, event.y, outline="red", width=2)
            # Recreate the "+" sign in the new center position
            center_x = (self.frame_start[0] + event.x) / 2
            center_y = (self.frame_start[1] + event.y) / 2
            self.plus_sign = self.canvas.create_text(center_x, center_y, text="+", font=("Arial", 18), fill="red")
            # Add label with coordinates and size            
        else:
            try:
                # Move the frame
                dx = event.x - self.frame_start[0]
                dy = event.y - self.frame_start[1]
                self.canvas.move(self.frame, dx, dy)
                if hasattr(self, 'plus_sign'):  # Only move the plus_sign if it exists
                    self.canvas.move(self.plus_sign, dx, dy)  # Move the "+" sign along with the frame
                if hasattr(self, 'label'):  # Only move the label if it exists
                    self.canvas.move(self.label, dx, dy)  # Move the label along with the frame
                self.frame_start = (event.x, event.y)
            except:
                pass
        self.update_label()

    # Function to update label with coordinates and size
    def update_label(self):
        if hasattr(self, 'label'):
            self.canvas.delete(self.label)
        label_x = self.frame_start[0] + 125
        label_y = self.frame_start[1] - 10
        #self.canvas.coords(self.label, label_x, label_y)
        #self.canvas.itemconfig(self.label, text=f"x: {self.frame_start[0]}, y: {self.frame_start[1]}, width: {int(self.frame_size[0])}, height: {int(self.frame_size[1])}")
        self.label = self.canvas.create_text(label_x, label_y,  text=f"x: {self.frame_start[0]}, y: {self.frame_start[1]}, width: {int(self.frame_size[0])}, height: {int(self.frame_size[1])}", font=("Arial", 12), fill="red")
        self.lebals_label.config(text=f"Coordinates: X: {self.frame_start[0]}, Y: {self.frame_start[1]}, Width: {int(self.frame_size[0])}, Height: {int(self.frame_size[1])}")
      
    def on_zoom(self, event):
        if self.frame_created:
            # Calculate the new frame size
            if event.delta > 0:
                self.frame_size = (self.frame_size[0] * 1.1, self.frame_size[1] * 1.1)
            else:
                self.frame_size = (self.frame_size[0] / 1.1, self.frame_size[1] / 1.1)
                    # Recalculate the frame's coordinates with the new size
            self.canvas.coords(self.frame, self.frame_start[0], self.frame_start[1], 
                               self.frame_start[0] + self.frame_size[0], 
                               self.frame_start[1] + self.frame_size[1])
                    # Recalculate the new center of the frame
            center_x = self.frame_start[0] + self.frame_size[0] / 2
            center_y = self.frame_start[1] + self.frame_size[1] / 2
            self.canvas.coords(self.plus_sign, center_x, center_y)
        self.update_label()
            
if __name__ == "__main__":
    app = ImageEditor()
    app.mainloop()
