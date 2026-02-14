#!/usr/bin/env python3
"""
KAIROS FILE SIFTER v2.0 - GUARANTEED EXECUTION
Single file, no external dependencies beyond tkinter.
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import sys

class GuaranteedFileSifter:
    def __init__(self, master):
        self.master = master
        master.title("KAIROS FILE SIFTER v2.0")
        master.geometry("700x550")
        master.configure(bg='#1a1a1a')
        
        # EXTENSION MAPPING - CUSTOMIZE HERE
        self.category_map = {
            # Images
            '.png': 'Images', '.jpg': 'Images', '.jpeg': 'Images', 
            '.gif': 'Images', '.bmp': 'Images', '.svg': 'Images',
            '.webp': 'Images', '.ico': 'Images', '.tiff': 'Images',
            
            # Documents
            '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents',
            '.txt': 'Documents', '.rtf': 'Documents', '.md': 'Documents',
            '.csv': 'Documents', '.xls': 'Documents', '.xlsx': 'Documents',
            '.ppt': 'Documents', '.pptx': 'Documents', '.odt': 'Documents',
            
            # Audio
            '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio',
            '.aac': 'Audio', '.ogg': 'Audio', '.m4a': 'Audio',
            '.wma': 'Audio',
            
            # Video
            '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video',
            '.mov': 'Video', '.wmv': 'Video', '.flv': 'Video',
            '.webm': 'Video', '.m4v': 'Video',
            
            # Archives
            '.zip': 'Archives', '.rar': 'Archives', '.7z': 'Archives',
            '.tar': 'Archives', '.gz': 'Archives', '.bz2': 'Archives',
            
            # Code
            '.py': 'Code', '.js': 'Code', '.html': 'Code',
            '.css': 'Code', '.java': 'Code', '.cpp': 'Code',
            '.c': 'Code', '.php': 'Code', '.rb': 'Code',
            '.json': 'Code', '.xml': 'Code', '.sql': 'Code',
            
            # Executables
            '.exe': 'Executables', '.msi': 'Executables',
            '.dmg': 'Executables', '.app': 'Executables',
            '.bat': 'Executables', '.sh': 'Executables',
            
            # Fonts
            '.ttf': 'Fonts', '.otf': 'Fonts', '.woff': 'Fonts',
            '.woff2': 'Fonts',
        }
        
        self.setup_ui()
        self.source_path = None
        self.target_path = None
        
    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.master, bg='#2d2d2d', height=80)
        header.pack(fill='x', pady=(0, 20))
        
        title = tk.Label(header, text="⛏️ KAIROS FILE SIFTER", 
                        font=('Courier', 22, 'bold'),
                        fg='#00ff88', bg='#2d2d2d')
        title.pack(pady=20)
        
        subtitle = tk.Label(header, text="IF FASCINATING = TRUE → COPY → PASTE → REPEAT",
                          font=('Courier', 10),
                          fg='#888', bg='#2d2d2d')
        subtitle.pack()
        
        # MAIN CONTAINER
        main = tk.Frame(self.master, bg='#1a1a1a')
        main.pack(fill='both', expand=True, padx=20)
        
        # SOURCE SELECTION
        source_frame = tk.LabelFrame(main, text=" STEP 1: SELECT SOURCE FOLDER ",
                                    font=('Courier', 10, 'bold'),
                                    fg='#00aaff', bg='#2d2d2d', labelanchor='n')
        source_frame.pack(fill='x', pady=(0, 15))
        
        tk.Button(source_frame, text="📁 BROWSE SOURCE", 
                 command=self.select_source,
                 bg='#333', fg='white',
                 font=('Courier', 10),
                 padx=20, pady=5).pack(pady=10)
        
        self.source_label = tk.Label(source_frame, text="No folder selected",
                                    font=('Courier', 9),
                                    fg='#aaa', bg='#2d2d2d',
                                    wraplength=600, justify='left')
        self.source_label.pack(pady=(0, 10), padx=10)
        
        # TARGET SELECTION
        target_frame = tk.LabelFrame(main, text=" STEP 2: SELECT DESTINATION ",
                                    font=('Courier', 10, 'bold'),
                                    fg='#00aaff', bg='#2d2d2d', labelanchor='n')
        target_frame.pack(fill='x', pady=(0, 15))
        
        tk.Button(target_frame, text="📂 BROWSE DESTINATION", 
                 command=self.select_target,
                 bg='#333', fg='white',
                 font=('Courier', 10),
                 padx=20, pady=5).pack(pady=10)
        
        self.target_label = tk.Label(target_frame, text="No folder selected",
                                    font=('Courier', 9),
                                    fg='#aaa', bg='#2d2d2d',
                                    wraplength=600, justify='left')
        self.target_label.pack(pady=(0, 10), padx=10)
        
        # ACTION BUTTONS
        button_frame = tk.Frame(main, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        self.scan_btn = tk.Button(button_frame, text="🔍 SCAN FILES", 
                                 command=self.scan_files,
                                 state='disabled',
                                 bg='#0055aa', fg='white',
                                 font=('Courier', 11, 'bold'),
                                 width=15, pady=8)
        self.scan_btn.pack(side='left', padx=5)
        
        self.sort_btn = tk.Button(button_frame, text="⚡ EXECUTE SORT", 
                                 command=self.execute_sort,
                                 state='disabled',
                                 bg='#008800', fg='white',
                                 font=('Courier', 11, 'bold'),
                                 width=15, pady=8)
        self.sort_btn.pack(side='left', padx=5)
        
        # STATUS / LOG
        log_frame = tk.LabelFrame(main, text=" SYSTEM LOG ",
                                 font=('Courier', 10, 'bold'),
                                 fg='#ffaa00', bg='#2d2d2d', labelanchor='n')
        log_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Text widget for logging
        self.log_text = tk.Text(log_frame, height=8,
                               bg='#111', fg='#00ff88',
                               font=('Courier', 9),
                               wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        self.log("System initialized. Ready.")
        
    def log(self, message):
        """Add timestamped message to log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.master.update_idletasks()
        
    def select_source(self):
        """Let user select source folder."""
        folder = filedialog.askdirectory(title="Select folder to organize")
        if folder:
            self.source_path = Path(folder)
            self.source_label.config(text=f"SOURCE: {self.source_path}", fg='#00ff88')
            self.log(f"Source set: {folder}")
            
            # Enable scan button if we have both paths
            if self.target_path:
                self.scan_btn.config(state='normal')
                self.sort_btn.config(state='normal')
    
    def select_target(self):
        """Let user select destination folder."""
        folder = filedialog.askdirectory(title="Select where to save organized files")
        if folder:
            self.target_path = Path(folder)
            self.target_label.config(text=f"DESTINATION: {self.target_path}", fg='#00ff88')
            self.log(f"Destination set: {folder}")
            
            # Enable scan button if we have both paths
            if self.source_path:
                self.scan_btn.config(state='normal')
                self.sort_btn.config(state='normal')
    
    def scan_files(self):
        """Scan source folder and show what will be moved."""
        if not self.source_path or not self.target_path:
            self.log("ERROR: Select both source and destination first!")
            return
            
        try:
            self.log(f"Scanning {self.source_path}...")
            
            file_count = 0
            category_counts = {}
            
            for item in self.source_path.iterdir():
                if item.is_file():
                    file_count += 1
                    ext = item.suffix.lower()
                    category = self.category_map.get(ext, 'Other')
                    
                    if category not in category_counts:
                        category_counts[category] = 0
                    category_counts[category] += 1
            
            # Display results
            self.log(f"Found {file_count} files to organize:")
            for cat, count in sorted(category_counts.items()):
                self.log(f"  {cat}: {count} files")
                
            self.log("Scan complete. Ready to execute.")
            
        except Exception as e:
            self.log(f"SCAN ERROR: {str(e)}")
            messagebox.showerror("Scan Error", f"Could not scan folder:\n{str(e)}")
    
    def execute_sort(self):
        """Execute the actual file sorting."""
        if not self.source_path or not self.target_path:
            self.log("ERROR: Select both folders first!")
            return
            
        if not messagebox.askyesno("Confirm Execution", 
                                  f"Organize files from:\n{self.source_path}\n\nInto:\n{self.target_path}\n\nProceed?"):
            self.log("Operation cancelled.")
            return
            
        try:
            moved_count = 0
            error_count = 0
            
            self.log("Starting file organization...")
            
            for item in self.source_path.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()
                    category = self.category_map.get(ext, 'Other')
                    
                    # Create category folder
                    category_folder = self.target_path / category
                    category_folder.mkdir(exist_ok=True)
                    
                    # Move file
                    try:
                        destination = category_folder / item.name
                        
                        # Handle duplicate names
                        counter = 1
                        while destination.exists():
                            name_parts = item.stem, item.suffix
                            new_name = f"{name_parts[0]}_{counter}{name_parts[1]}"
                            destination = category_folder / new_name
                            counter += 1
                        
                        shutil.move(str(item), str(destination))
                        moved_count += 1
                        
                        if moved_count % 10 == 0:  # Progress update
                            self.log(f"  Moved {moved_count} files...")
                            
                    except Exception as e:
                        error_count += 1
                        self.log(f"  Failed: {item.name} - {str(e)}")
            
            # Final report
            self.log(f"✓ COMPLETE: Moved {moved_count} files, {error_count} errors")
            
            if error_count > 0:
                messagebox.showwarning("Complete with Errors", 
                                     f"Moved {moved_count} files.\n\n{error_count} files had errors.")
            else:
                messagebox.showinfo("Success!", 
                                  f"Successfully organized {moved_count} files!\n\nCheck: {self.target_path}")
                
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Execution Failed", f"Operation failed:\n{str(e)}")

def main():
    """Main entry point with error handling."""
    try:
        # Try to run the GUI
        root = tk.Tk()
        app = GuaranteedFileSifter(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        root.mainloop()
        
    except tk.TclError as e:
        print("FATAL: Tkinter/GUI failed. This usually means:")
        print("  1. You're on a server/no GUI environment")
        print("  2. Python tkinter is not installed")
        print("\nOn Linux/macOS, install it with:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  macOS: Comes with Python by default")
        print("  Windows: Should work out of the box")
        print(f"\nError details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()