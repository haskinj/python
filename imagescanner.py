#!/usr/bin/env python3
"""
IMAGE ANALYZER – Color, OCR, and Object Detection in One GUI
Forge-compliant. Zero configuration. Just works.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path
import threading
import time

# ------------------------------------------------------------
# CORE IMAGE ANALYSIS FUNCTIONS – STANDARD LIBRARY + PILLOW
# ------------------------------------------------------------

def analyze_colors(image_path, max_colors=256):
    """
    Extract color frequency data using Pillow's getcolors().
    Returns list of (count, RGB) tuples and dominant colors.
    """
    try:
        img = Image.open(image_path)
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Reduce colors to get meaningful frequencies
        quantized = img.quantize(colors=max_colors)
        palette = quantized.getpalette()
        
        # Get color counts
        colors = quantized.getcolors(maxcolors=max_colors)
        
        if colors is None:
            return "Color data: Too many unique colors (>256) after quantization."
        
        # Sort by frequency (descending)
        colors.sort(key=lambda x: x[0], reverse=True)
        
        # Format output
        result = []
        result.append("=" * 50)
        result.append("COLOR ANALYSIS")
        result.append("=" * 50)
        result.append(f"Total unique colors: {len(colors)}")
        result.append("")
        result.append("TOP 20 DOMINANT COLORS (RGB):")
        result.append("-" * 40)
        
        for i, (count, color_idx) in enumerate(colors[:20]):
            # Get RGB from palette
            r = palette[color_idx * 3]
            g = palette[color_idx * 3 + 1]
            b = palette[color_idx * 3 + 2]
            rgb = (r, g, b)
            percentage = (count / (img.width * img.height)) * 100
            result.append(f"{i+1:2d}. RGB{rgb} – {count} pixels ({percentage:.2f}%)")
        
        # Calculate average color
        img_rgb = img.convert('RGB')
        pixels = list(img_rgb.getdata())
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        result.append("")
        result.append(f"AVERAGE COLOR: RGB({avg_r}, {avg_g}, {avg_b})")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"COLOR ANALYSIS ERROR: {str(e)}"

def analyze_basic_stats(image_path):
    """Extract basic image statistics using Pillow."""
    try:
        img = Image.open(image_path)
        result = []
        result.append("=" * 50)
        result.append("IMAGE STATISTICS")
        result.append("=" * 50)
        result.append(f"Filename: {Path(image_path).name}")
        result.append(f"Format: {img.format or 'Unknown'}")
        result.append(f"Mode: {img.mode}")
        result.append(f"Dimensions: {img.width} x {img.height} pixels")
        result.append(f"File size: {os.path.getsize(image_path):,} bytes")
        
        # Estimate megapixels
        mp = (img.width * img.height) / 1_000_000
        result.append(f"Resolution: {mp:.2f} megapixels")
        
        return "\n".join(result)
    except Exception as e:
        return f"STATS ERROR: {str(e)}"

# ------------------------------------------------------------
# OCR FUNCTIONS – WILL AUTO-DETECT AVAILABLE ENGINE
# ------------------------------------------------------------

OCR_AVAILABLE = False
OCR_ENGINE = None

def init_ocr():
    """Attempt to initialize available OCR engine."""
    global OCR_AVAILABLE, OCR_ENGINE
    
    # Try pytesseract first (lightweight)
    try:
        import pytesseract
        # Test if tesseract is installed
        pytesseract.get_tesseract_version()
        OCR_AVAILABLE = True
        OCR_ENGINE = "tesseract"
        return True, "Tesseract OCR ready"
    except:
        pass
    
    # Try easyocr as fallback (more accurate but heavier)
    try:
        import easyocr
        # Lazy initialization - will load on first use
        OCR_AVAILABLE = True
        OCR_ENGINE = "easyocr"
        return True, "EasyOCR available (will load on first use)"
    except:
        pass
    
    return False, "No OCR engine found. Install: pip install pytesseract OR easyocr"

def extract_text_from_image(image_path):
    """Extract text using available OCR engine."""
    if not OCR_AVAILABLE:
        return "\n".join([
            "=" * 50,
            "OCR TEXT EXTRACTION",
            "=" * 50,
            "⚠️  NO OCR ENGINE INSTALLED",
            "",
            "To enable text extraction, install one of:",
            "  • Tesseract: sudo apt install tesseract-ocr && pip install pytesseract",
            "  • EasyOCR: pip install easyocr",
            "",
            "Your 2014 Lenovo can handle either."
        ])
    
    try:
        result = []
        result.append("=" * 50)
        result.append("OCR TEXT EXTRACTION")
        result.append("=" * 50)
        
        if OCR_ENGINE == "tesseract":
            import pytesseract
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            result.append(text.strip() if text.strip() else "[No text detected]")
            
        elif OCR_ENGINE == "easyocr":
            import easyocr
            # Initialize reader (lazy load)
            if not hasattr(extract_text_from_image, "reader"):
                extract_text_from_image.reader = easyocr.Reader(['en'])
            result_text = extract_text_from_image.reader.readtext(image_path, detail=0)
            if result_text:
                result.append("\n".join(result_text))
            else:
                result.append("[No text detected]")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"OCR ERROR: {str(e)}"

# ------------------------------------------------------------
# OBJECT DETECTION FUNCTIONS – WILL AUTO-DETECT AVAILABLE ENGINE
# ------------------------------------------------------------

DETECTION_AVAILABLE = False
DETECTION_ENGINE = None

def init_detection():
    """Attempt to initialize available object detection engine."""
    global DETECTION_AVAILABLE, DETECTION_ENGINE
    
    # Try ImageAI first (simplest API)
    try:
        from imageai.Detection import ObjectDetection
        DETECTION_AVAILABLE = True
        DETECTION_ENGINE = "imageai"
        return True, "ImageAI available"
    except:
        pass
    
    # Try YOLO via ultralytics
    try:
        from ultralytics import YOLO
        DETECTION_AVAILABLE = True
        DETECTION_ENGINE = "yolo"
        return True, "YOLO available"
    except:
        pass
    
    return False, "No detection engine found. Install: pip install imageai OR ultralytics"

def detect_objects(image_path):
    """Detect objects using available detection engine."""
    if not DETECTION_AVAILABLE:
        return "\n".join([
            "=" * 50,
            "OBJECT DETECTION",
            "=" * 50,
            "⚠️  NO DETECTION ENGINE INSTALLED",
            "",
            "To enable object detection, install:",
            "  • ImageAI: pip install imageai tensorflow opencv-python",
            "  • YOLO: pip install ultralytics",
            "",
            "Note: Detection models require ~500MB download on first use."
        ])
    
    try:
        result = []
        result.append("=" * 50)
        result.append("OBJECT DETECTION")
        result.append("=" * 50)
        
        if DETECTION_ENGINE == "imageai":
            from imageai.Detection import ObjectDetection
            import os
            
            # Lazy download model
            model_path = os.path.expanduser("~/.imageai/yolov3.pt")
            if not os.path.exists(model_path):
                result.append("Downloading YOLOv3 model (first time only)...")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                import urllib.request
                urllib.request.urlretrieve(
                    "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolov3.pt",
                    model_path
                )
            
            detector = ObjectDetection()
            detector.setModelTypeAsYOLOv3()
            detector.setModelPath(model_path)
            detector.loadModel()
            
            detections = detector.detectObjectsFromImage(
                input_image=image_path,
                output_image_path=None,
                minimum_percentage_probability=30
            )
            
            if detections:
                result.append(f"Found {len(detections)} objects:")
                result.append("-" * 40)
                for obj in detections[:20]:  # Limit to 20
                    name = obj["name"]
                    prob = obj["percentage_probability"]
                    result.append(f"  • {name}: {prob:.1f}% confidence")
            else:
                result.append("[No objects detected]")
        
        elif DETECTION_ENGINE == "yolo":
            from ultralytics import YOLO
            
            # Lazy download model
            if not hasattr(detect_objects, "model"):
                detect_objects.model = YOLO('yolov8n.pt')  # Nano model, fastest
            
            results = detect_objects.model(image_path)
            
            if results[0].boxes is not None:
                names = results[0].names
                boxes = results[0].boxes
                detected = {}
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = names[cls]
                    if name in detected:
                        detected[name] = max(detected[name], conf)
                    else:
                        detected[name] = conf
                
                result.append(f"Found {len(detected)} object types:")
                result.append("-" * 40)
                for name, conf in list(detected.items())[:20]:
                    result.append(f"  • {name}: {conf*100:.1f}% confidence")
            else:
                result.append("[No objects detected]")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"OBJECT DETECTION ERROR: {str(e)}"

# ------------------------------------------------------------
# MAIN PROCESSING ENGINE
# ------------------------------------------------------------

def process_image(image_path, output_dir, include_colors=True, 
                  include_stats=True, include_ocr=True, include_detection=True,
                  progress_callback=None):
    """Process a single image and generate analysis text file."""
    
    output_file = output_dir / f"{Path(image_path).stem}_analysis.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"IMAGE ANALYSIS REPORT\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: {Path(image_path).name}\n")
        f.write("=" * 70 + "\n\n")
        
        # Basic stats
        if include_stats:
            f.write(analyze_basic_stats(image_path))
            f.write("\n\n")
        
        # Color analysis
        if include_colors:
            f.write(analyze_colors(image_path))
            f.write("\n\n")
        
        # OCR text
        if include_ocr:
            f.write(extract_text_from_image(image_path))
            f.write("\n\n")
        
        # Object detection
        if include_detection:
            f.write(detect_objects(image_path))
            f.write("\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n")
    
    if progress_callback:
        progress_callback()
    
    return output_file

# ------------------------------------------------------------
# TKINTER GUI – FORGE AESTHETIC
# ------------------------------------------------------------
class ImageAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IMAGE ANALYZER - FORGE EDITION")
        self.root.geometry("700x700")
        self.root.configure(bg='black')
        
        self.input_folder = None
        self.output_folder = None
        self.image_files = []
        
        # Header
        tk.Label(root, text="IMAGE ANALYZER [f++]",
                fg='#00cccc', bg='black',
                font=('Courier New', 16, 'bold')).pack(pady=(20,10))
        
        tk.Label(root, text="Extract colors, text, and objects from any image",
                fg='#008080', bg='black',
                font=('Courier New', 10)).pack()
        
        # Status indicators
        status_frame = tk.Frame(root, bg='black')
        status_frame.pack(pady=10)
        
        self.ocr_status = tk.Label(status_frame, text="⚫ OCR: Not initialized",
                                  fg='#004d4d', bg='black',
                                  font=('Courier New', 9))
        self.ocr_status.pack()
        
        self.detect_status = tk.Label(status_frame, text="⚫ Detection: Not initialized",
                                     fg='#004d4d', bg='black',
                                     font=('Courier New', 9))
        self.detect_status.pack()
        
        # Folder selection
        folder_frame = tk.Frame(root, bg='black')
        folder_frame.pack(pady=20)
        
        tk.Label(folder_frame, text="INPUT FOLDER:",
                fg='#00cccc', bg='black',
                font=('Courier New', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5)
        
        self.input_btn = tk.Button(folder_frame, text="[ SELECT FOLDER ]",
                                  fg='black', bg='#008080',
                                  font=('Courier New', 10, 'bold'),
                                  command=self.select_input)
        self.input_btn.grid(row=0, column=1, padx=5)
        
        self.input_label = tk.Label(folder_frame, text="(no folder selected)",
                                   fg='#004d4d', bg='black',
                                   font=('Courier New', 9))
        self.input_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        tk.Label(folder_frame, text="OUTPUT FOLDER:",
                fg='#00cccc', bg='black',
                font=('Courier New', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=(15,0))
        
        self.output_btn = tk.Button(folder_frame, text="[ SELECT FOLDER ]",
                                   fg='black', bg='#008080',
                                   font=('Courier New', 10, 'bold'),
                                   command=self.select_output)
        self.output_btn.grid(row=2, column=1, padx=5, pady=(15,0))
        
        self.output_label = tk.Label(folder_frame, text="(will create 'analyzed_images' folder)",
                                    fg='#004d4d', bg='black',
                                    font=('Courier New', 9))
        self.output_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Analysis options
        options_frame = tk.Frame(root, bg='black')
        options_frame.pack(pady=20)
        
        tk.Label(options_frame, text="ANALYSIS OPTIONS:",
                fg='#00cccc', bg='black',
                font=('Courier New', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        self.color_var = tk.BooleanVar(value=True)
        self.stats_var = tk.BooleanVar(value=True)
        self.ocr_var = tk.BooleanVar(value=True)
        self.detect_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Color Analysis (Pillow)",
                      variable=self.color_var, fg='#008080', bg='black',
                      selectcolor='black', font=('Courier New', 9)).grid(row=1, column=0, sticky='w', padx=20)
        
        tk.Checkbutton(options_frame, text="Image Statistics",
                      variable=self.stats_var, fg='#008080', bg='black',
                      selectcolor='black', font=('Courier New', 9)).grid(row=2, column=0, sticky='w', padx=20)
        
        tk.Checkbutton(options_frame, text="OCR Text Extraction",
                      variable=self.ocr_var, fg='#008080', bg='black',
                      selectcolor='black', font=('Courier New', 9),
                      command=self.toggle_ocr).grid(row=1, column=1, sticky='w', padx=20)
        
        tk.Checkbutton(options_frame, text="Object Detection",
                      variable=self.detect_var, fg='#008080', bg='black',
                      selectcolor='black', font=('Courier New', 9),
                      command=self.toggle_detection).grid(row=2, column=1, sticky='w', padx=20)
        
        # PROCESS button
        self.process_btn = tk.Button(root, text="[  PROCESS IMAGES  ]",
                                    fg='black', bg='#00cccc',
                                    font=('Courier New', 14, 'bold'),
                                    state='disabled',
                                    command=self.process)
        self.process_btn.pack(pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(root, orient='horizontal',
                                        length=500, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status = tk.Label(root, text="Ready.",
                              fg='#008080', bg='black',
                              font=('Courier New', 9))
        self.status.pack()
        
        # Log output
        self.log = tk.Text(root, height=12, width=80,
                          bg='#0a0a0a', fg='#00cccc',
                          font=('Courier New', 9),
                          insertbackground='#00cccc')
        self.log.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Footer
        tk.Label(root, text="><^",
                fg='#004d4d', bg='black',
                font=('Courier New', 12)).pack(pady=(10,0))
        
        # Initialize engines in background
        self.init_engines()
    
    def log_message(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.root.update()
    
    def init_engines(self):
        """Initialize OCR and detection engines in background thread."""
        def init():
            # OCR
            ocr_ok, ocr_msg = init_ocr()
            if ocr_ok:
                self.ocr_status.config(text=f"🟢 OCR: {ocr_msg}", fg='#008080')
            else:
                self.ocr_status.config(text=f"🔴 OCR: {ocr_msg}", fg='#800000')
            
            # Detection
            det_ok, det_msg = init_detection()
            if det_ok:
                self.detect_status.config(text=f"🟢 Detection: {det_msg}", fg='#008080')
            else:
                self.detect_status.config(text=f"🔴 Detection: {det_msg}", fg='#800000')
        
        threading.Thread(target=init, daemon=True).start()
    
    def toggle_ocr(self):
        if self.ocr_var.get():
            if not OCR_AVAILABLE:
                self.log_message("⚠️ OCR not installed. Run: pip install pytesseract OR easyocr")
    
    def toggle_detection(self):
        if self.detect_var.get():
            if not DETECTION_AVAILABLE:
                self.log_message("⚠️ Object detection not installed. Run: pip install imageai OR ultralytics")
    
    def select_input(self):
        folder = filedialog.askdirectory(title="Select folder containing images")
        if folder:
            self.input_folder = Path(folder)
            self.input_label.config(text=str(self.input_folder))
            
            # Find image files
            self.image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff']:
                self.image_files.extend(self.input_folder.glob(ext))
                self.image_files.extend(self.input_folder.glob(ext.upper()))
            
            self.log_message(f"Found {len(self.image_files)} images in {self.input_folder.name}")
            
            if self.output_folder and self.image_files:
                self.process_btn.config(state='normal')
    
    def select_output(self):
        folder = filedialog.askdirectory(title="Select output folder for analysis files")
        if folder:
            self.output_folder = Path(folder)
            self.output_label.config(text=str(self.output_folder))
            
            if self.input_folder and self.image_files:
                self.process_btn.config(state='normal')
        else:
            # Default: create 'analyzed_images' in input folder
            self.output_folder = None
            self.output_label.config(text="(will create 'analyzed_images' folder)")
    
    def process(self):
        if not self.image_files:
            messagebox.showerror("Error", "No images found in selected folder.")
            return
        
        # Determine output directory
        if self.output_folder:
            out_dir = self.output_folder
        else:
            out_dir = self.input_folder / "analyzed_images"
        
        out_dir.mkdir(exist_ok=True)
        
        self.log_message(f"\n{'='*60}")
        self.log_message(f"PROCESSING {len(self.image_files)} IMAGES")
        self.log_message(f"{'='*60}")
        
        self.progress['maximum'] = len(self.image_files)
        self.progress['value'] = 0
        self.status.config(text="Processing...")
        self.root.update()
        
        processed = 0
        failed = 0
        
        for i, img_path in enumerate(self.image_files):
            try:
                self.log_message(f"[{i+1}/{len(self.image_files)}] Analyzing: {img_path.name}")
                
                def update_progress():
                    self.progress['value'] = i + 1
                    self.root.update()
                
                output_file = process_image(
                    img_path, out_dir,
                    include_colors=self.color_var.get(),
                    include_stats=self.stats_var.get(),
                    include_ocr=self.ocr_var.get(),
                    include_detection=self.detect_var.get(),
                    progress_callback=update_progress
                )
                
                processed += 1
                self.log_message(f"  ✓ Saved: {output_file.name}")
                
            except Exception as e:
                failed += 1
                self.log_message(f"  ✗ ERROR: {str(e)[:100]}")
        
        self.progress['value'] = len(self.image_files)
        
        summary = f"\n{'='*60}\nCOMPLETE: {processed} processed, {failed} failed\nOutput: {out_dir}\n{'='*60}"
        self.log_message(summary)
        self.status.config(text=f"✓ Done! {processed} images analyzed.")
        messagebox.showinfo("Complete", f"Processed {processed} images.\nOutput saved to:\n{out_dir}")

# ------------------------------------------------------------
# BOOT
# ------------------------------------------------------------
if __name__ == "__main__":
    # Check for Pillow (required)
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow not installed. Run: pip install Pillow")
        sys.exit(1)
    
    root = tk.Tk()
    root.configure(bg='black')
    app = ImageAnalyzerGUI(root)
    root.mainloop()