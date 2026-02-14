#!/usr/bin/env python3
"""
JSON FORGE GUI - BULK MERGE WITH VISUAL FEEDBACK
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import json
import os
import glob
from datetime import datetime
import threading

class JsonForgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON FORGE // DODECAGONE MERGER")
        self.root.geometry("800x650")
        self.root.configure(bg='#1a1a1a')
        
        # NEON COLOR PALETTE
        self.neon_teal = '#00ff88'
        self.neon_cyan = '#00ffff'
        self.neon_pink = '#ff00ff'
        self.neon_green = '#00ff00'
        self.neon_yellow = '#ffff00'
        self.bg_dark = '#1a1a1a'
        self.bg_medium = '#2d2d2d'
        
        self.setup_gui()
        self.json_files = []
        self.total_files = 0
        self.processing_thread = None
        
    def setup_gui(self):
        # HEADER
        header = tk.Frame(self.root, bg='#2d2d2d', height=90)
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(header, text="⛏️ JSON FORGE MERGER", 
                        font=('Courier', 22, 'bold'),
                        fg=self.neon_teal, bg='#2d2d2d')
        title.pack(pady=20)
        
        subtitle = tk.Label(header, text="BULK JSON MERGE WITH SIGNAL FILTERING",
                          font=('Courier', 10),
                          fg='#888', bg='#2d2d2d')
        subtitle.pack()
        
        # MAIN CONTAINER
        main = tk.Frame(self.root, bg=self.bg_dark)
        main.pack(fill='both', expand=True, padx=20)
        
        # STEP 1: INPUT FOLDER
        input_frame = tk.LabelFrame(main, text=" STEP 1: SELECT JSON FOLDER ",
                                  font=('Courier', 10, 'bold'),
                                  fg=self.neon_cyan, bg=self.bg_medium, labelanchor='n')
        input_frame.pack(fill='x', pady=(0, 15))
        
        self.input_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.input_var, 
                font=('Courier', 9), width=60,
                bg='#111', fg='#ccc', insertbackground='white').pack(side='left', padx=10, pady=10)
        
        tk.Button(input_frame, text="📁 BROWSE", 
                 command=self.select_input_folder,
                 bg='#333', fg='white',
                 font=('Courier', 9, 'bold'),
                 padx=15, pady=5).pack(side='right', padx=10)
        
        # STEP 2: OUTPUT FILE
        output_frame = tk.LabelFrame(main, text=" STEP 2: SET OUTPUT FILE ",
                                   font=('Courier', 10, 'bold'),
                                   fg=self.neon_pink, bg=self.bg_medium, labelanchor='n')
        output_frame.pack(fill='x', pady=(0, 15))
        
        self.output_var = tk.StringVar(value="DODECAGONE_FORGED.json")
        tk.Entry(output_frame, textvariable=self.output_var, 
                font=('Courier', 9), width=60,
                bg='#111', fg='#ccc', insertbackground='white').pack(side='left', padx=10, pady=10)
        
        tk.Button(output_frame, text="💾 SAVE AS...", 
                 command=self.select_output_file,
                 bg='#333', fg='white',
                 font=('Courier', 9, 'bold'),
                 padx=15, pady=5).pack(side='right', padx=10)
        
        # STEP 3: MERGE OPTIONS
        options_frame = tk.LabelFrame(main, text=" STEP 3: FORGE OPTIONS ",
                                    font=('Courier', 10, 'bold'),
                                    fg=self.neon_green, bg=self.bg_medium, labelanchor='n')
        options_frame.pack(fill='x', pady=(0, 15))
        
        # Option checkboxes
        opt_frame = tk.Frame(options_frame, bg=self.bg_medium)
        opt_frame.pack(padx=10, pady=10)
        
        self.var_smart_filter = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame, text="Smart Filtering (high-value only)",
                      variable=self.var_smart_filter,
                      font=('Courier', 9),
                      fg='#aaa', bg=self.bg_medium,
                      selectcolor='#333').pack(anchor='w')
        
        self.var_pretty_print = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame, text="Pretty Print (indented JSON)",
                      variable=self.var_pretty_print,
                      font=('Courier', 9),
                      fg='#aaa', bg=self.bg_medium,
                      selectcolor='#333').pack(anchor='w')
        
        self.var_backup = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame, text="Create Backup (timestamped)",
                      variable=self.var_backup,
                      font=('Courier', 9),
                      fg='#aaa', bg=self.bg_medium,
                      selectcolor='#333').pack(anchor='w')
        
        # STEP 4: CONTROL BUTTONS
        control_frame = tk.Frame(main, bg=self.bg_dark)
        control_frame.pack(pady=20)
        
        self.scan_btn = tk.Button(control_frame, text="🔍 SCAN FOLDER", 
                                 command=self.scan_folder,
                                 bg='#0055aa', fg='white',
                                 font=('Courier', 11, 'bold'),
                                 width=15, pady=8, state='disabled')
        self.scan_btn.pack(side='left', padx=5)
        
        self.forge_btn = tk.Button(control_frame, text="⚡ FORGE MERGE", 
                                  command=self.start_forge,
                                  bg='#008800', fg='white',
                                  font=('Courier', 11, 'bold'),
                                  width=15, pady=8, state='disabled')
        self.forge_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ CLEAR LOG", 
                                  command=self.clear_log,
                                  bg='#aa5500', fg='white',
                                  font=('Courier', 11, 'bold'),
                                  width=15, pady=8)
        self.clear_btn.pack(side='left', padx=5)
        
        # PROGRESS BAR
        self.progress = ttk.Progressbar(main, length=400, mode='determinate')
        self.progress.pack(pady=(0, 10))
        
        # LOG/STATUS WINDOW
        log_frame = tk.LabelFrame(main, text=" FORGE LOG ",
                                 font=('Courier', 10, 'bold'),
                                 fg=self.neon_yellow, bg=self.bg_medium, labelanchor='n')
        log_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 height=15,
                                                 bg='#111', fg=self.neon_teal,
                                                 font=('Courier', 9),
                                                 wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # STATUS BAR
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Select input folder.")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bd=1, relief=tk.SUNKEN, anchor=tk.W,
                             bg='#2d2d2d', fg='#888', font=('Courier', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind input validation
        self.input_var.trace('w', self.validate_inputs)
        
    def log(self, message, color=None):
        """Add timestamped message to log with optional color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = f"color_{len(self.log_text.get('1.0', tk.END))}"
        
        # Configure color tag if specified
        if color:
            self.log_text.tag_config(tag, foreground=color)
        
        # Insert message
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag if color else "")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def select_input_folder(self):
        """Let user select folder containing JSON files"""
        folder = filedialog.askdirectory(title="Select folder with JSON files")
        if folder:
            self.input_var.set(folder)
            self.scan_folder()
            
    def select_output_file(self):
        """Let user choose output file location"""
        file = filedialog.asksaveasfilename(
            title="Save merged JSON as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file:
            self.output_var.set(file)
            
    def validate_inputs(self, *args):
        """Enable/disable buttons based on input state"""
        if self.input_var.get() and os.path.exists(self.input_var.get()):
            self.scan_btn.config(state='normal')
        else:
            self.scan_btn.config(state='disabled')
            
    def scan_folder(self):
        """Scan folder for JSON files"""
        folder = self.input_var.get()
        if not folder:
            return
            
        self.json_files = []
        self.log("Scanning folder for JSON files...", self.neon_cyan)
        
        try:
            # Find all JSON files recursively
            json_patterns = ['*.json', '*.JSON']
            for pattern in json_patterns:
                for filepath in glob.glob(os.path.join(folder, '**', pattern), recursive=True):
                    self.json_files.append(filepath)
                    
            self.total_files = len(self.json_files)
            
            if self.total_files > 0:
                self.log(f"Found {self.total_files} JSON files", self.neon_green)
                self.forge_btn.config(state='normal')
                self.status_var.set(f"Ready: {self.total_files} JSON files found")
            else:
                self.log("No JSON files found!", self.neon_pink)
                self.forge_btn.config(state='disabled')
                self.status_var.set("No JSON files found")
                
        except Exception as e:
            self.log(f"Scan error: {str(e)}", self.neon_pink)
            self.forge_btn.config(state='disabled')
            
    def start_forge(self):
        """Start the merge process in a separate thread"""
        if not self.json_files:
            messagebox.showwarning("No Files", "Scan folder first!")
            return
            
        # Disable buttons during processing
        self.scan_btn.config(state='disabled')
        self.forge_btn.config(state='disabled')
        self.progress['value'] = 0
        
        # Start processing in thread
        self.processing_thread = threading.Thread(target=self.forge_process, daemon=True)
        self.processing_thread.start()
        
        # Start progress monitor
        self.monitor_progress()
        
    def forge_process(self):
        """Main forge process (runs in thread)"""
        try:
            # Create master ledger structure
            master_ledger = {
                "system": "DodecaGone",
                "export_date": datetime.now().isoformat(),
                "total_files": self.total_files,
                "merge_options": {
                    "smart_filter": self.var_smart_filter.get(),
                    "pretty_print": self.var_pretty_print.get(),
                    "backup_created": self.var_backup.get()
                },
                "notes": []
            }
            
            processed = 0
            errors = []
            
            for filepath in self.json_files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Apply smart filtering if enabled
                    if self.var_smart_filter.get():
                        clean_note = self.smart_filter(data)
                        if clean_note:  # Only add if it passes filter
                            master_ledger["notes"].append(clean_note)
                    else:
                        # Add everything
                        master_ledger["notes"].append({
                            "source_file": os.path.basename(filepath),
                            "data": data
                        })
                    
                    processed += 1
                    
                except Exception as e:
                    errors.append(f"{os.path.basename(filepath)}: {str(e)}")
                
                # Update progress (thread-safe via after)
                progress_pct = (processed / self.total_files) * 100
                self.root.after(0, lambda p=progress_pct: self.progress.config(value=p))
            
            # Save the merged file
            output_file = self.output_var.get()
            indent = 4 if self.var_pretty_print.get() else None
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(master_ledger, f, indent=indent, ensure_ascii=False)
            
            # Create backup if requested
            if self.var_backup.get():
                backup_file = f"{output_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(master_ledger, f, indent=indent, ensure_ascii=False)
            
            # Thread-safe UI updates
            self.root.after(0, self.forge_complete, processed, errors, output_file)
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Forge process crashed: {str(e)}", self.neon_pink))
            
    def smart_filter(self, data):
        """Filter for high-value signal only (your original logic)"""
        try:
            # Check if this looks like a Google Keep note
            if isinstance(data, dict) and 'textContent' in data:
                # Extract from Google Keep format
                content = data.get("textContent", "").strip()
                if not content or len(content) < 10:  # Too short
                    return None
                    
                clean_note = {
                    "title": data.get("title", "UNTITLED_SHARD"),
                    "content": content,
                    "labels": [label['name'] for label in data.get("labels", [])],
                    "timestamp": data.get("userEditedTimestampUsec", 0),
                    "is_archived": data.get("isArchived", False),
                    "character_count": len(content)
                }
                return clean_note
                
            # Handle generic JSON objects
            elif isinstance(data, dict):
                # Check for meaningful content
                content_str = str(data).strip()
                if len(content_str) > 50:  # Arbitrary threshold
                    return {
                        "title": "GENERIC_JSON_OBJECT",
                        "content": content_str[:500],  # Truncate long content
                        "data_type": "generic_dict",
                        "key_count": len(data)
                    }
                    
        except Exception:
            pass
            
        return None
        
    def monitor_progress(self):
        """Monitor the processing thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.root.after(100, self.monitor_progress)
        else:
            self.progress['value'] = 100
            
    def forge_complete(self, processed, errors, output_file):
        """Called when forge process completes"""
        self.log("="*50, self.neon_teal)
        self.log(f"⚡ FORGE COMPLETE ⚡", self.neon_green)
        self.log(f"Processed: {processed}/{self.total_files} files", self.neon_cyan)
        
        if errors:
            self.log(f"Errors: {len(errors)}", self.neon_pink)
            for error in errors[:5]:  # Show first 5 errors
                self.log(f"  - {error}", '#ff6666')
            if len(errors) > 5:
                self.log(f"  ... and {len(errors)-5} more", '#ff6666')
                
        self.log(f"Output: {output_file}", self.neon_cyan)
        self.log(f"Total notes in ledger: {processed - len(errors)}", self.neon_green)
        self.log("="*50, self.neon_teal)
        
        # Re-enable buttons
        self.scan_btn.config(state='normal')
        self.forge_btn.config(state='normal')
        self.status_var.set(f"Forge complete: {processed} files merged")
        
        # Show completion dialog
        messagebox.showinfo("Forge Complete", 
                          f"Successfully merged {processed} files into:\n{output_file}\n\n"
                          f"Errors: {len(errors)}")
        
    def clear_log(self):
        """Clear the log window"""
        self.log_text.delete('1.0', tk.END)
        self.log("Log cleared. Ready for new forge operation.", self.neon_yellow)

def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = JsonForgeGUI(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Bind Escape to close
        root.bind('<Escape>', lambda e: root.destroy())
        
        root.mainloop()
        
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        # Fallback to command line
        fallback_cli()

def fallback_cli():
    """Command-line fallback if GUI fails"""
    import sys
    import glob
    
    print("\n" + "="*60)
    print("JSON FORGE - COMMAND LINE MODE")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python json_forge.py <input_folder> [output_file]")
        print("\nExample:")
        print("  python json_forge.py ./Takeout/Keep merged_output.json")
        return
        
    input_folder = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "FORGED_OUTPUT.json"
    
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found!")
        return
        
    print(f"\nScanning: {input_folder}")
    
    # Find JSON files
    json_files = []
    for pattern in ['*.json', '*.JSON']:
        json_files.extend(glob.glob(os.path.join(input_folder, '**', pattern), recursive=True))
    
    if not json_files:
        print("No JSON files found!")
        return
        
    print(f"Found {len(json_files)} JSON files")
    
    # Merge files
    master_ledger = {
        "system": "DodecaGone",
        "export_date": datetime.now().isoformat(),
        "total_files": len(json_files),
        "notes": []
    }
    
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Simple extraction
            if isinstance(data, dict):
                clean_note = {
                    "source": os.path.basename(filepath),
                    "title": data.get("title", "UNTITLED"),
                    "content": data.get("textContent", str(data)[:200]),
                    "timestamp": data.get("userEditedTimestampUsec", 0)
                }
                master_ledger["notes"].append(clean_note)
                
        except Exception as e:
            print(f"  Error reading {os.path.basename(filepath)}: {e}")
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_ledger, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Forge complete!")
    print(f"   Saved to: {output_file}")
    print(f"   Notes: {len(master_ledger['notes'])}")
    
if __name__ == "__main__":
    main()