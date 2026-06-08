import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import datetime
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk
import math
import threading
import time

# ─── Data Storage ────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.expanduser("~"), "wellness_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"entries": [], "mood_log": [], "streaks": 0, "last_date": ""}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Content ──────────────────────────────────────────────────────────────────
MOODS = [
    ("😄", "Amazing",    "#FFD700"),
    ("😊", "Happy",      "#90EE90"),
    ("😐", "Okay",       "#87CEEB"),
    ("😔", "Low",        "#DDA0DD"),
    ("😢", "Sad",        "#B0C4DE"),
    ("😰", "Anxious",    "#FFB347"),
    ("😤", "Frustrated", "#FA8072"),
    ("😴", "Exhausted",  "#C0C0C0"),
]

MOTIVATIONAL_QUOTES = [
    ("Every expert was once a beginner.\nEvery pro was once an amateur.\nStart before you're ready.", "— Helen Hayes"),
    ("You don't have to be great to start,\nbut you have to start to be great.", "— Zig Ziglar"),
    ("Mistakes are proof that\nyou are trying. Keep going.", "— Anonymous"),
    ("Your struggle today is\nyour strength tomorrow.", "— Unknown"),
    ("Growth and comfort\ncannot coexist. Choose growth.", "— Ginni Rometty"),
    ("Failure is not the opposite of success.\nIt is part of success.", "— Arianna Huffington"),
    ("You are not behind.\nYou are on your own path,\nmoving at your own pace.", "— Anonymous"),
    ("Rest if you must,\nbut never quit.", "— Edgar A. Guest"),
    ("The only way out is through.\nAnd you CAN get through this.", "— Robert Frost"),
    ("Hard days are the best,\nbecause that's when champions\nare made.", "— Gabby Douglas"),
]

HEALTHY_TIPS = [
    ("💧", "Hydrate!", "Drink a glass of water right now. Your brain is 75% water — nourish it."),
    ("🌬️", "Breathe Deep", "4 counts in. Hold 4. Out for 6. Repeat 5 times. Calm arrives."),
    ("🚶", "Move Your Body", "A 10-minute walk boosts mood more than a cup of coffee. Try it!"),
    ("🌙", "Sleep Matters", "7–9 hours is your brain's reset button. Protect your sleep."),
    ("🥗", "Eat to Think", "Brain food: nuts, berries, eggs. Fuel your mind, not just your body."),
    ("📵", "Digital Detox", "30 minutes off screens = lower cortisol. Your feed can wait."),
    ("🤝", "Connect", "Talk to one person today. Connection is medicine."),
    ("📓", "Write It Out", "Journaling for 5 minutes clears mental fog better than scrolling."),
    ("☀️", "Sunlight", "10 minutes of sun boosts serotonin. Step outside, even briefly."),
    ("🎵", "Music Heals", "Put on your favourite song. Music rewires stressed brains fast."),
]

FAILURE_LESSONS = [
    {
        "person": "J.K. Rowling",
        "failure": "Rejected by 12 publishers for Harry Potter.",
        "lesson": "Rejection is not the end. It's redirection. The 13th door opened the world."
    },
    {
        "person": "Albert Einstein",
        "failure": "Couldn't speak until age 4. Teachers called him slow.",
        "lesson": "Being different isn't a deficit. The world's greatest minds often start quietly."
    },
    {
        "person": "Thomas Edison",
        "failure": "Failed 10,000 times before the lightbulb.",
        "lesson": "You didn't fail 10,000 times. You found 10,000 ways that didn't work — yet."
    },
    {
        "person": "Oprah Winfrey",
        "failure": "Fired from her first TV job for being 'unfit for television'.",
        "lesson": "Someone's opinion of you is not your destiny. Define yourself."
    },
    {
        "person": "Steve Jobs",
        "failure": "Was fired from the company he built.",
        "lesson": "Being knocked down doesn't erase what you built. You always carry your skills."
    },
    {
        "person": "Walt Disney",
        "failure": "Fired for 'lacking imagination.' First studio went bankrupt.",
        "lesson": "Imagination can't be fired. Your vision survives every setback."
    },
]

AFFIRMATIONS = [
    "I am doing better than I think I am.",
    "My struggles do not define me — my resilience does.",
    "It's okay to not have everything figured out.",
    "I am worthy of rest, joy, and peace.",
    "Every day I show up is a victory.",
    "I am not behind. I am on my path.",
    "Asking for help is a sign of strength.",
    "I am allowed to take things one step at a time.",
    "My mental health matters as much as my grades.",
    "I belong here. I am enough.",
]

# ─── Image Generators ─────────────────────────────────────────────────────────
def make_gradient_bg(w, h, c1, c2, direction="vertical"):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    r1,g1,b1 = c1; r2,g2,b2 = c2
    for i in range(h if direction=="vertical" else w):
        t = i/(h-1) if direction=="vertical" else i/(w-1)
        r = int(r1 + t*(r2-r1)); g = int(g1 + t*(g2-g1)); b = int(b1 + t*(b2-b1))
        if direction=="vertical":
            draw.line([(0,i),(w,i)], fill=(r,g,b))
        else:
            draw.line([(i,0),(i,h)], fill=(r,g,b))
    return img

def make_breathing_frame(size, phase, max_r, label):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx = cy = size // 2
    r = int(max_r * phase)
    # Glow rings
    for ring in range(4, 0, -1):
        rr = r + ring * 8
        alpha = int(40 - ring * 8)
        draw.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(100, 200, 255, alpha))
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(80, 180, 255, 200), outline=(255,255,255,180), width=3)
    return ImageTk.PhotoImage(img)

# ─── App ──────────────────────────────────────────────────────────────────────
class WellnessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌱 MindBloom – Student Wellness")
        self.geometry("900x680")
        self.configure(bg="#0d1117")
        self.resizable(True, True)
        self.minsize(800, 600)

        self.data = load_data()
        self._update_streak()

        self.current_page = None
        self._build_fonts()
        self._build_sidebar()
        self._build_content_area()
        self.show_page("home")

    def _build_fonts(self):
        self.f_title  = ("Georgia", 26, "bold")
        self.f_head   = ("Georgia", 18, "bold")
        self.f_sub    = ("Helvetica", 13)
        self.f_body   = ("Helvetica", 12)
        self.f_small  = ("Helvetica", 10)
        self.f_emoji  = ("Segoe UI Emoji", 28) if os.name=="nt" else ("TkDefaultFont", 28)

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#161b22", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg="#1f6feb", height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="🌱 MindBloom", font=("Georgia", 15, "bold"),
                 bg="#1f6feb", fg="white").pack(expand=True)

        # Streak badge
        self.streak_label = tk.Label(self.sidebar,
            text=f"🔥 {self.data.get('streaks',0)}-day streak",
            font=self.f_small, bg="#161b22", fg="#f0a500", pady=8)
        self.streak_label.pack(fill="x", padx=10)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=10, pady=5)

        nav_items = [
            ("🏠", "Home",          "home"),
            ("😊", "Mood Tracker",  "mood"),
            ("📓", "My Journal",    "journal"),
            ("💪", "Learn & Grow",  "learn"),
            ("🌿", "Healthy Life",  "health"),
            ("🫁", "Breathe",       "breathe"),
            ("✨", "Affirmations",  "affirm"),
        ]
        self.nav_buttons = {}
        for icon, label, key in nav_items:
            btn = tk.Button(self.sidebar, text=f"  {icon}  {label}",
                font=self.f_body, anchor="w", bg="#161b22", fg="#c9d1d9",
                activebackground="#21262d", activeforeground="white",
                relief="flat", bd=0, padx=10, pady=10, cursor="hand2",
                command=lambda k=key: self.show_page(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # Bottom quote
        quote_text = random.choice(AFFIRMATIONS)
        tk.Label(self.sidebar, text=f'"{quote_text}"',
                 font=("Georgia", 9, "italic"), bg="#161b22", fg="#8b949e",
                 wraplength=170, justify="center", pady=10).pack(side="bottom", padx=8, pady=10)

    def _build_content_area(self):
        self.content = tk.Frame(self, bg="#0d1117")
        self.content.pack(side="right", fill="both", expand=True)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _nav_highlight(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg="#21262d", fg="white",
                              font=("Helvetica", 12, "bold"))
            else:
                btn.configure(bg="#161b22", fg="#c9d1d9",
                              font=self.f_body)

    def show_page(self, key):
        self.current_page = key
        self._nav_highlight(key)
        self._clear_content()
        pages = {
            "home":    self.page_home,
            "mood":    self.page_mood,
            "journal": self.page_journal,
            "learn":   self.page_learn,
            "health":  self.page_health,
            "breathe": self.page_breathe,
            "affirm":  self.page_affirm,
        }
        pages[key]()

    def _update_streak(self):
        today = str(datetime.date.today())
        if self.data.get("last_date") != today:
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
            if self.data.get("last_date") == yesterday:
                self.data["streaks"] = self.data.get("streaks", 0) + 1
            elif self.data.get("last_date") != today:
                self.data["streaks"] = 1
            self.data["last_date"] = today
            save_data(self.data)

    # ── Scrollable frame helper ──────────────────────────────────────────────
    def _scrollable(self):
        outer = tk.Frame(self.content, bg="#0d1117")
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg="#0d1117", highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#0d1117")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120),"units"))
        return inner

    # ── Page Header ──────────────────────────────────────────────────────────
    def _header(self, parent, emoji, title, subtitle):
        hf = tk.Frame(parent, bg="#161b22", pady=20)
        hf.pack(fill="x", padx=0)
        tk.Label(hf, text=emoji, font=("TkDefaultFont", 32),
                 bg="#161b22", fg="white").pack()
        tk.Label(hf, text=title, font=self.f_title,
                 bg="#161b22", fg="white").pack()
        tk.Label(hf, text=subtitle, font=self.f_sub,
                 bg="#161b22", fg="#8b949e").pack(pady=(4,0))

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: HOME
    # ─────────────────────────────────────────────────────────────────────────
    def page_home(self):
        frame = self._scrollable()
        self._header(frame, "🌱", "Welcome Back", self._greeting())

        # Quote card
        q, attr = random.choice(MOTIVATIONAL_QUOTES)
        qf = tk.Frame(frame, bg="#1f6feb", padx=30, pady=25)
        qf.pack(fill="x", padx=25, pady=15)
        tk.Label(qf, text=q, font=("Georgia", 13, "italic"),
                 bg="#1f6feb", fg="white", wraplength=560, justify="center").pack()
        tk.Label(qf, text=attr, font=self.f_small,
                 bg="#1f6feb", fg="#c0d8ff").pack(pady=(8,0))

        # You are not alone section
        alone_f = tk.Frame(frame, bg="#0d3b2e", padx=25, pady=20)
        alone_f.pack(fill="x", padx=25, pady=5)
        tk.Label(alone_f, text="💚  You Are Not Alone",
                 font=("Georgia", 15, "bold"), bg="#0d3b2e", fg="#3fb950").pack()
        tk.Label(alone_f,
            text="Whatever you're carrying right now — stress, failure, loneliness, confusion — "
                 "thousands of students feel exactly what you feel. You are not broken. "
                 "You are human. And you are stronger than you know.",
            font=self.f_body, bg="#0d3b2e", fg="#b3f0c0", wraplength=580,
            justify="center").pack(pady=(10,0))

        # Quick action cards
        tk.Label(frame, text="Where do you want to begin today?",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=15).pack()

        cards = [
            ("😊", "Track\nMood",  "mood",    "#1a3a5c"),
            ("📓", "Write\nFeeling","journal", "#2d1b3d"),
            ("💪", "Learn from\nFailure","learn","#1e3a1e"),
            ("🫁", "Breathe &\nRelax","breathe","#3a2a0d"),
        ]
        cf = tk.Frame(frame, bg="#0d1117")
        cf.pack(padx=25, pady=10)
        for i, (em, txt, pg, col) in enumerate(cards):
            card = tk.Frame(cf, bg=col, width=160, height=130,
                            cursor="hand2", padx=10, pady=15)
            card.grid(row=0, column=i, padx=8)
            card.pack_propagate(False)
            tk.Label(card, text=em, font=("TkDefaultFont", 26),
                     bg=col, fg="white").pack()
            tk.Label(card, text=txt, font=("Helvetica", 11, "bold"),
                     bg=col, fg="white", justify="center").pack()
            card.bind("<Button-1>", lambda e, p=pg: self.show_page(p))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, p=pg: self.show_page(p))

        # Daily tip
        tip = random.choice(HEALTHY_TIPS)
        tf = tk.Frame(frame, bg="#1c1f26", padx=25, pady=20)
        tf.pack(fill="x", padx=25, pady=15)
        tk.Label(tf, text=f"{tip[0]} Today's Tip: {tip[1]}",
                 font=("Helvetica", 13, "bold"), bg="#1c1f26", fg="#f0a500").pack(anchor="w")
        tk.Label(tf, text=tip[2], font=self.f_body,
                 bg="#1c1f26", fg="#c9d1d9", wraplength=580, justify="left").pack(anchor="w", pady=5)

    def _greeting(self):
        h = datetime.datetime.now().hour
        if h < 12:   return "Good morning! ☀️ A new day, a new chance."
        elif h < 17: return "Good afternoon! 🌤️ You're doing great."
        else:        return "Good evening! 🌙 Rest is also progress."

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: MOOD TRACKER
    # ─────────────────────────────────────────────────────────────────────────
    def page_mood(self):
        frame = self._scrollable()
        self._header(frame, "😊", "Mood Tracker",
                     "How are you feeling right now? Be honest — this is your safe space.")

        tk.Label(frame, text="Tap your mood:",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=10).pack()

        mood_grid = tk.Frame(frame, bg="#0d1117")
        mood_grid.pack(padx=20)
        self.selected_mood = tk.StringVar()

        for i, (em, label, col) in enumerate(MOODS):
            r, c = divmod(i, 4)
            mf = tk.Frame(mood_grid, bg=col, width=140, height=110,
                          cursor="hand2", padx=8, pady=10)
            mf.grid(row=r, column=c, padx=8, pady=8)
            mf.pack_propagate(False)
            tk.Label(mf, text=em, font=("TkDefaultFont", 28),
                     bg=col, fg="white").pack()
            tk.Label(mf, text=label, font=("Helvetica", 12, "bold"),
                     bg=col, fg="white").pack()
            mf.bind("<Button-1>", lambda e, l=label, c2=col: self._select_mood(l, c2, mood_grid))
            for child in mf.winfo_children():
                child.bind("<Button-1>", lambda e, l=label, c2=col: self._select_mood(l, c2, mood_grid))

        self.mood_note_label = tk.Label(frame, text="", font=self.f_body,
                                        bg="#0d1117", fg="#8b949e")
        self.mood_note_label.pack(pady=5)

        # Mood note
        tk.Label(frame, text="Add a note about your mood (optional):",
                 font=self.f_body, bg="#0d1117", fg="#c9d1d9").pack(anchor="w", padx=30, pady=(15,5))
        self.mood_text = tk.Text(frame, height=3, width=60, font=self.f_body,
                                 bg="#161b22", fg="white", insertbackground="white",
                                 relief="flat", padx=10, pady=8)
        self.mood_text.pack(padx=30)

        tk.Button(frame, text="  Log My Mood  ", font=("Helvetica", 13, "bold"),
                  bg="#1f6feb", fg="white", relief="flat", padx=20, pady=10,
                  cursor="hand2", command=self._log_mood).pack(pady=20)

        # Recent moods
        tk.Label(frame, text="Recent Mood History",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=5).pack()

        history = self.data.get("mood_log", [])[-7:]
        if not history:
            tk.Label(frame, text="No mood entries yet. Log your first one above!",
                     font=self.f_body, bg="#0d1117", fg="#8b949e").pack(pady=10)
        else:
            for entry in reversed(history):
                self._mood_entry_card(frame, entry)

    def _select_mood(self, label, color, grid):
        self.selected_mood.set(label)
        self.mood_note_label.config(
            text=f"✓ Selected: {label} — Your feelings are valid.",
            fg=color)

    def _log_mood(self):
        mood = self.selected_mood.get()
        if not mood:
            messagebox.showinfo("Choose a Mood", "Please tap a mood first!")
            return
        note = self.mood_text.get("1.0", "end").strip()
        entry = {
            "date": str(datetime.datetime.now().strftime("%b %d, %Y  %H:%M")),
            "mood": mood,
            "note": note
        }
        self.data.setdefault("mood_log", []).append(entry)
        save_data(self.data)
        messagebox.showinfo("Mood Logged ✓",
            f"Feeling {mood} — that's okay! Acknowledging how you feel is the first step to feeling better.")
        self.show_page("mood")

    def _mood_entry_card(self, parent, entry):
        cf = tk.Frame(parent, bg="#161b22", padx=15, pady=10)
        cf.pack(fill="x", padx=30, pady=4)
        row = tk.Frame(cf, bg="#161b22")
        row.pack(fill="x")
        tk.Label(row, text=entry["mood"], font=("Helvetica", 16, "bold"),
                 bg="#161b22", fg="#f0a500").pack(side="left")
        tk.Label(row, text=f"  {entry['date']}", font=self.f_small,
                 bg="#161b22", fg="#8b949e").pack(side="left")
        if entry.get("note"):
            tk.Label(cf, text=entry["note"], font=self.f_small,
                     bg="#161b22", fg="#c9d1d9", wraplength=500,
                     justify="left").pack(anchor="w", pady=3)

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: JOURNAL
    # ─────────────────────────────────────────────────────────────────────────
    def page_journal(self):
        frame = self._scrollable()
        self._header(frame, "📓", "My Journal",
                     "Write freely. This space belongs to you alone.")

        tab_frame = tk.Frame(frame, bg="#161b22", pady=5)
        tab_frame.pack(fill="x", padx=20, pady=10)

        self.journal_tab = tk.StringVar(value="good")

        good_btn = tk.Button(tab_frame, text="✅  What Went GOOD",
            font=("Helvetica", 12, "bold"), bg="#1e4620", fg="#3fb950",
            activebackground="#2ea043", relief="flat", padx=15, pady=8,
            cursor="hand2", command=lambda: self._switch_journal("good"))
        good_btn.pack(side="left", padx=8)

        bad_btn = tk.Button(tab_frame, text="🌧️  What Was Hard",
            font=("Helvetica", 12, "bold"), bg="#3d1a1a", fg="#f85149",
            activebackground="#6e2b2b", relief="flat", padx=15, pady=8,
            cursor="hand2", command=lambda: self._switch_journal("bad"))
        bad_btn.pack(side="left", padx=8)

        # Prompt area
        self.journal_prompt_label = tk.Label(frame, font=("Georgia", 12, "italic"),
                                              bg="#0d1117", fg="#8b949e", wraplength=600,
                                              justify="center", pady=8)
        self.journal_prompt_label.pack()
        self._switch_journal("good", update_only=True)

        self.journal_text = tk.Text(frame, height=10, width=65,
                                     font=("Georgia", 12),
                                     bg="#161b22", fg="white",
                                     insertbackground="white",
                                     relief="flat", padx=15, pady=12,
                                     wrap="word")
        self.journal_text.pack(padx=30, pady=5)

        tk.Button(frame, text="  Save Entry  ", font=("Helvetica", 13, "bold"),
                  bg="#1f6feb", fg="white", relief="flat", padx=20, pady=10,
                  cursor="hand2", command=self._save_journal).pack(pady=15)

        # Past entries
        tk.Label(frame, text="Past Entries", font=self.f_head,
                 bg="#0d1117", fg="#c9d1d9", pady=5).pack()

        entries = self.data.get("entries", [])[-5:]
        if not entries:
            tk.Label(frame, text="Your journal is empty. Start writing — even one line helps.",
                     font=self.f_body, bg="#0d1117", fg="#8b949e").pack(pady=10)
        else:
            for entry in reversed(entries):
                self._journal_entry_card(frame, entry)

    def _switch_journal(self, tab, update_only=False):
        if not update_only:
            self.journal_tab.set(tab)
        prompts = {
            "good": "💚 What made you smile today? A small win? A kind word? Write it. You deserve to celebrate.",
            "bad": "🌧️ What was tough today? Write it out. Getting it on paper takes it out of your head.",
        }
        self.journal_prompt_label.config(text=prompts[self.journal_tab.get()])

    def _save_journal(self):
        text = self.journal_text.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Nothing Written", "Write at least a few words. Even 'today was hard' counts.")
            return
        entry = {
            "date": str(datetime.datetime.now().strftime("%b %d, %Y  %H:%M")),
            "type": self.journal_tab.get(),
            "text": text,
        }
        self.data.setdefault("entries", []).append(entry)
        save_data(self.data)

        msg = (
            "🌱 Saved! Writing about what went well builds gratitude and resilience."
            if entry["type"] == "good" else
            "💙 Saved. You faced something hard and you're still here. That's strength."
        )
        messagebox.showinfo("Entry Saved ✓", msg)
        self.show_page("journal")

    def _journal_entry_card(self, parent, entry):
        col = "#1e4620" if entry.get("type") == "good" else "#3d1a1a"
        icon = "✅" if entry.get("type") == "good" else "🌧️"
        cf = tk.Frame(parent, bg=col, padx=15, pady=12)
        cf.pack(fill="x", padx=30, pady=5)
        header = tk.Frame(cf, bg=col)
        header.pack(fill="x")
        tk.Label(header, text=f"{icon}  {entry['date']}",
                 font=self.f_small, bg=col, fg="#8b949e").pack(side="left")
        tk.Label(cf, text=entry["text"][:200] + ("..." if len(entry["text"])>200 else ""),
                 font=self.f_body, bg=col, fg="white",
                 wraplength=540, justify="left").pack(anchor="w", pady=5)

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: LEARN & GROW (Failure lessons)
    # ─────────────────────────────────────────────────────────────────────────
    def page_learn(self):
        frame = self._scrollable()
        self._header(frame, "💪", "Learn & Grow",
                     "Failure is not your enemy. It's your most honest teacher.")

        # Fear vs Growth reframe
        ff = tk.Frame(frame, bg="#1a1a2e", padx=25, pady=20)
        ff.pack(fill="x", padx=25, pady=10)
        tk.Label(ff, text="🔄 Reframe Your Thinking",
                 font=("Georgia", 15, "bold"), bg="#1a1a2e", fg="#a78bfa").pack(anchor="w")

        reframes = [
            ("❌  Fear says:",  '"I failed, so I am not good enough."',   "#f85149"),
            ("✅  Growth says:", '"I failed, so now I know what to fix."', "#3fb950"),
            ("❌  Fear says:",  '"What will people think?"',              "#f85149"),
            ("✅  Growth says:", '"What can I learn from this?"',          "#3fb950"),
            ("❌  Fear says:",  '"I should give up."',                    "#f85149"),
            ("✅  Growth says:", '"Every expert failed here first."',      "#3fb950"),
        ]
        for label, text, col in reframes:
            row = tk.Frame(ff, bg="#1a1a2e")
            row.pack(anchor="w", pady=3)
            tk.Label(row, text=label, font=("Helvetica", 11, "bold"),
                     bg="#1a1a2e", fg=col, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=text, font=("Georgia", 11, "italic"),
                     bg="#1a1a2e", fg="#c9d1d9").pack(side="left")

        # Famous failure stories
        tk.Label(frame, text="Famous Failures Who Changed the World",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=10).pack()

        for story in FAILURE_LESSONS:
            sf = tk.Frame(frame, bg="#161b22", padx=20, pady=15)
            sf.pack(fill="x", padx=25, pady=6)
            tk.Label(sf, text=story["person"],
                     font=("Georgia", 14, "bold"), bg="#161b22", fg="#f0a500").pack(anchor="w")
            tk.Label(sf, text=f"💔 {story['failure']}",
                     font=self.f_body, bg="#161b22", fg="#f85149",
                     wraplength=560, justify="left").pack(anchor="w", pady=3)
            tk.Label(sf, text=f"💡 {story['lesson']}",
                     font=("Georgia", 11, "italic"), bg="#161b22", fg="#3fb950",
                     wraplength=560, justify="left").pack(anchor="w")

        # Thought about giving up
        tf = tk.Frame(frame, bg="#0d2a1a", padx=25, pady=25)
        tf.pack(fill="x", padx=25, pady=15)
        tk.Label(tf, text="💚 If You're Feeling Like You Can't Go On",
                 font=("Georgia", 14, "bold"), bg="#0d2a1a", fg="#3fb950").pack()
        tk.Label(tf,
            text="You are not alone. Many students before you hit a wall so dark it felt permanent. "
                 "It was not. What you feel right now is real, but it is also temporary.\n\n"
                 "Reach out to one person today — a friend, a family member, a teacher, "
                 "a counselor. Just one. You don't have to explain everything. Just say: "
                 '"I\'m having a really hard time." That one sentence can change everything.',
            font=self.f_body, bg="#0d2a1a", fg="#b3f0c0",
            wraplength=580, justify="center").pack(pady=10)
        tk.Label(tf, text="You showed up today. That already makes you brave.",
                 font=("Georgia", 13, "bold italic"), bg="#0d2a1a", fg="white").pack(pady=5)

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: HEALTHY LIFESTYLE
    # ─────────────────────────────────────────────────────────────────────────
    def page_health(self):
        frame = self._scrollable()
        self._header(frame, "🌿", "Healthy Lifestyle",
                     "Your body and mind are connected. Care for both.")

        # Checklist
        tk.Label(frame, text="Today's Wellness Checklist",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=10).pack()

        checklist_items = [
            "💧 Drank 6–8 glasses of water",
            "🥗 Had a nourishing meal",
            "🚶 Moved my body (walk, stretch, dance)",
            "🌙 Got 7–9 hours of sleep last night",
            "📵 Took a break from screens",
            "🤝 Connected with someone I care about",
            "🧘 Had a quiet moment for myself",
            "😄 Did something that made me smile",
        ]

        self.check_vars = []
        cf = tk.Frame(frame, bg="#161b22", padx=20, pady=15)
        cf.pack(fill="x", padx=25, pady=5)
        for item in checklist_items:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(cf, text=item, variable=var,
                                font=self.f_body, bg="#161b22", fg="#c9d1d9",
                                selectcolor="#1f6feb", activebackground="#161b22",
                                activeforeground="white", anchor="w")
            cb.pack(anchor="w", pady=4)
            self.check_vars.append(var)

        tk.Button(frame, text="  Check My Score  ", font=("Helvetica", 13, "bold"),
                  bg="#2ea043", fg="white", relief="flat", padx=20, pady=10,
                  cursor="hand2", command=self._wellness_score).pack(pady=15)

        # Tips cards
        tk.Label(frame, text="Daily Wellness Tips",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=5).pack()

        colors = ["#1a3a5c","#2d1b3d","#1e3a1e","#3a2a0d","#2a1a1a","#1a2a2a","#2a2a1a","#1a1a3a","#2a1a3a","#1a3a2a"]
        for i, tip in enumerate(HEALTHY_TIPS):
            tf = tk.Frame(frame, bg=colors[i % len(colors)], padx=20, pady=15)
            tf.pack(fill="x", padx=25, pady=5)
            tk.Label(tf, text=f"{tip[0]}  {tip[1]}",
                     font=("Helvetica", 13, "bold"),
                     bg=colors[i % len(colors)], fg="white").pack(anchor="w")
            tk.Label(tf, text=tip[2], font=self.f_body,
                     bg=colors[i % len(colors)], fg="#c9d1d9",
                     wraplength=560, justify="left").pack(anchor="w", pady=5)

    def _wellness_score(self):
        score = sum(v.get() for v in self.check_vars)
        total = len(self.check_vars)
        pct = int(score / total * 100)
        msg = (
            "🌟 100% — You're absolutely thriving today!" if pct == 100 else
            "💚 Great day! Keep it up!" if pct >= 75 else
            "😊 Solid effort! Small steps every day." if pct >= 50 else
            "🌱 That's okay — even 1 tick is a win. Tomorrow is a new chance."
        )
        messagebox.showinfo(f"Wellness Score: {pct}%",
            f"You checked {score} out of {total} items.\n\n{msg}")

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: BREATHING EXERCISE
    # ─────────────────────────────────────────────────────────────────────────
    def page_breathe(self):
        self._header(self.content, "🫁", "Breathe & Relax",
                     "Box breathing: used by military to calm the mind in seconds.")

        self.breathe_label = tk.Label(self.content, text="Press Start to begin",
                                       font=("Georgia", 22, "bold"),
                                       bg="#0d1117", fg="#87CEEB")
        self.breathe_label.pack(pady=10)

        self.breathe_canvas = tk.Canvas(self.content, width=280, height=280,
                                         bg="#0d1117", highlightthickness=0)
        self.breathe_canvas.pack()
        self._draw_breathe_circle(0.3)

        self.breathe_counter = tk.Label(self.content, text="",
                                         font=("Georgia", 48, "bold"),
                                         bg="#0d1117", fg="white")
        self.breathe_counter.pack()

        self.breathe_tip = tk.Label(self.content,
            text="Inhale → Hold → Exhale → Hold. Repeat 4 times.\nYour nervous system will thank you.",
            font=("Helvetica", 12), bg="#0d1117", fg="#8b949e",
            justify="center")
        self.breathe_tip.pack(pady=5)

        self.breathe_running = False
        self.breathe_btn = tk.Button(self.content, text="  ▶  Start Breathing  ",
                                      font=("Helvetica", 13, "bold"),
                                      bg="#1f6feb", fg="white", relief="flat",
                                      padx=20, pady=12, cursor="hand2",
                                      command=self._toggle_breathe)
        self.breathe_btn.pack(pady=10)

        afm = tk.Frame(self.content, bg="#0d2a1a", padx=25, pady=15)
        afm.pack(fill="x", padx=30, pady=15)
        tk.Label(afm, text="💙 When anxiety peaks, remember:",
                 font=("Helvetica", 12, "bold"), bg="#0d2a1a", fg="#3fb950").pack(anchor="w")
        tk.Label(afm,
            text="Anxiety cannot hurt you. It is your body trying to protect you.\n"
                 "Breathing slowly tells your brain: 'I am safe. The threat has passed.'\n"
                 "You are in control. One breath at a time.",
            font=("Georgia", 11, "italic"), bg="#0d2a1a", fg="#b3f0c0",
            justify="left").pack(anchor="w", pady=8)

    def _draw_breathe_circle(self, scale):
        self.breathe_canvas.delete("all")
        cx, cy, max_r = 140, 140, 110
        r = int(max_r * scale)
        for i in range(5, 0, -1):
            rr = r + i*10
            alpha_hex = format(max(0, 60 - i*12), '02x')
            try:
                self.breathe_canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                    fill="", outline=f"#87CEEB{alpha_hex}", width=2)
            except:
                pass
        self.breathe_canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
            fill="#1a3a5c", outline="#87CEEB", width=3)

    def _toggle_breathe(self):
        if self.breathe_running:
            self.breathe_running = False
            self.breathe_btn.config(text="  ▶  Start Breathing  ")
            self.breathe_label.config(text="Press Start to begin")
            self.breathe_counter.config(text="")
            self._draw_breathe_circle(0.3)
        else:
            self.breathe_running = True
            self.breathe_btn.config(text="  ⏹  Stop  ")
            threading.Thread(target=self._breathe_cycle, daemon=True).start()

    def _breathe_cycle(self):
        phases = [("Inhale…", 4, 1.0), ("Hold…", 4, 1.0),
                  ("Exhale…", 4, 0.3), ("Hold…", 4, 0.3)]
        while self.breathe_running:
            for label, secs, scale_to in phases:
                if not self.breathe_running: return
                self.after(0, self.breathe_label.config, {"text": label})
                start_scale = 0.3 if label=="Inhale…" else (1.0 if label in ["Hold…","Exhale…"] else 0.3)
                for t in range(secs):
                    if not self.breathe_running: return
                    self.after(0, self.breathe_counter.config, {"text": str(secs - t)})
                    steps = 20
                    for s in range(steps):
                        if not self.breathe_running: return
                        progress = s / steps
                        sc = start_scale + (scale_to - start_scale) * progress
                        self.after(0, self._draw_breathe_circle, sc)
                        time.sleep(1/steps)

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE: AFFIRMATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def page_affirm(self):
        frame = self._scrollable()
        self._header(frame, "✨", "Affirmations",
                     "Your mind believes what you tell it. Tell it the truth.")

        self.affirm_card = tk.Frame(frame, bg="#1f2937", padx=40, pady=40)
        self.affirm_card.pack(fill="x", padx=30, pady=20)
        self.affirm_text = tk.Label(self.affirm_card,
            text=random.choice(AFFIRMATIONS),
            font=("Georgia", 18, "bold"), bg="#1f2937", fg="white",
            wraplength=500, justify="center")
        self.affirm_text.pack()

        tk.Button(frame, text="  ✨ New Affirmation  ", font=("Helvetica", 13, "bold"),
                  bg="#7c3aed", fg="white", relief="flat", padx=20, pady=10,
                  cursor="hand2",
                  command=lambda: self.affirm_text.config(text=random.choice(AFFIRMATIONS))
                  ).pack(pady=10)

        tk.Label(frame, text="All Affirmations for You",
                 font=self.f_head, bg="#0d1117", fg="#c9d1d9", pady=10).pack()

        colors = ["#1f1a3d", "#0d2a1a", "#1a1a0d", "#1a0d1a", "#0d1a2a",
                  "#2a1a0d", "#1a2a0d", "#0d1a1a", "#2a0d1a", "#1a2a2a"]
        for i, aff in enumerate(AFFIRMATIONS):
            af = tk.Frame(frame, bg=colors[i % len(colors)], padx=20, pady=15)
            af.pack(fill="x", padx=25, pady=4)
            tk.Label(af, text=f"✦  {aff}",
                     font=("Georgia", 12, "italic"), bg=colors[i % len(colors)],
                     fg="white", wraplength=560, justify="left").pack(anchor="w")

        # Closing message
        cf = tk.Frame(frame, bg="#0d2a1a", padx=30, pady=25)
        cf.pack(fill="x", padx=25, pady=15)
        tk.Label(cf, text="💚 A Message from MindBloom",
                 font=("Georgia", 15, "bold"), bg="#0d2a1a", fg="#3fb950").pack()
        tk.Label(cf,
            text="You are not just a student. You are a whole, complex, worthy human being.\n"
                 "Your value is not measured in grades, achievements, or what others think.\n\n"
                 "On the hard days — and there will be hard days — remember:\n"
                 "You are still here. And that matters more than you know.",
            font=("Georgia", 12), bg="#0d2a1a", fg="#b3f0c0",
            wraplength=560, justify="center").pack(pady=12)


if __name__ == "__main__":
    app = WellnessApp()
    app.mainloop()
