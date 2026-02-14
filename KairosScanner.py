#!/usr/bin/env python3
"""
KAIROS COGNITIVE ARTIFACT SCANNER
Double-clickable GUI for Linux
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import glob
import subprocess
from datetime import datetime

class SimpleScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 KAIROS Scanner")
        self.root.geometry("700x500")
        
        # Check for Tesseract
        self.tesseract_installed = self.check_tesseract()
        
        self.setup_ui()
        
    def check_tesseract(self):
        """Check if Tesseract OCR is installed."""
        try:
            result = subprocess.run(["tesseract", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_tesseract(self):
        """Install Tesseract via apt."""
        answer = messagebox.askyesno(
            "Install Tesseract",
            "Tesseract OCR is required but not installed.\n\n"
            "Install now? (Requires sudo password)"
        )
        
        if answer:
            # Try to install
            try:
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "tesseract-ocr"], check=True)
                messagebox.showinfo("Success", "Tesseract installed successfully!")
                self.tesseract_installed = True
                self.status_label.config(text="✅ Tesseract installed")
                return True
            except Exception as e:
                messagebox.showerror("Install Failed", f"Could not install Tesseract:\n{e}")
                return False
        return False
    
    def setup_ui(self):
        """Create simple UI."""
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if self.tesseract_installed:
            self.status_label = ttk.Label(status_frame, text="✅ Tesseract ready")
        else:
            self.status_label = ttk.Label(status_frame, text="❌ Tesseract not installed", 
                                         foreground="red")
        self.status_label.pack(side=tk.LEFT)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="🧠 KAIROS COGNITIVE SCANNER", 
                 font=("Courier", 16, "bold")).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Extract text from screenshot conversations").pack(pady=(0, 20))
        
        # Input folder
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Screenshots Folder:").pack(side=tk.LEFT)
        self.input_var = tk.StringVar(value="screenshots")
        ttk.Entry(input_frame, textvariable=self.input_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT)
        
        # Output file
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output File:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value="scan_results.txt")
        ttk.Entry(output_frame, textvariable=self.output_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="📸 SCAN NOW", 
                  command=self.scan_now, width=20).pack(pady=5)
        
        ttk.Button(button_frame, text="📂 OPEN RESULTS", 
                  command=self.open_results, width=20).pack(pady=5)
        
        ttk.Button(button_frame, text="⚙️ INSTALL TESSERACT", 
                  command=self.install_tesseract, width=20).pack(pady=5)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Log
        ttk.Label(main_frame, text="Log:").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Auto-scan if screenshots folder exists
        if os.path.exists("screenshots"):
            self.log("Found 'screenshots' folder. Ready to scan.")
    
    def browse_input(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.set(folder)
    
    def log(self, message):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def scan_now(self):
        """Start scanning."""
        if not self.tesseract_installed:
            if not self.install_tesseract():
                return
        
        input_dir = self.input_var.get()
        output_file = self.output_var.get()
        
        if not os.path.exists(input_dir):
            messagebox.showerror("Error", f"Folder not found:\n{input_dir}")
            return
        
        # Start scanning in background
        self.progress.start()
        self.log("Starting scan...")
        
        # Run in thread to keep UI responsive
        import threading
        thread = threading.Thread(target=self.run_scan, args=(input_dir, output_file))
        thread.daemon = True
        thread.start()
        
        # Check progress
        self.check_scan_complete(thread)
    
    def run_scan(self, input_dir, output_file):
        """Run the actual scan."""
        try:
            # Find images
            images = []
            for pattern in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']:
                images.extend(glob.glob(os.path.join(input_dir, pattern)))
            
            if not images:
                self.log(f"No images found in {input_dir}")
                return
            
            self.log(f"Found {len(images)} images")
            
            # Process each image
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, img_path in enumerate(images):
                    self.log(f"Scanning {i+1}/{len(images)}: {os.path.basename(img_path)}")
                    
                    try:
                        # Use tesseract command line (simpler than Python binding)
                        result = subprocess.run(
                            ["tesseract", img_path, "stdout"],
                            capture_output=True, text=True, encoding='utf-8'
                        )
                        
                        if result.returncode == 0:
                            text = result.stdout.strip()
                            f.write(f"\n{'='*80}\n")
                            f.write(f"FILE: {os.path.basename(img_path)}\n")
                            f.write(f"{'='*80}\n\n")
                            f.write(text)
                            f.write("\n")
                        else:
                            self.log(f"Error scanning {os.path.basename(img_path)}")
                            
                    except Exception as e:
                        self.log(f"Error: {e}")
            
            self.log(f"\n✅ Scan complete! Saved to {output_file}")
            self.log(f"Total images processed: {len(images)}")
            
        except Exception as e:
            self.log(f"Error: {e}")
    
    def check_scan_complete(self, thread):
        """Check if scan thread is complete."""
        if thread.is_alive():
            self.root.after(100, lambda: self.check_scan_complete(thread))
        else:
            self.progress.stop()
            self.log("Scan thread finished.")
    
    def open_results(self):
        """Open the results file."""
        output_file = self.output_var.get()
        if os.path.exists(output_file):
            # Open with default text editor
            try:
                subprocess.run(["xdg-open", output_file])
            except:
                # Show in dialog
                with open(output_file, 'r') as f:
                    content = f.read()
                
                result_window = tk.Toplevel(self.root)
                result_window.title(f"Results: {output_file}")
                result_window.geometry("600x400")
                
                text = scrolledtext.ScrolledText(result_window)
                text.pack(fill=tk.BOTH, expand=True)
                text.insert(1.0, content[:10000])  # First 10k chars
        else:
            messagebox.showwarning("No Results", "Results file not found yet.")

def main():
    """Main entry point."""
    root = tk.Tk()
    app = SimpleScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()