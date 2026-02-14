#!/usr/bin/env python3
"""
COLOR ANALYZER – Zero friction. Just double-click.
Extracts color frequencies and image stats.
No OCR. No object detection. No dependency hell.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
from pathlib import Path
import time

# ------------------------------------------------------------
# COLOR ANALYSIS – USES ONLY PILLOW
# ------------------------------------------------------------
def analyze_colors(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        # Resize for speed on old computers
        img.thumbnail((300, 300))
        
        # Get all pixels
        pixels = list(img.getdata())
        total_pixels = len(pixels)
        
        # Count color frequencies (simple method)
        color_count = {}
        for pixel in pixels[:50000]:  # limit for speed
            # Reduce color precision for grouping
            r = (pixel[0] // 20) * 20
            g = (pixel[1] // 20) * 20
            b = (pixel[2] // 20) * 20
            key = (r, g, b)
            color_count[key] = color_count.get(key, 0) + 1
        
        # Sort by frequency
        sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate percentages
        total_sampled = sum(x[1] for x in sorted_colors)
        
        result = []
        result.append("=" * 50)
        result.append("COLOR ANALYSIS")
        result.append("=" * 50)
        result.append(f"Image: {Path(image_path).name}")
        result.append(f"Dimensions: {img.width} x {img.height}")
        result.append(f"Total pixels sampled: {total_sampled:,}")
        result.append("")
        result.append("TOP 20 COLORS (approx):")
        result.append("-" * 40)
        
        for i, ((r,g,b), count) in enumerate(sorted_colors[:20]):
            percent = (count / total_sampled) * 100
            result.append(f"{i+1:2d}. RGB({r},{g},{b}) – {percent:.1f}%")
        
        # Average color
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        result.append("")
        result.append(f"AVERAGE COLOR: RGB({avg_r},{avg_g},{avg_b})")
        
        return "\n".join(result)
    except Exception as e:
        return f"COLOR ERROR: {e}"

# ------------------------------------------------------------
# IMAGE STATS
# ------------------------------------------------------------
def analyze_stats(image_path):
    try:
        img = Image.open(image_path)
        result = []
        result.append("=" * 50)
        result.append("IMAGE STATISTICS")
        result.append("=" * 50)
        result.append(f"File name: {Path(image_path).name}")
        result.append(f"Format: {img.format or 'Unknown'}")
        result.append(f"Mode: {img.mode}")
        result.append(f"Dimensions: {img.width} x {img.height} pixels")
        result.append(f"File size: {os.path.getsize(image_path):,} bytes")
        return "\n".join(result)
    except Exception as e:
        return f"STATS ERROR: {e}"

# ------------------------------------------------------------
# PROCESS ONE IMAGE
# ------------------------------------------------------------
def process_image(image_path, output_dir):
    out_file = output_dir / f"{Path(image_path).stem}_analysis.txt"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"IMAGE ANALYSIS REPORT\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(analyze_stats(image_path) + "\n\n")
        f.write(analyze_colors(image_path) + "\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n")
    return out_file

# ------------------------------------------------------------
# GUI – SIMPLE, NO BEIGE
# ------------------------------------------------------------
class ColorAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("COLOR ANALYZER")
        self.root.geometry("600x500")
        self.root.configure(bg='black')
        
        self.input_folder = None
        self.image_files = []
        
        tk.Label(root, text="COLOR ANALYZER [f++]",
                fg='#00cccc', bg='black',
                font=('Courier New', 16, 'bold')).pack(pady=(20,10))
        
        tk.Label(root, text="Extract colors from every image in a folder",
                fg='#008080', bg='black',
                font=('Courier New', 10)).pack()
        
        # Folder button
        btn = tk.Button(root, text="[ SELECT IMAGE FOLDER ]",
                       fg='black', bg='#008080',
                       font=('Courier New', 12, 'bold'),
                       command=self.select_folder)
        btn.pack(pady=20)
        
        self.folder_label = tk.Label(root, text="(no folder selected)",
                                    fg='#004d4d', bg='black',
                                    font=('Courier New', 9))
        self.folder_label.pack()
        
        # Process button
        self.process_btn = tk.Button(root, text="[ PROCESS IMAGES ]",
                                    fg='black', bg='#00cccc',
                                    font=('Courier New', 14, 'bold'),
                                    state='disabled',
                                    command=self.process)
        self.process_btn.pack(pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(root, orient='horizontal', length=450, mode='determinate')
        self.progress.pack(pady=10)
        
        # Log
        self.log = tk.Text(root, height=12, width=80,
                          bg='#0a0a0a', fg='#00cccc',
                          font=('Courier New', 9))
        self.log.pack(pady=10, padx=10, fill='both', expand=True)
        
        tk.Label(root, text="><^", fg='#004d4d', bg='black',
                font=('Courier New', 12)).pack(pady=(10,0))
    
    def log_message(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.root.update()
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder = Path(folder)
            self.folder_label.config(text=str(self.input_folder))
            
            # Find images
            self.image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']:
                self.image_files.extend(self.input_folder.glob(ext))
                self.image_files.extend(self.input_folder.glob(ext.upper()))
            
            self.log_message(f"📁 Found {len(self.image_files)} images")
            if self.image_files:
                self.process_btn.config(state='normal')
    
    def process(self):
        if not self.image_files:
            return
        
        out_dir = self.input_folder / "analyzed_images"
        out_dir.mkdir(exist_ok=True)
        
        self.log_message(f"\nProcessing {len(self.image_files)} images...")
        self.progress['maximum'] = len(self.image_files)
        self.progress['value'] = 0
        
        success = 0
        for i, img_path in enumerate(self.image_files):
            try:
                self.log_message(f"[{i+1}] {img_path.name}")
                process_image(img_path, out_dir)
                success += 1
            except Exception as e:
                self.log_message(f"  ✗ Error: {e}")
            self.progress['value'] = i + 1
            self.root.update()
        
        self.log_message(f"\n✅ Done! {success} images processed.")
        self.log_message(f"📁 Output folder: {out_dir}")
        messagebox.showinfo("Complete", f"Processed {success} images.")

# ------------------------------------------------------------
# BOOT
# ------------------------------------------------------------
if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed. Run: sudo apt install python3-pil")
        exit(1)
    
    root = tk.Tk()
    root.configure(bg='black')
    app = ColorAnalyzer(root)
    root.mainloop()