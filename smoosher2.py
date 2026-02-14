#!/usr/bin/env python3
"""
TXT SMOOSHER – FIXED VERSION
Now catches: .txt, .TXT, .md, .text, and ALL subfolders
No file left behind.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from pathlib import Path

class TxtSmoosher:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT SMOOSHER - FIXED")
        self.root.geometry("600x550")
        self.root.configure(bg='black')
        
        self.input_folder = None
        self.text_files = []
        
        # Header
        tk.Label(root, text="TXT SMOOSHER [FIXED]",
                fg='#00cccc', bg='black',
                font=('Courier New', 16, 'bold')).pack(pady=(20,10))
        
        tk.Label(root, text="Now finds EVERY text file in ALL subfolders",
                fg='#008080', bg='black',
                font=('Courier New', 10)).pack()
        
        # Folder selection
        btn_frame = tk.Frame(root, bg='black')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="[ SELECT FOLDER TO SMOOSH ]",
                 fg='black', bg='#008080',
                 font=('Courier New', 11, 'bold'),
                 command=self.select_folder).pack()
        
        self.folder_label = tk.Label(btn_frame, text="(no folder selected)",
                                    fg='#004d4d', bg='black',
                                    font=('Courier New', 9))
        self.folder_label.pack(pady=5)
        
        # File count display
        self.count_label = tk.Label(btn_frame, text="",
                                   fg='#00cccc', bg='black',
                                   font=('Courier New', 10, 'bold'))
        self.count_label.pack(pady=5)
        
        # Output format
        format_frame = tk.Frame(root, bg='black')
        format_frame.pack(pady=10)
        
        tk.Label(format_frame, text="OUTPUT FORMAT:",
                fg='#00cccc', bg='black',
                font=('Courier New', 10, 'bold')).pack()
        
        self.format_var = tk.StringVar(value="txt")
        
        fm = tk.Frame(format_frame, bg='black')
        fm.pack(pady=5)
        
        tk.Radiobutton(fm, text="Single .txt file (with headers)",
                      variable=self.format_var, value="txt",
                      fg='#008080', bg='black', selectcolor='black',
                      font=('Courier New', 9)).pack(side='left', padx=10)
        
        tk.Radiobutton(fm, text="Single .json file (structured)",
                      variable=self.format_var, value="json",
                      fg='#008080', bg='black', selectcolor='black',
                      font=('Courier New', 9)).pack(side='left', padx=10)
        
        # Output file location
        loc_frame = tk.Frame(root, bg='black')
        loc_frame.pack(pady=15)
        
        tk.Label(loc_frame, text="OUTPUT LOCATION (optional):",
                fg='#00cccc', bg='black',
                font=('Courier New', 9)).pack()
        
        self.output_path = None
        tk.Button(loc_frame, text="[ CHOOSE OUTPUT FILE ]",
                 fg='black', bg='#008080',
                 font=('Courier New', 9),
                 command=self.select_output).pack(pady=5)
        
        self.output_label = tk.Label(loc_frame, text="(will create 'smooshed' folder)",
                                    fg='#004d4d', bg='black',
                                    font=('Courier New', 8))
        self.output_label.pack()
        
        # INCLUDE SUBFOLDERS option
        sub_frame = tk.Frame(root, bg='black')
        sub_frame.pack(pady=5)
        
        self.subfolders_var = tk.BooleanVar(value=True)
        tk.Checkbutton(sub_frame, text="Include ALL subfolders (recursive)",
                      variable=self.subfolders_var,
                      fg='#008080', bg='black', selectcolor='black',
                      font=('Courier New', 9)).pack()
        
        # SMOOSH button
        self.smoosh_btn = tk.Button(root, text="[  SMOOSH  ]",
                                   fg='black', bg='#00cccc',
                                   font=('Courier New', 14, 'bold'),
                                   state='disabled',
                                   command=self.smoosh)
        self.smoosh_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, orient='horizontal',
                                        length=450, mode='determinate')
        self.progress.pack(pady=10)
        
        # Log area
        self.log = tk.Text(root, height=10, width=80,
                          bg='#0a0a0a', fg='#00cccc',
                          font=('Courier New', 9))
        self.log.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Footer
        tk.Label(root, text="><^",
                fg='#004d4d', bg='black',
                font=('Courier New', 12)).pack(pady=(10,0))
    
    def log_message(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.root.update()
    
    def find_all_text_files(self, folder, recursive=True):
        """Find ALL text files: .txt, .TXT, .md, .text, .log, etc."""
        folder = Path(folder)
        text_files = []
        
        # ALL text file extensions (case insensitive)
        extensions = ['*.txt', '*.TXT', '*.md', '*.MD', '*.text', '*.TEXT', 
                      '*.log', '*.LOG', '*.csv', '*.CSV', '*.json', '*.JSON']
        
        if recursive:
            # Search ALL subfolders
            for ext in extensions:
                text_files.extend(folder.rglob(ext))
        else:
            # Current folder only
            for ext in extensions:
                text_files.extend(folder.glob(ext))
        
        # Remove duplicates and sort
        text_files = sorted(set(text_files))
        
        # Also catch ANY file that ends with .txt regardless of case
        # (manual catch for any we missed)
        if recursive:
            for f in folder.rglob("*"):
                if f.is_file() and f.suffix.lower() == '.txt' and f not in text_files:
                    text_files.append(f)
        else:
            for f in folder.glob("*"):
                if f.is_file() and f.suffix.lower() == '.txt' and f not in text_files:
                    text_files.append(f)
        
        return sorted(text_files)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing text files")
        if folder:
            self.input_folder = Path(folder)
            self.folder_label.config(text=str(self.input_folder))
            
            # Find ALL text files
            self.text_files = self.find_all_text_files(
                self.input_folder, 
                recursive=self.subfolders_var.get()
            )
            
            self.log_message(f"📁 Searching: {self.input_folder}")
            self.log_message(f"   Recursive: {self.subfolders_var.get()}")
            self.log_message(f"   Found {len(self.text_files)} text files")
            
            # Show first few files as preview
            if self.text_files:
                self.log_message(f"\n📄 First 5 files:")
                for f in self.text_files[:5]:
                    size = f.stat().st_size
                    self.log_message(f"   • {f.relative_to(self.input_folder)} ({size:,} bytes)")
                if len(self.text_files) > 5:
                    self.log_message(f"   • ... and {len(self.text_files)-5} more")
                
                self.count_label.config(
                    text=f"✅ {len(self.text_files)} text files ready to smoosh",
                    fg='#00cccc'
                )
                self.smoosh_btn.config(state='normal')
            else:
                self.count_label.config(
                    text="⚠️ No text files found",
                    fg='#800000'
                )
                self.smoosh_btn.config(state='disabled')
    
    def select_output(self):
        fmt = self.format_var.get()
        default_ext = ".txt" if fmt == "txt" else ".json"
        file_path = filedialog.asksaveasfilename(
            title="Save smooshed file as",
            defaultextension=default_ext,
            filetypes=[
                ("Text files", "*.txt"), 
                ("JSON files", "*.json"), 
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_path = Path(file_path)
            self.output_label.config(text=str(self.output_path))
    
    def smoosh(self):
        if not self.text_files:
            messagebox.showerror("Error", "No text files found.")
            return
        
        fmt = self.format_var.get()
        
        # Determine output path
        if self.output_path:
            out_path = self.output_path
        else:
            # Default: create "smooshed" folder in input folder
            out_dir = self.input_folder / "smooshed"
            out_dir.mkdir(exist_ok=True)
            folder_name = self.input_folder.name or "files"
            out_name = f"smooshed_{folder_name}_{self._timestamp_short()}.{fmt}"
            out_path = out_dir / out_name
        
        self.log_message(f"\n{'='*60}")
        self.log_message(f"SMOOSHING {len(self.text_files)} FILES → {out_path.name}")
        self.log_message(f"{'='*60}")
        self.log_message(f"Output format: .{fmt}")
        self.log_message(f"Recursive: {self.subfolders_var.get()}")
        self.log_message("")
        
        self.progress['maximum'] = len(self.text_files)
        self.progress['value'] = 0
        
        processed = 0
        skipped = 0
        
        try:
            if fmt == "txt":
                processed, skipped = self.smoosh_to_txt(out_path)
            else:  # json
                processed, skipped = self.smoosh_to_json(out_path)
            
            self.progress['value'] = len(self.text_files)
            
            self.log_message(f"\n✅ Complete!")
            self.log_message(f"   • Processed: {processed} files")
            self.log_message(f"   • Skipped: {skipped} files (empty or unreadable)")
            self.log_message(f"   • Saved to: {out_path}")
            
            messagebox.showinfo(
                "Success", 
                f"Smooshed {processed} files\n"
                f"Skipped {skipped} files\n\n"
                f"Saved to:\n{out_path}"
            )
            
        except Exception as e:
            self.log_message(f"\n❌ ERROR: {e}")
            messagebox.showerror("Error", str(e))
    
    def smoosh_to_txt(self, out_path):
        """Combine all text files into one big .txt with headers."""
        processed = 0
        skipped = 0
        
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write("=" * 70 + "\n")
            out_f.write(f"SMOOSHED TEXT FILE\n")
            out_f.write(f"Generated: {self._timestamp()}\n")
            out_f.write(f"Source folder: {self.input_folder}\n")
            out_f.write(f"Recursive: {self.subfolders_var.get()}\n")
            out_f.write(f"Files found: {len(self.text_files)}\n")
            out_f.write("=" * 70 + "\n\n")
            out_f.write(f"CONTENTS:\n")
            out_f.write("-" * 70 + "\n\n")
            
            for i, file_path in enumerate(self.text_files):
                # Update progress
                self.progress['value'] = i + 1
                self.root.update()
                
                # Show relative path in log
                try:
                    rel_path = file_path.relative_to(self.input_folder)
                except:
                    rel_path = file_path.name
                
                self.log_message(f"  [{i+1}/{len(self.text_files)}] {rel_path}")
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    if content.strip():  # Skip empty files
                        out_f.write(f"\n\n{'='*50}\n")
                        out_f.write(f"FILE: {rel_path}\n")
                        out_f.write(f"PATH: {file_path}\n")
                        out_f.write(f"SIZE: {file_path.stat().st_size:,} bytes\n")
                        out_f.write(f"{'='*50}\n\n")
                        out_f.write(content)
                        out_f.write("\n")
                        processed += 1
                    else:
                        skipped += 1
                        self.log_message(f"     ⚠️  Skipped (empty)")
                        
                except Exception as e:
                    skipped += 1
                    self.log_message(f"     ⚠️  Error: {e}")
                    out_f.write(f"\n\n[ERROR READING {rel_path}: {e}]\n")
        
        return processed, skipped
    
    def smoosh_to_json(self, out_path):
        """Combine all text files into a JSON array."""
        data = []
        processed = 0
        skipped = 0
        
        for i, file_path in enumerate(self.text_files):
            # Update progress
            self.progress['value'] = i + 1
            self.root.update()
            
            try:
                rel_path = str(file_path.relative_to(self.input_folder))
            except:
                rel_path = str(file_path)
            
            self.log_message(f"  [{i+1}/{len(self.text_files)}] {rel_path}")
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                data.append({
                    "filename": file_path.name,
                    "path": rel_path,
                    "full_path": str(file_path),
                    "content": content,
                    "size_bytes": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
                processed += 1
                
            except Exception as e:
                skipped += 1
                self.log_message(f"     ⚠️  Error: {e}")
                data.append({
                    "filename": file_path.name,
                    "path": rel_path,
                    "full_path": str(file_path),
                    "error": str(e),
                    "size_bytes": file_path.stat().st_size
                })
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                "source_folder": str(self.input_folder),
                "recursive": self.subfolders_var.get(),
                "files_found": len(self.text_files),
                "files_processed": processed,
                "files_skipped": skipped,
                "generated": self._timestamp(),
                "files": data
            }, f, indent=2, ensure_ascii=False)
        
        return processed, skipped
    
    @staticmethod
    def _timestamp():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def _timestamp_short():
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

# ------------------------------------------------------------
# BOOT
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='black')
    app = TxtSmoosher(root)
    root.mainloop()