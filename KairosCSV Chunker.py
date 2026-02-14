#!/usr/bin/env python3
"""
CSV SOVEREIGN CHUNKER - FORGE GUI v1.0
Visual interface for chunking large CSV files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import csv
import os
import json
from datetime import datetime
import threading
import queue

class CSVChunkerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Sovereign Chunker")
        self.root.geometry("750x650")
        
        # Forge Color Palette
        self.colors = {
            "bg": "#000000",
            "card_bg": "#0a0a0a",
            "teal": "#008080",
            "teal_light": "#00cccc",
            "teal_dark": "#004d4d",
            "text": "#c0c0c0"
        }
        
        # Configure styles
        self.setup_styles()
        self.setup_ui()
        
        # Threading for background processing
        self.task_queue = queue.Queue()
        self.processing = False
        
    def setup_styles(self):
        """Configure ttk styles with Forge aesthetic."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Background colors
        style.configure("Teal.TFrame", background=self.colors["card_bg"])
        style.configure("Teal.TLabel", background=self.colors["card_bg"], 
                       foreground=self.colors["teal_light"])
        
        # Buttons
        style.configure("Teal.TButton", 
                       background=self.colors["teal_dark"],
                       foreground=self.colors["teal_light"],
                       borderwidth=1)
        style.map("Teal.TButton",
                 background=[('active', self.colors["teal"])])
        
        # Progress bar
        style.configure("Teal.Horizontal.TProgressbar",
                       background=self.colors["teal"],
                       troughcolor=self.colors["teal_dark"])
    
    def setup_ui(self):
        """Build the GUI interface."""
        # Main container
        main_frame = ttk.Frame(self.root, style="Teal.TFrame", padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === HEADER ===
        header_frame = ttk.Frame(main_frame, style="Teal.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="⚙️ CSV SOVEREIGN CHUNKER", 
                 font=("Courier", 18, "bold"),
                 foreground=self.colors["teal_light"]).pack()
        
        ttk.Label(header_frame, text="Forge Utility v1.0 | Split large CSVs for AI ingestion",
                 foreground=self.colors["teal"]).pack()
        
        # === CONFIGURATION PANEL ===
        config_frame = ttk.LabelFrame(main_frame, text=" CONFIGURATION ", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # File selection
        file_frame = ttk.Frame(config_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Source CSV:", width=12).pack(side=tk.LEFT)
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)
        
        # Chunk settings
        settings_frame = ttk.Frame(config_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_frame, text="Rows per chunk:", width=15).pack(side=tk.LEFT)
        self.chunk_size = tk.StringVar(value="1000")
        ttk.Entry(settings_frame, textvariable=self.chunk_size, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_frame, text="Output folder:", width=15).pack(side=tk.LEFT, padx=(20,0))
        self.output_dir = tk.StringVar(value="csv_chunks")
        ttk.Entry(settings_frame, textvariable=self.output_dir, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)
        
        # === CONTROL PANEL ===
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(control_frame, text="⚡ START CHUNKING", 
                  command=self.start_chunking, width=20,
                  style="Teal.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🛑 STOP", 
                  command=self.stop_processing, width=15).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
                                          variable=self.progress_var,
                                          style="Teal.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # === LOG PANEL ===
        log_frame = ttk.LabelFrame(main_frame, text=" FORGE LOG ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 height=15,
                                                 bg=self.colors["card_bg"],
                                                 fg=self.colors["teal"],
                                                 insertbackground=self.colors["teal_light"],
                                                 font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # === STATUS BAR ===
        self.status_var = tk.StringVar(value="🟢 READY: Select a CSV file to begin.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W,
                              foreground=self.colors["teal"])
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message, level="INFO"):
        """Add a message to the log with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        
        tag_color = self.colors["teal"]
        if level == "ERROR":
            tag_color = "#ff5555"
        elif level == "SUCCESS":
            tag_color = self.colors["teal_light"]
            
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", level)
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Configure tags for colored text
        self.log_text.tag_config("timestamp", foreground=self.colors["teal"])
        self.log_text.tag_config(level, foreground=tag_color)
        
        self.root.update_idletasks()
    
    def browse_file(self):
        """Open file dialog to select CSV."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.log(f"Selected file: {os.path.basename(filename)}")
    
    def browse_output(self):
        """Open directory dialog for output."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def start_chunking(self):
        """Start the chunking process in a separate thread."""
        if self.processing:
            return
            
        # Validate inputs
        if not self.file_path.get():
            messagebox.showwarning("No File", "Please select a CSV file.")
            return
            
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("File Not Found", "The selected file does not exist.")
            return
            
        try:
            chunk_size = int(self.chunk_size.get())
            if chunk_size < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Size", "Please enter a positive integer for chunk size.")
            return
        
        # Reset UI
        self.processing = True
        self.progress_var.set(0)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log(f"Starting chunking process...", "INFO")
        self.status_var.set("⚡ PROCESSING: Chunking in progress...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.chunk_csv_thread, 
                                 args=(self.file_path.get(), 
                                       self.output_dir.get(), 
                                       chunk_size),
                                 daemon=True)
        thread.start()
        
        # Start checking for completion
        self.check_thread_status(thread)
    
    def chunk_csv_thread(self, input_path, output_dir, chunk_size):
        """Background thread for CSV chunking."""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Count total rows first (for progress bar)
            with open(input_path, 'r', encoding='utf-8') as f:
                total_rows = sum(1 for _ in f) - 1  # Subtract header
            
            self.task_queue.put(("PROGRESS_MAX", total_rows))
            self.log(f"File has {total_rows:,} data rows.", "INFO")
            
            # Read and chunk
            with open(input_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                header = next(reader)
                
                chunk_data = []
                chunk_index = 1
                processed_rows = 0
                
                for row in reader:
                    chunk_data.append(row)
                    processed_rows += 1
                    
                    # Update progress every 100 rows
                    if processed_rows % 100 == 0:
                        self.task_queue.put(("PROGRESS", processed_rows))
                        self.task_queue.put(("LOG", f"Processed {processed_rows:,} rows..."))
                    
                    if len(chunk_data) >= chunk_size:
                        self.write_chunk_gui(header, chunk_data, chunk_index, output_dir, input_path)
                        chunk_data = []
                        chunk_index += 1
                
                # Write final chunk
                if chunk_data:
                    self.write_chunk_gui(header, chunk_data, chunk_index, output_dir, input_path)
            
            # Completion
            self.task_queue.put(("COMPLETE", {
                "total_rows": processed_rows,
                "chunks": chunk_index,
                "output_dir": output_dir
            }))
            
        except Exception as e:
            self.task_queue.put(("ERROR", str(e)))
    
    def write_chunk_gui(self, header, data, chunk_num, output_dir, source_path):
        """Write a chunk and send update to GUI thread."""
        filename = f"chunk_{os.path.basename(source_path).replace('.csv', '')}_part{chunk_num:03d}.csv"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(data)
        
        self.task_queue.put(("CHUNK_WRITTEN", {
            "filename": filename,
            "rows": len(data)
        }))
    
    def check_thread_status(self, thread):
        """Check for messages from the processing thread."""
        try:
            while True:
                msg_type, data = self.task_queue.get_nowait()
                
                if msg_type == "PROGRESS_MAX":
                    self.progress_bar.config(maximum=data)
                elif msg_type == "PROGRESS":
                    self.progress_var.set(data)
                elif msg_type == "LOG":
                    self.log(data, "INFO")
                elif msg_type == "CHUNK_WRITTEN":
                    self.log(f"  ✓ Wrote {data['rows']} rows to '{data['filename']}'", "SUCCESS")
                elif msg_type == "COMPLETE":
                    self.processing = False
                    self.progress_var.set(data["total_rows"])
                    self.status_var.set(f"✅ COMPLETE: Created {data['chunks']} chunks in '{data['output_dir']}'")
                    self.log(f"\nChunking successful!", "SUCCESS")
                    self.log(f"Total rows processed: {data['total_rows']:,}", "SUCCESS")
                    self.log(f"Chunks created: {data['chunks']}", "SUCCESS")
                    self.log(f"Output directory: {data['output_dir']}", "SUCCESS")
                    
                    # Offer to open the output directory
                    self.root.after(1000, self.offer_open_directory, data["output_dir"])
                    break
                    
                elif msg_type == "ERROR":
                    self.processing = False
                    self.status_var.set("🔴 ERROR: Processing failed")
                    self.log(f"ERROR: {data}", "ERROR")
                    messagebox.showerror("Processing Error", f"An error occurred:\n{data}")
                    break
                    
        except queue.Empty:
            # Thread still running, check again in 100ms
            if thread.is_alive():
                self.root.after(100, lambda: self.check_thread_status(thread))
            else:
                self.processing = False
                self.status_var.set("⚠️ UNKNOWN: Thread terminated unexpectedly")
    
    def offer_open_directory(self, directory):
        """Ask if user wants to open the output directory."""
        if messagebox.askyesno("Complete", "Chunking complete! Open output directory?"):
            if os.name == 'nt':  # Windows
                os.startfile(directory)
            elif os.name == 'posix':  # macOS, Linux
                os.system(f'open "{directory}"' if sys.platform == 'darwin' else f'xdg-open "{directory}"')
    
    def stop_processing(self):
        """Stop the current processing job."""
        if self.processing:
            self.processing = False
            self.status_var.set("⏹️ STOPPED: Process interrupted by user")
            self.log("Process stopped by user.", "INFO")

def main():
    """Launch the application."""
    root = tk.Tk()
    app = CSVChunkerGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()