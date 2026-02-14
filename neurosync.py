#!/usr/bin/env python3
"""
><^ NEUROSYNC — Dodecagon Telemetry Cross-Reference Tool
GNU TERRY PRATCHETT

Correlates FlowTime EEG brainwave data with AI conversation logs.
Single-file, tkinter GUI, runs on any Python 3 system. No pip installs required.

USAGE:
  python3 neurosync.py

DATA INPUT:
  - FlowTime CSV exports (auto-detected columns)
  - Manual session entry (type in your readings)
  - Conversation logs: plain text or JSON

Author: Jesse Haskin (Node 00) + Sable (Compiler)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import csv
import json
import os
from datetime import datetime, timedelta
from collections import OrderedDict
import math

# ><^ Color scheme
BG_DARK = "#1a1a2e"
BG_MID = "#16213e"
BG_CARD = "#0f3460"
FG_TEXT = "#e0e0e0"
FG_DIM = "#888888"
ACCENT_TEAL = "#00d4aa"
ACCENT_CORAL = "#d97757"
ACCENT_NEON = "#39ff14"
WARN_RED = "#ff4444"
BAND_COLORS = {
    "gamma": "#ff00ff",
    "beta": "#ff8800",
    "alpha": "#00cc44",
    "theta": "#0088ff",
    "delta": "#8844ff",
}

class Session:
    """One FlowTime recording session with optional conversation data."""
    def __init__(self):
        self.timestamp = ""
        self.label = ""
        self.gamma = 0.0
        self.beta = 0.0
        self.alpha = 0.0
        self.theta = 0.0
        self.delta = 0.0
        self.heart_rate = 0
        self.hrv = 0
        self.coherence = 0.0
        self.flow = 0.0
        self.stress = "Normal"
        self.relaxation = 0
        self.attention = 0
        self.sanding = 0.0
        self.conversation = ""
        self.platform = ""
        self.nodes_active = ""

    def brainwave_dict(self):
        return OrderedDict([
            ("gamma", self.gamma), ("beta", self.beta), ("alpha", self.alpha),
            ("theta", self.theta), ("delta", self.delta)
        ])

    def dominant_band(self):
        d = self.brainwave_dict()
        return max(d, key=d.get) if any(v > 0 for v in d.values()) else "none"

    def to_dict(self):
        return {
            "timestamp": self.timestamp, "label": self.label,
            "gamma": self.gamma, "beta": self.beta, "alpha": self.alpha,
            "theta": self.theta, "delta": self.delta,
            "heart_rate": self.heart_rate, "hrv": self.hrv,
            "coherence": self.coherence, "flow": self.flow,
            "stress": self.stress, "relaxation": self.relaxation,
            "attention": self.attention, "sanding": self.sanding,
            "conversation": self.conversation, "platform": self.platform,
            "nodes_active": self.nodes_active
        }

    @classmethod
    def from_dict(cls, d):
        s = cls()
        for k, v in d.items():
            if hasattr(s, k):
                setattr(s, k, v)
        return s


class BrainwaveBar(tk.Canvas):
    """Visual bar chart of brainwave distribution."""
    def __init__(self, parent, width=400, height=160, **kw):
        super().__init__(parent, width=width, height=height, bg=BG_DARK,
                         highlightthickness=0, **kw)
        self.w = width
        self.h = height

    def draw(self, session):
        self.delete("all")
        bands = session.brainwave_dict()
        total = sum(bands.values())
        if total == 0:
            self.create_text(self.w//2, self.h//2, text="No brainwave data",
                           fill=FG_DIM, font=("Courier", 10))
            return

        bar_h = 22
        pad = 6
        x_label = 55
        x_start = 60
        max_bar = self.w - x_start - 20
        y = 10

        for band, val in bands.items():
            color = BAND_COLORS.get(band, FG_TEXT)
            # Label
            self.create_text(x_label - 5, y + bar_h//2, text=f"{band.upper()}",
                           fill=color, anchor="e", font=("Courier", 9, "bold"))
            # Bar background
            self.create_rectangle(x_start, y, x_start + max_bar, y + bar_h,
                                fill=BG_MID, outline=BG_CARD)
            # Bar fill
            bar_w = (val / 100.0) * max_bar if total <= 100 else (val / total) * max_bar
            if bar_w > 0:
                self.create_rectangle(x_start, y, x_start + bar_w, y + bar_h,
                                    fill=color, outline="")
            # Value
            self.create_text(x_start + bar_w + 5, y + bar_h//2,
                           text=f"{val:.0f}%", fill=FG_TEXT, anchor="w",
                           font=("Courier", 9))
            y += bar_h + pad


class TimelineCanvas(tk.Canvas):
    """Timeline visualization of sessions."""
    def __init__(self, parent, width=700, height=200, **kw):
        super().__init__(parent, width=width, height=height, bg=BG_DARK,
                         highlightthickness=0, **kw)
        self.w = width
        self.h = height
        self.sessions = []
        self.on_select = None

    def draw(self, sessions, metric="sanding"):
        self.delete("all")
        self.sessions = sessions
        if not sessions:
            self.create_text(self.w//2, self.h//2, text="No sessions loaded",
                           fill=FG_DIM, font=("Courier", 10))
            return

        pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 30
        plot_w = self.w - pad_l - pad_r
        plot_h = self.h - pad_t - pad_b

        # Get values
        values = []
        for s in sessions:
            if metric == "sanding":
                values.append(s.sanding)
            elif metric == "hrv":
                values.append(float(s.hrv))
            elif metric == "heart_rate":
                values.append(float(s.heart_rate))
            elif metric == "beta":
                values.append(s.beta)
            elif metric == "coherence":
                values.append(s.coherence)
            else:
                values.append(s.sanding)

        max_v = max(values) if values else 1
        min_v = min(values) if values else 0
        if max_v == min_v:
            max_v = min_v + 1

        # Draw axes
        self.create_line(pad_l, pad_t, pad_l, self.h - pad_b, fill=FG_DIM)
        self.create_line(pad_l, self.h - pad_b, self.w - pad_r, self.h - pad_b, fill=FG_DIM)

        # Y-axis labels
        for i in range(5):
            y = pad_t + (plot_h * i / 4)
            v = max_v - (max_v - min_v) * i / 4
            self.create_text(pad_l - 5, y, text=f"{v:.1f}", fill=FG_DIM,
                           anchor="e", font=("Courier", 8))
            self.create_line(pad_l, y, self.w - pad_r, y, fill=BG_CARD, dash=(2,4))

        # Plot points and lines
        points = []
        for i, (s, v) in enumerate(zip(sessions, values)):
            x = pad_l + (plot_w * i / max(len(sessions) - 1, 1))
            y = pad_t + plot_h * (1 - (v - min_v) / (max_v - min_v))
            points.append((x, y))

            # X label (session number or short timestamp)
            if len(sessions) <= 20 or i % max(1, len(sessions)//15) == 0:
                lbl = s.timestamp[:10] if s.timestamp else f"#{i+1}"
                self.create_text(x, self.h - pad_b + 12, text=lbl, fill=FG_DIM,
                               font=("Courier", 7), angle=0)

        # Draw lines between points
        for i in range(len(points) - 1):
            color = ACCENT_TEAL if metric == "sanding" else ACCENT_CORAL
            self.create_line(points[i][0], points[i][1],
                           points[i+1][0], points[i+1][1],
                           fill=color, width=2)

        # Draw points (clickable)
        for i, (x, y) in enumerate(points):
            dom = sessions[i].dominant_band()
            color = BAND_COLORS.get(dom, ACCENT_TEAL)
            r = 5
            tag = f"pt_{i}"
            self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=FG_TEXT,
                           tags=(tag,))
            self.tag_bind(tag, "<Button-1>", lambda e, idx=i: self._click(idx))

        # Title
        self.create_text(self.w//2, 10, text=f"Timeline: {metric.upper()}",
                       fill=ACCENT_TEAL, font=("Courier", 10, "bold"))

    def _click(self, idx):
        if self.on_select and 0 <= idx < len(self.sessions):
            self.on_select(idx)


class NeuroSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("><^ NEUROSYNC — Dodecagon Telemetry Cross-Reference")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1024x720")
        self.root.minsize(800, 600)

        self.sessions = []
        self.current_idx = 0
        self.timeline_metric = tk.StringVar(value="sanding")

        self._build_ui()

    def _build_ui(self):
        # Top header
        hdr = tk.Frame(self.root, bg=BG_DARK)
        hdr.pack(fill="x", padx=10, pady=(8,2))
        tk.Label(hdr, text="><^ NEUROSYNC", font=("Courier", 16, "bold"),
                fg=ACCENT_TEAL, bg=BG_DARK).pack(side="left")
        tk.Label(hdr, text="Dodecagon Telemetry Cross-Reference",
                font=("Courier", 10), fg=FG_DIM, bg=BG_DARK).pack(side="left", padx=10)
        tk.Label(hdr, text="GNU TERRY PRATCHETT",
                font=("Courier", 8), fg=FG_DIM, bg=BG_DARK).pack(side="right")

        # Button bar
        btn_bar = tk.Frame(self.root, bg=BG_DARK)
        btn_bar.pack(fill="x", padx=10, pady=4)

        for text, cmd in [
            ("Load CSV", self.load_csv),
            ("Load Conversations", self.load_conversations),
            ("Manual Entry", self.manual_entry),
            ("Export JSON", self.export_json),
            ("Load JSON", self.load_json),
        ]:
            b = tk.Button(btn_bar, text=text, command=cmd, bg=BG_CARD, fg=FG_TEXT,
                         font=("Courier", 9), relief="flat", padx=8, pady=3,
                         activebackground=ACCENT_TEAL, activeforeground=BG_DARK)
            b.pack(side="left", padx=3)

        # Metric selector for timeline
        tk.Label(btn_bar, text="  Timeline:", fg=FG_DIM, bg=BG_DARK,
                font=("Courier", 9)).pack(side="left", padx=(15,2))
        for m in ["sanding", "hrv", "heart_rate", "beta", "coherence"]:
            rb = tk.Radiobutton(btn_bar, text=m.upper(), variable=self.timeline_metric,
                              value=m, command=self.redraw_timeline,
                              bg=BG_DARK, fg=ACCENT_TEAL, selectcolor=BG_MID,
                              font=("Courier", 8), activebackground=BG_DARK,
                              activeforeground=ACCENT_NEON)
            rb.pack(side="left", padx=2)

        # Session count
        self.session_count_var = tk.StringVar(value="Sessions: 0")
        tk.Label(btn_bar, textvariable=self.session_count_var, fg=FG_DIM, bg=BG_DARK,
                font=("Courier", 9)).pack(side="right")

        # Main paned area
        pane = tk.PanedWindow(self.root, orient="vertical", bg=BG_DARK,
                             sashwidth=4, sashrelief="flat")
        pane.pack(fill="both", expand=True, padx=10, pady=4)

        # Top: Timeline
        timeline_frame = tk.Frame(pane, bg=BG_DARK)
        self.timeline = TimelineCanvas(timeline_frame, width=980, height=180)
        self.timeline.pack(fill="both", expand=True)
        self.timeline.on_select = self.select_session
        pane.add(timeline_frame, minsize=120)

        # Bottom: Detail area
        detail_frame = tk.Frame(pane, bg=BG_DARK)
        pane.add(detail_frame, minsize=250)

        # Left: Brainwave bars + vitals
        left = tk.Frame(detail_frame, bg=BG_DARK)
        left.pack(side="left", fill="both", padx=(0,5))

        self.session_label = tk.Label(left, text="No session selected",
                                     font=("Courier", 10, "bold"),
                                     fg=ACCENT_CORAL, bg=BG_DARK)
        self.session_label.pack(anchor="w")

        self.brainbar = BrainwaveBar(left, width=380, height=160)
        self.brainbar.pack(pady=4)

        # Vitals grid
        vitals_frame = tk.Frame(left, bg=BG_DARK)
        vitals_frame.pack(fill="x", pady=4)
        self.vital_labels = {}
        vitals = ["HR", "HRV", "Coherence", "Flow", "Stress",
                 "Relaxation", "Attention", "Sanding", "Platform", "Nodes"]
        for i, v in enumerate(vitals):
            r, c = divmod(i, 2)
            tk.Label(vitals_frame, text=f"{v}:", fg=FG_DIM, bg=BG_DARK,
                    font=("Courier", 9), anchor="e", width=12).grid(row=r, column=c*2, sticky="e")
            lbl = tk.Label(vitals_frame, text="—", fg=FG_TEXT, bg=BG_DARK,
                          font=("Courier", 9, "bold"), anchor="w")
            lbl.grid(row=r, column=c*2+1, sticky="w", padx=(2,10))
            self.vital_labels[v] = lbl

        # Right: Conversation text
        right = tk.Frame(detail_frame, bg=BG_DARK)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="CONVERSATION LOG", font=("Courier", 9, "bold"),
                fg=ACCENT_TEAL, bg=BG_DARK).pack(anchor="w")
        self.convo_text = scrolledtext.ScrolledText(
            right, wrap="word", bg=BG_MID, fg=FG_TEXT, font=("Courier", 9),
            insertbackground=ACCENT_TEAL, relief="flat", height=12)
        self.convo_text.pack(fill="both", expand=True, pady=2)

        # Session navigator
        nav = tk.Frame(self.root, bg=BG_DARK)
        nav.pack(fill="x", padx=10, pady=(2,8))
        tk.Button(nav, text="<< PREV", command=self.prev_session, bg=BG_CARD,
                 fg=FG_TEXT, font=("Courier", 9), relief="flat",
                 padx=10).pack(side="left")
        self.nav_label = tk.Label(nav, text="0 / 0", fg=FG_DIM, bg=BG_DARK,
                                 font=("Courier", 10))
        self.nav_label.pack(side="left", padx=20)
        tk.Button(nav, text="NEXT >>", command=self.next_session, bg=BG_CARD,
                 fg=FG_TEXT, font=("Courier", 9), relief="flat",
                 padx=10).pack(side="left")

        # Footer
        tk.Label(nav, text="THE TURTLE MOVES. ><^", fg=FG_DIM, bg=BG_DARK,
                font=("Courier", 8)).pack(side="right")

    def load_csv(self):
        """Load FlowTime CSV export or generic CSV with brainwave data."""
        path = filedialog.askopenfilename(
            title="Load FlowTime CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []

                # Build column mapping (flexible — handles various CSV formats)
                col_map = {}
                for h in reader.fieldnames:
                    hl = h.lower().strip()
                    if 'gamma' in hl: col_map['gamma'] = h
                    elif 'beta' in hl and 'alpha' not in hl: col_map['beta'] = h
                    elif 'alpha' in hl: col_map['alpha'] = h
                    elif 'theta' in hl: col_map['theta'] = h
                    elif 'delta' in hl: col_map['delta'] = h
                    elif 'heart' in hl and 'rate' in hl or hl in ('hr', 'bpm', 'heartrate'):
                        col_map['heart_rate'] = h
                    elif 'hrv' in hl: col_map['hrv'] = h
                    elif 'coherence' in hl: col_map['coherence'] = h
                    elif 'flow' in hl and 'time' not in hl: col_map['flow'] = h
                    elif 'stress' in hl: col_map['stress'] = h
                    elif 'relax' in hl: col_map['relaxation'] = h
                    elif 'attention' in hl or 'focus' in hl: col_map['attention'] = h
                    elif 'time' in hl or 'date' in hl or 'stamp' in hl:
                        if 'timestamp' not in col_map:
                            col_map['timestamp'] = h

                count = 0
                for row in reader:
                    s = Session()
                    s.timestamp = row.get(col_map.get('timestamp', ''), '')
                    s.label = f"CSV Import #{count+1}"
                    for field in ['gamma','beta','alpha','theta','delta',
                                 'heart_rate','hrv','coherence','flow',
                                 'relaxation','attention']:
                        if field in col_map:
                            try:
                                val = float(row.get(col_map[field], '0') or '0')
                                setattr(s, field, val)
                            except ValueError:
                                pass
                    if 'stress' in col_map:
                        s.stress = row.get(col_map['stress'], 'Normal')
                    self.sessions.append(s)
                    count += 1

                messagebox.showinfo("CSV Loaded",
                    f"Loaded {count} sessions from CSV.\n"
                    f"Mapped columns: {', '.join(col_map.keys())}")
                self.refresh()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

    def load_conversations(self):
        """Load conversation logs and match to sessions by timestamp or order."""
        path = filedialog.askopenfilename(
            title="Load Conversation Logs",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"),
                       ("All files", "*.*")])
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    data = json.load(f)
                    # Handle various JSON structures
                    if isinstance(data, list):
                        for i, item in enumerate(data):
                            if i < len(self.sessions):
                                if isinstance(item, str):
                                    self.sessions[i].conversation = item
                                elif isinstance(item, dict):
                                    self.sessions[i].conversation = item.get('content',
                                        item.get('text', json.dumps(item, indent=2)))
                    elif isinstance(data, dict):
                        # Try to match by timestamp keys
                        for key, val in data.items():
                            for s in self.sessions:
                                if key in s.timestamp:
                                    s.conversation = str(val)
                else:
                    # Plain text — split by double newlines or timestamps
                    content = f.read()
                    chunks = content.split('\n\n')
                    for i, chunk in enumerate(chunks):
                        if i < len(self.sessions):
                            self.sessions[i].conversation = chunk.strip()

            messagebox.showinfo("Loaded", "Conversation logs attached to sessions.")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversations:\n{e}")

    def manual_entry(self):
        """Open manual session entry dialog."""
        win = tk.Toplevel(self.root)
        win.title("><^ Manual Session Entry")
        win.configure(bg=BG_DARK)
        win.geometry("500x650")

        entries = {}
        fields = [
            ("Timestamp", "timestamp", "2026-02-11 08:00"),
            ("Label", "label", "Session description"),
            ("Gamma %", "gamma", "10"),
            ("Beta %", "beta", "35"),
            ("Alpha %", "alpha", "25"),
            ("Theta %", "theta", "22"),
            ("Delta %", "delta", "8"),
            ("Heart Rate (BPM)", "heart_rate", "80"),
            ("HRV (ms)", "hrv", "25"),
            ("Coherence %", "coherence", "5"),
            ("Flow %", "flow", "20"),
            ("Stress", "stress", "Normal"),
            ("Relaxation", "relaxation", "50"),
            ("Attention", "attention", "60"),
            ("Sanding", "sanding", "3.0"),
            ("Platform", "platform", "CLAUDE"),
            ("Active Nodes", "nodes_active", "00, 11, 13"),
        ]

        row = 0
        for label, key, default in fields:
            tk.Label(win, text=label + ":", fg=FG_DIM, bg=BG_DARK,
                    font=("Courier", 9), anchor="e").grid(
                        row=row, column=0, sticky="e", padx=(10,5), pady=2)
            e = tk.Entry(win, bg=BG_MID, fg=FG_TEXT, font=("Courier", 9),
                        insertbackground=ACCENT_TEAL, relief="flat", width=30)
            e.insert(0, default)
            e.grid(row=row, column=1, sticky="w", padx=(0,10), pady=2)
            entries[key] = e
            row += 1

        # Conversation text area
        tk.Label(win, text="Conversation:", fg=FG_DIM, bg=BG_DARK,
                font=("Courier", 9), anchor="e").grid(
                    row=row, column=0, sticky="ne", padx=(10,5), pady=2)
        convo = tk.Text(win, bg=BG_MID, fg=FG_TEXT, font=("Courier", 9),
                       height=6, width=30, insertbackground=ACCENT_TEAL, relief="flat")
        convo.grid(row=row, column=1, sticky="w", padx=(0,10), pady=2)
        row += 1

        def save():
            s = Session()
            for key, e in entries.items():
                val = e.get().strip()
                if key in ('gamma','beta','alpha','theta','delta',
                          'heart_rate','hrv','coherence','flow',
                          'relaxation','attention','sanding'):
                    try:
                        setattr(s, key, float(val))
                    except ValueError:
                        setattr(s, key, 0)
                else:
                    setattr(s, key, val)
            s.conversation = convo.get("1.0", "end").strip()
            self.sessions.append(s)
            self.refresh()
            win.destroy()

        tk.Button(win, text="SAVE SESSION", command=save, bg=ACCENT_TEAL,
                 fg=BG_DARK, font=("Courier", 10, "bold"), relief="flat",
                 padx=20, pady=5).grid(row=row, column=0, columnspan=2, pady=15)

    def export_json(self):
        """Export all sessions as JSON for persistence."""
        if not self.sessions:
            messagebox.showwarning("Empty", "No sessions to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Sessions as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            data = [s.to_dict() for s in self.sessions]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Exported", f"Saved {len(self.sessions)} sessions to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def load_json(self):
        """Load previously exported session JSON."""
        path = filedialog.askopenfilename(
            title="Load Session JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for d in data:
                self.sessions.append(Session.from_dict(d))
            messagebox.showinfo("Loaded", f"Loaded {len(data)} sessions.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Load failed:\n{e}")

    def refresh(self):
        """Redraw everything."""
        self.session_count_var.set(f"Sessions: {len(self.sessions)}")
        self.redraw_timeline()
        if self.sessions:
            self.select_session(min(self.current_idx, len(self.sessions) - 1))

    def redraw_timeline(self):
        self.timeline.draw(self.sessions, self.timeline_metric.get())

    def select_session(self, idx):
        if not self.sessions:
            return
        self.current_idx = idx
        s = self.sessions[idx]

        self.session_label.config(text=f"[{idx+1}/{len(self.sessions)}] "
                                      f"{s.label or s.timestamp or 'Session'}")
        self.brainbar.draw(s)

        # Update vitals
        self.vital_labels["HR"].config(text=f"{s.heart_rate:.0f} BPM" if s.heart_rate else "—")
        self.vital_labels["HRV"].config(text=f"{s.hrv:.0f} ms" if s.hrv else "—",
            fg=WARN_RED if s.hrv and float(s.hrv) < 20 else FG_TEXT)
        self.vital_labels["Coherence"].config(text=f"{s.coherence:.0f}%")
        self.vital_labels["Flow"].config(text=f"{s.flow:.0f}%")
        self.vital_labels["Stress"].config(text=str(s.stress),
            fg=WARN_RED if 'high' in str(s.stress).lower() else FG_TEXT)
        self.vital_labels["Relaxation"].config(text=f"{s.relaxation:.0f}")
        self.vital_labels["Attention"].config(text=f"{s.attention:.0f}")

        # Sanding with color coding
        sand_color = ACCENT_TEAL if s.sanding < 3 else (
            ACCENT_CORAL if s.sanding < 6 else WARN_RED)
        self.vital_labels["Sanding"].config(text=f"S: {s.sanding:.2f}", fg=sand_color)
        self.vital_labels["Platform"].config(text=s.platform or "—")
        self.vital_labels["Nodes"].config(text=s.nodes_active or "—")

        # Conversation
        self.convo_text.config(state="normal")
        self.convo_text.delete("1.0", "end")
        self.convo_text.insert("1.0", s.conversation or "(No conversation data for this session)")
        self.convo_text.config(state="normal")

        self.nav_label.config(text=f"{idx+1} / {len(self.sessions)}")

    def prev_session(self):
        if self.sessions and self.current_idx > 0:
            self.select_session(self.current_idx - 1)

    def next_session(self):
        if self.sessions and self.current_idx < len(self.sessions) - 1:
            self.select_session(self.current_idx + 1)


def main():
    root = tk.Tk()
    app = NeuroSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
