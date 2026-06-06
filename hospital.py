import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime, date
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",         
    "password": "um03ar65",    
    "database": "hospital_db"
}

#  COLOR PALETTE  (Deep Medical Blue + Gold)
BG      = "#0A0F1E"
PANEL   = "#111827"
CARD    = "#1A2235"
BORDER  = "#1E3A5F"
ACCENT  = "#00B4D8"
ACCENT2 = "#FFD700"
TEXT    = "#E8F4FD"
SUBTEXT = "#7B9DBF"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER  = "#EF4444"
HOVER   = "#162032"

#  DATABASE CONNECTION  (no auto-create)
def get_connection():
    """Connect to MySQL. DB must already exist (created via hospital_db.sql)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror(
            "Database Error",
            f"Cannot connect to MySQL.\n\nError: {e}\n\n"
            "Make sure you have:\n"
            "  1. Run hospital_db.sql in MySQL Workbench\n"
            "  2. Set the correct credentials in DB_CONFIG (top of hospital.py)"
        )
        return None

#  VALIDATION HELPERS

def validate_alpha_name(name: str) -> tuple[bool, str]:
    """Name must contain only letters, spaces, dots, and hyphens (no digits)."""
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    if not re.match(r"^[A-Za-z][A-Za-z\s.\-']{1,}$", name):
        return False, "Name must contain letters only (spaces, dots, hyphens allowed)."
    return True, ""

def validate_phone(phone: str) -> tuple[bool, str]:
    phone = phone.strip()
    if not re.match(r"^[\d\+\-\s]{7,15}$", phone):
        return False, "Phone must be 7–15 digits (+ and - allowed)."
    if not re.search(r"\d{7,}", re.sub(r"[\+\-\s]", "", phone)):
        return False, "Phone must contain at least 7 numeric digits."
    return True, ""

def validate_email(email: str) -> tuple[bool, str]:
    if not email.strip():
        return True, ""   # optional
    if not re.match(r"^[\w\.\-]+@[\w\.\-]+\.\w{2,}$", email.strip()):
        return False, "Invalid email format (e.g. name@domain.com)."
    return True, ""

def validate_age(age: str) -> tuple[bool, str]:
    try:
        a = int(age.strip())
        if not (1 <= a <= 149):
            raise ValueError
        return True, ""
    except ValueError:
        return False, "Age must be a whole number between 1 and 149."

def validate_positive_float(val: str, label: str) -> tuple[bool, str]:
    try:
        f = float(val.strip())
        if f < 0:
            raise ValueError
        return True, ""
    except ValueError:
        return False, f"{label} must be a non-negative number."

def validate_non_negative_int(val: str, label: str) -> tuple[bool, str]:
    try:
        i = int(val.strip())
        if i < 0:
            raise ValueError
        return True, ""
    except ValueError:
        return False, f"{label} must be a non-negative whole number."

def validate_date(d: str) -> tuple[bool, str]:
    try:
        datetime.strptime(d.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format (e.g. 2025-01-30)."

def validate_time(t: str) -> tuple[bool, str]:
    try:
        datetime.strptime(t.strip(), "%H:%M")
        return True, ""
    except ValueError:
        return False, "Time must be in HH:MM format (e.g. 09:30)."

def validate_alpha_only(val: str, label: str) -> tuple[bool, str]:
    """Allows letters, spaces, and hyphens — no digits."""
    val = val.strip()
    if len(val) < 2:
        return False, f"{label} must be at least 2 characters."
    if not re.match(r"^[A-Za-z][A-Za-z\s\-]+$", val):
        return False, f"{label} must contain letters only."
    return True, ""

def collect_errors(checks: list) -> list[str]:
    """Run a list of (ok, msg) pairs, collect all failure messages."""
    return [msg for ok, msg in checks if not ok]

#  STYLED WIDGET HELPERS
def make_entry(parent, placeholder="", width=25, show=""):
    frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                     highlightthickness=1, bd=0)
    e = tk.Entry(frame, bg=CARD, fg=SUBTEXT, insertbackground=ACCENT,
                 relief="flat", font=("Consolas", 11), width=width,
                 show=show, bd=4)
    e.pack(fill="x")
    e._placeholder = placeholder
    e._active = False

    def on_focus_in(_):
        if not e._active:
            e.delete(0, "end")
            e.config(fg=TEXT)
            e._active = True
        frame.config(highlightbackground=ACCENT)

    def on_focus_out(_):
        if not e.get():
            e.insert(0, placeholder)
            e.config(fg=SUBTEXT)
            e._active = False
        frame.config(highlightbackground=BORDER)

    e.insert(0, placeholder)
    e.bind("<FocusIn>", on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    e.frame = frame
    return e

def get_val(entry) -> str:
    v = entry.get()
    return "" if v == entry._placeholder else v.strip()

def make_btn(parent, text, command, color=ACCENT, fg=BG, width=16):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, activebackground=ACCENT2,
                    activeforeground=BG, relief="flat", bd=0,
                    font=("Segoe UI", 10, "bold"), width=width,
                    cursor="hand2", pady=7)
    btn.bind("<Enter>", lambda _: btn.config(bg=ACCENT2, fg=BG))
    btn.bind("<Leave>", lambda _: btn.config(bg=color, fg=fg))
    return btn

def make_label(parent, text, size=11, color=TEXT, bold=False):
    style = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=CARD, fg=color,
                    font=("Segoe UI", size, style))

def section_title(parent, text):
    f = tk.Frame(parent, bg=CARD)
    f.pack(fill="x", pady=(18, 8))
    tk.Label(f, text="▸ " + text, bg=CARD, fg=ACCENT2,
             font=("Segoe UI", 13, "bold")).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x",
                                          expand=True, padx=10, pady=6)

def make_treeview(parent, columns, headings):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
        background=PANEL, foreground=TEXT,
        rowheight=30, fieldbackground=PANEL,
        borderwidth=0, font=("Consolas", 10))
    style.configure("Custom.Treeview.Heading",
        background=BORDER, foreground=ACCENT2,
        relief="flat", font=("Segoe UI", 10, "bold"))
    style.map("Custom.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", BG)])

    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    sb  = ttk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    sbx = ttk.Scrollbar(frame, orient="horizontal")
    sbx.pack(side="bottom", fill="x")

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=sb.set, xscrollcommand=sbx.set)
    for col, head in zip(columns, headings):
        tree.heading(col, text=head)
        tree.column(col, anchor="center", width=130, minwidth=80)
    sb.config(command=tree.yview)
    sbx.config(command=tree.xview)
    tree.pack(fill="both", expand=True)
    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background=CARD)
    return tree

def search_bar(parent, sv, load_fn):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", padx=10, pady=(10, 5))
    tk.Label(f, text="🔍", bg=BG, fg=ACCENT,
             font=("Segoe UI", 13)).pack(side="left")
    tk.Entry(f, textvariable=sv, bg=CARD, fg=TEXT,
             insertbackground=ACCENT, relief="flat", font=("Consolas", 11),
             bd=5, highlightbackground=BORDER, highlightthickness=1
             ).pack(side="left", fill="x", expand=True, ipady=3, padx=5)
    sv.trace("w", lambda *_: load_fn())
    make_btn(f, "Refresh", load_fn, width=10).pack(side="left")

#  ICONS
ICONS = {
    "Dashboard":    "🏥",
    "Patients":     "👤",
    "Doctors":      "🩺",
    "Appointments": "📅",
    "Rooms":        "🛏",
    "Billing":      "💰",
}

#  MAIN APPLICATION
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediCore — Hospital Management System")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.update_idletasks()
        w, h = 1300, 800
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self._build_ui()
        self.show_page("Dashboard")

    def _build_ui(self):
        # ── Sidebar ───────────────────────────
        self.sidebar = tk.Frame(self, bg=PANEL, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_f = tk.Frame(self.sidebar, bg=PANEL, pady=20)
        logo_f.pack(fill="x")
        tk.Label(logo_f, text="🏥", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 28)).pack()
        tk.Label(logo_f, text="MediCore", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(logo_f, text="Hospital Management", bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack()
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15)

        self.nav_btns = {}
        nav_f = tk.Frame(self.sidebar, bg=PANEL)
        nav_f.pack(fill="x", pady=10)
        for page in ICONS:
            icon = ICONS[page]
            btn = tk.Button(nav_f,
                text=f"  {icon}  {page}", anchor="w",
                command=lambda p=page: self.show_page(p),
                bg=PANEL, fg=SUBTEXT, activebackground=HOVER,
                activeforeground=ACCENT, relief="flat", bd=0,
                font=("Segoe UI", 11), cursor="hand2",
                padx=10, pady=12)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HOVER, fg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn, pg=page:
                     b.config(bg=PANEL if self._active != pg else HOVER,
                              fg=SUBTEXT if self._active != pg else ACCENT))
            self.nav_btns[page] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=15, side="bottom", pady=5)
        tk.Label(self.sidebar, text=f"📅 {date.today().strftime('%d %b %Y')}",
                 bg=PANEL, fg=SUBTEXT, font=("Segoe UI", 9)).pack(
                 side="bottom", pady=5)

        # ── Content area ───────────────────────
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.topbar = tk.Frame(self.content, bg=PANEL, height=55)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        self.page_title_lbl = tk.Label(self.topbar, text="Dashboard",
            bg=PANEL, fg=TEXT, font=("Segoe UI", 15, "bold"))
        self.page_title_lbl.pack(side="left", padx=20, pady=10)
        tk.Label(self.topbar, text="✦ Powered by MediCore v2.0",
            bg=PANEL, fg=SUBTEXT, font=("Segoe UI", 9)).pack(
            side="right", padx=20)

        self.page_frame = tk.Frame(self.content, bg=BG)
        self.page_frame.pack(fill="both", expand=True)
        self._active = None

    def show_page(self, name):
        if self._active and self._active in self.nav_btns:
            self.nav_btns[self._active].config(bg=PANEL, fg=SUBTEXT)
        self._active = name
        self.nav_btns[name].config(bg=HOVER, fg=ACCENT)
        self.page_title_lbl.config(text=f"{ICONS.get(name,'')}  {name}")
        for w in self.page_frame.winfo_children():
            w.destroy()
        builders = {
            "Dashboard":    DashboardPage,
            "Patients":     PatientsPage,
            "Doctors":      DoctorsPage,
            "Appointments": AppointmentsPage,
            "Rooms":        RoomsPage,
            "Billing":      BillingPage,
        }
        builders[name](self.page_frame)


#  DASHBOARD PAGE
class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self._build()

    def _build(self):
        tk.Label(self, text="Welcome to MediCore Dashboard",
                 bg=BG, fg=TEXT, font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(self, text="Real-time hospital statistics",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 10)).pack(
                 anchor="w", pady=(0, 15))

        stats = self._get_stats()
        cards = [
            ("👤 Total Patients",       stats["patients"],    ACCENT),
            ("🩺 Total Doctors",         stats["doctors"],     SUCCESS),
            ("📅 Appointments",          stats["appointments"],WARNING),
            ("🛏 Total Rooms",           stats["rooms"],       "#A78BFA"),
            ("💰 Total Bills",           stats["bills"],       ACCENT2),
            ("🕒 Today's Appointments",  stats["today_appts"], DANGER),
        ]
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x")
        for i, (label, value, color) in enumerate(cards):
            card = tk.Frame(row, bg=CARD, bd=0,
                            highlightbackground=color, highlightthickness=1)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            row.columnconfigure(i % 3, weight=1)
            tk.Label(card, text=label, bg=CARD, fg=SUBTEXT,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=15, pady=(15, 2))
            tk.Label(card, text=str(value), bg=CARD, fg=color,
                     font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=15, pady=(0, 15))

        tk.Label(self, text="Recent Patients", bg=BG, fg=ACCENT2,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(20, 5))
        cols = ("ID", "Name", "Age", "Gender", "Phone", "Blood", "Date")
        tree = make_treeview(self, cols, cols)
        self._load_recent(tree)

    def _get_stats(self):
        s = {k: 0 for k in ("patients","doctors","appointments",
                              "rooms","bills","today_appts")}
        conn = get_connection()
        if not conn:
            return s
        try:
            cur = conn.cursor()
            for key, q in [
                ("patients",     "SELECT COUNT(*) FROM patients"),
                ("doctors",      "SELECT COUNT(*) FROM doctors"),
                ("appointments", "SELECT COUNT(*) FROM appointments"),
                ("rooms",        "SELECT COUNT(*) FROM rooms"),
                ("bills",        "SELECT COUNT(*) FROM billing"),
                ("today_appts",  "SELECT COUNT(*) FROM appointments WHERE appointment_date=CURDATE()"),
            ]:
                cur.execute(q)
                s[key] = cur.fetchone()[0]
        except:
            pass
        finally:
            conn.close()
        return s

    def _load_recent(self, tree):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id,name,age,gender,phone,blood_group,admission_date "
                "FROM patients ORDER BY id DESC LIMIT 10")
            for i, row in enumerate(cur.fetchall()):
                tree.insert("", "end", values=row,
                            tags=("even" if i % 2 == 0 else "odd",))
        except:
            pass
        finally:
            conn.close()


#  PATIENTS PAGE
class PatientsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._sel_id = None
        self._build()

    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(paned, bg=CARD, padx=20, pady=15)
        paned.add(form, minsize=330)
        section_title(form, "Patient Details")

        # Name
        make_label(form, "Full Name *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_name = make_entry(form, "Letters only, e.g. Ali Hassan", width=30)
        self.e_name.frame.pack(fill="x", ipady=2)

        # Age
        make_label(form, "Age *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_age = make_entry(form, "1–149", width=30)
        self.e_age.frame.pack(fill="x", ipady=2)

        # Phone
        make_label(form, "Phone *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_phone = make_entry(form, "e.g. 03001234567", width=30)
        self.e_phone.frame.pack(fill="x", ipady=2)

        # Email
        make_label(form, "Email", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_email = make_entry(form, "Optional: name@domain.com", width=30)
        self.e_email.frame.pack(fill="x", ipady=2)

        # Address
        make_label(form, "Address", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_addr = make_entry(form, "Street, City", width=30)
        self.e_addr.frame.pack(fill="x", ipady=2)

        # Gender
        make_label(form, "Gender *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.gender_var = tk.StringVar(value="Male")
        ttk.Combobox(form, textvariable=self.gender_var,
            values=["Male", "Female", "Other"], state="readonly",
            font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        # Blood group
        make_label(form, "Blood Group", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.blood_var = tk.StringVar(value="A+")
        ttk.Combobox(form, textvariable=self.blood_var,
            values=["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"],
            state="readonly", font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        # Admission date
        make_label(form, "Admission Date (YYYY-MM-DD)", size=10,
                   color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_date = make_entry(form, date.today().strftime("%Y-%m-%d"), width=30)
        self.e_date._active = True
        self.e_date.frame.pack(fill="x", ipady=2)

        btn_f = tk.Frame(form, bg=CARD)
        btn_f.pack(fill="x", pady=15)
        make_btn(btn_f, "➕ Add Patient",  self._add,    color=SUCCESS).pack(side="left", padx=(0, 5))
        make_btn(btn_f, "✏️ Update",        self._update, color=WARNING).pack(side="left", padx=5)
        make_btn(btn_f, "🗑 Delete",         self._delete, color=DANGER ).pack(side="left", padx=5)
        make_btn(form,  "🔄 Clear Form",    self._clear,  color=BORDER, fg=TEXT, width=30).pack(fill="x")

        # ── Right: table ──────────────────────
        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=500)
        self.sv = tk.StringVar()
        search_bar(right, self.sv, self._load)
        cols = ("ID", "Name", "Age", "Gender", "Phone", "Email", "Blood", "Date")
        self.tree = make_treeview(right, cols, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._load()

    # ── Validation ────────────────────────────
    def _validate(self):
        errs = collect_errors([
            validate_alpha_name(get_val(self.e_name)),
            validate_age(get_val(self.e_age)),
            validate_phone(get_val(self.e_phone)),
            validate_email(get_val(self.e_email)),
            validate_date(self.e_date.get()),
        ])
        if errs:
            messagebox.showerror("Validation Error", "\n".join(f"• {e}" for e in errs))
            return False
        return True

    def _add(self):
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO patients "
                "(name,age,gender,phone,email,address,blood_group,admission_date) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (get_val(self.e_name), int(get_val(self.e_age)),
                 self.gender_var.get(), get_val(self.e_phone),
                 get_val(self.e_email), get_val(self.e_addr),
                 self.blood_var.get(), self.e_date.get()))
            conn.commit()
            messagebox.showinfo("Success", "✅ Patient added successfully!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Please select a patient first.")
            return
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE patients SET name=%s,age=%s,gender=%s,phone=%s,"
                "email=%s,address=%s,blood_group=%s,admission_date=%s WHERE id=%s",
                (get_val(self.e_name), int(get_val(self.e_age)),
                 self.gender_var.get(), get_val(self.e_phone),
                 get_val(self.e_email), get_val(self.e_addr),
                 self.blood_var.get(), self.e_date.get(), self._sel_id))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Patient updated!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Please select a patient first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this patient? This cannot be undone."):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM patients WHERE id=%s", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "🗑 Patient deleted.")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _clear(self):
        self._sel_id = None
        for e, ph in [(self.e_name, "Letters only, e.g. Ali Hassan"),
                      (self.e_age,  "1–149"),
                      (self.e_phone,"e.g. 03001234567"),
                      (self.e_email,"Optional: name@domain.com"),
                      (self.e_addr, "Street, City")]:
            e.delete(0, "end")
            e.insert(0, ph)
            e.config(fg=SUBTEXT)
            e._active = False
        self.gender_var.set("Male")
        self.blood_var.set("A+")
        self.e_date.delete(0, "end")
        self.e_date.insert(0, date.today().strftime("%Y-%m-%d"))

    def _load(self, *_):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            q = self.sv.get().strip()
            if q:
                cur.execute(
                    "SELECT id,name,age,gender,phone,email,blood_group,admission_date "
                    "FROM patients WHERE name LIKE %s OR phone LIKE %s ORDER BY id DESC",
                    (f"%{q}%", f"%{q}%"))
            else:
                cur.execute(
                    "SELECT id,name,age,gender,phone,email,blood_group,admission_date "
                    "FROM patients ORDER BY id DESC")
            for i, row in enumerate(cur.fetchall()):
                self.tree.insert("", "end", values=row,
                                 tags=("even" if i % 2 == 0 else "odd",))
        except:
            pass
        finally:
            conn.close()

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._sel_id = v[0]
        for e, val in [(self.e_name, v[1]), (self.e_age, v[2]),
                       (self.e_phone, v[4]), (self.e_email, v[5] or ""),
                       (self.e_addr, "")]:
            e.delete(0, "end")
            e.insert(0, str(val))
            e.config(fg=TEXT)
            e._active = True
        self.gender_var.set(v[3])
        self.blood_var.set(v[6] or "A+")
        self.e_date.delete(0, "end")
        self.e_date.insert(0, str(v[7]))


#  DOCTORS PAGE
class DoctorsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._sel_id = None
        self._build()

    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(paned, bg=CARD, padx=20, pady=15)
        paned.add(form, minsize=330)
        section_title(form, "Doctor Details")

        make_label(form, "Full Name *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_name = make_entry(form, "Dr. Letters Only, e.g. Dr. Ahmed", width=30)
        self.e_name.frame.pack(fill="x", ipady=2)

        make_label(form, "Specialization *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_spec = make_entry(form, "Letters only, e.g. Cardiology", width=30)
        self.e_spec.frame.pack(fill="x", ipady=2)

        make_label(form, "Phone *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_phone = make_entry(form, "e.g. 03001234567", width=30)
        self.e_phone.frame.pack(fill="x", ipady=2)

        make_label(form, "Email", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_email = make_entry(form, "Optional: doctor@hospital.com", width=30)
        self.e_email.frame.pack(fill="x", ipady=2)

        make_label(form, "Experience (years)", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_exp = make_entry(form, "e.g. 10", width=30)
        self.e_exp.frame.pack(fill="x", ipady=2)

        make_label(form, "Availability", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.avail_var = tk.StringVar(value="Available")
        ttk.Combobox(form, textvariable=self.avail_var,
            values=["Available", "Not Available"], state="readonly",
            font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        btn_f = tk.Frame(form, bg=CARD)
        btn_f.pack(fill="x", pady=15)
        make_btn(btn_f, "➕ Add Doctor",  self._add,    color=SUCCESS).pack(side="left", padx=(0, 5))
        make_btn(btn_f, "✏️ Update",       self._update, color=WARNING).pack(side="left", padx=5)
        make_btn(btn_f, "🗑 Delete",        self._delete, color=DANGER ).pack(side="left", padx=5)
        make_btn(form,  "🔄 Clear Form",   self._clear,  color=BORDER, fg=TEXT, width=30).pack(fill="x")

        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=500)
        self.sv = tk.StringVar()
        search_bar(right, self.sv, self._load)
        cols = ("ID", "Name", "Specialization", "Phone", "Email", "Experience", "Available")
        self.tree = make_treeview(right, cols, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self._load()

    def _validate(self):
        exp_val = get_val(self.e_exp)
        exp_check = validate_non_negative_int(exp_val, "Experience") if exp_val else (True, "")
        errs = collect_errors([
            validate_alpha_name(get_val(self.e_name)),
            validate_alpha_only(get_val(self.e_spec), "Specialization"),
            validate_phone(get_val(self.e_phone)),
            validate_email(get_val(self.e_email)),
            exp_check,
        ])
        if errs:
            messagebox.showerror("Validation Error", "\n".join(f"• {e}" for e in errs))
            return False
        return True

    def _add(self):
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            exp = get_val(self.e_exp) or "0"
            cur.execute(
                "INSERT INTO doctors "
                "(name,specialization,phone,email,experience,available) "
                "VALUES(%s,%s,%s,%s,%s,%s)",
                (get_val(self.e_name), get_val(self.e_spec),
                 get_val(self.e_phone), get_val(self.e_email),
                 int(exp), 1 if self.avail_var.get() == "Available" else 0))
            conn.commit()
            messagebox.showinfo("Success", "✅ Doctor added!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            exp = get_val(self.e_exp) or "0"
            cur.execute(
                "UPDATE doctors SET name=%s,specialization=%s,phone=%s,"
                "email=%s,experience=%s,available=%s WHERE id=%s",
                (get_val(self.e_name), get_val(self.e_spec),
                 get_val(self.e_phone), get_val(self.e_email),
                 int(exp), 1 if self.avail_var.get() == "Available" else 0,
                 self._sel_id))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Doctor updated!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this doctor?"):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM doctors WHERE id=%s", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "🗑 Doctor deleted.")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _clear(self):
        self._sel_id = None
        for e, ph in [(self.e_name,  "Dr. Letters Only, e.g. Dr. Ahmed"),
                      (self.e_spec,  "Letters only, e.g. Cardiology"),
                      (self.e_phone, "e.g. 03001234567"),
                      (self.e_email, "Optional: doctor@hospital.com"),
                      (self.e_exp,   "e.g. 10")]:
            e.delete(0, "end")
            e.insert(0, ph)
            e.config(fg=SUBTEXT)
            e._active = False
        self.avail_var.set("Available")

    def _load(self, *_):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            q = self.sv.get().strip()
            if q:
                cur.execute(
                    "SELECT id,name,specialization,phone,email,experience,"
                    "IF(available,'Yes','No') FROM doctors "
                    "WHERE name LIKE %s OR specialization LIKE %s ORDER BY id DESC",
                    (f"%{q}%", f"%{q}%"))
            else:
                cur.execute(
                    "SELECT id,name,specialization,phone,email,experience,"
                    "IF(available,'Yes','No') FROM doctors ORDER BY id DESC")
            for i, row in enumerate(cur.fetchall()):
                self.tree.insert("", "end", values=row,
                                 tags=("even" if i % 2 == 0 else "odd",))
        except:
            pass
        finally:
            conn.close()

    def _on_sel(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._sel_id = v[0]
        for e, val in [(self.e_name, v[1]), (self.e_spec, v[2]),
                       (self.e_phone, v[3]), (self.e_email, v[4]),
                       (self.e_exp, v[5])]:
            e.delete(0, "end")
            e.insert(0, str(val))
            e.config(fg=TEXT)
            e._active = True
        self.avail_var.set("Available" if v[6] == "Yes" else "Not Available")


#  APPOINTMENTS PAGE
class AppointmentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._sel_id = None
        self._build()

    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(paned, bg=CARD, padx=20, pady=15)
        paned.add(form, minsize=330)
        section_title(form, "New Appointment")

        make_label(form, "Patient *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
            state="readonly", font=("Consolas", 10), width=28)
        self.patient_combo.pack(fill="x", ipady=4)

        make_label(form, "Doctor *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.doctor_var = tk.StringVar()
        self.doctor_combo = ttk.Combobox(form, textvariable=self.doctor_var,
            state="readonly", font=("Consolas", 10), width=28)
        self.doctor_combo.pack(fill="x", ipady=4)

        make_label(form, "Date (YYYY-MM-DD) *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_date = make_entry(form, date.today().strftime("%Y-%m-%d"), width=30)
        self.e_date._active = True
        self.e_date.frame.pack(fill="x", ipady=2)

        make_label(form, "Time (HH:MM) *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_time = make_entry(form, "e.g. 09:30", width=30)
        self.e_time.frame.pack(fill="x", ipady=2)

        make_label(form, "Status", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.status_var = tk.StringVar(value="Scheduled")
        ttk.Combobox(form, textvariable=self.status_var,
            values=["Scheduled", "Completed", "Cancelled"],
            state="readonly", font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        make_label(form, "Notes", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_notes = make_entry(form, "Optional notes", width=30)
        self.e_notes.frame.pack(fill="x", ipady=2)

        btn_f = tk.Frame(form, bg=CARD)
        btn_f.pack(fill="x", pady=15)
        make_btn(btn_f, "➕ Book",     self._add,         color=SUCCESS).pack(side="left", padx=(0, 5))
        make_btn(btn_f, "✏️ Update",    self._update,      color=WARNING).pack(side="left", padx=5)
        make_btn(btn_f, "🗑 Delete",     self._delete,      color=DANGER ).pack(side="left", padx=5)
        make_btn(form,  "🔄 Refresh Dropdowns", self._load_combos,
                 color=ACCENT, fg=BG, width=30).pack(fill="x")

        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=500)
        self.sv = tk.StringVar()
        search_bar(right, self.sv, self._load)
        cols = ("ID", "Patient", "Doctor", "Date", "Time", "Status", "Notes")
        self.tree = make_treeview(right, cols, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self._load_combos()
        self._load()

    def _load_combos(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id,name FROM patients ORDER BY name")
            self._patients = {f"{r[0]} - {r[1]}": r[0] for r in cur.fetchall()}
            self.patient_combo["values"] = list(self._patients.keys())
            cur.execute("SELECT id,name,specialization FROM doctors WHERE available=1 ORDER BY name")
            self._doctors = {f"{r[0]} - {r[1]} ({r[2]})": r[0] for r in cur.fetchall()}
            self.doctor_combo["values"] = list(self._doctors.keys())
        except:
            pass
        finally:
            conn.close()

    def _validate(self):
        errs = collect_errors([
            (bool(self.patient_var.get()), "Select a patient"),
            (bool(self.doctor_var.get()),  "Select a doctor"),
            validate_date(self.e_date.get()),
            validate_time(get_val(self.e_time)),
        ])
        if errs:
            messagebox.showerror("Validation", "\n".join(f"• {e}" for e in errs))
            return False
        return True

    def _add(self):
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO appointments "
                "(patient_id,doctor_id,appointment_date,appointment_time,status,notes) "
                "VALUES(%s,%s,%s,%s,%s,%s)",
                (self._patients[self.patient_var.get()],
                 self._doctors[self.doctor_var.get()],
                 self.e_date.get(), get_val(self.e_time),
                 self.status_var.get(), get_val(self.e_notes)))
            conn.commit()
            messagebox.showinfo("Booked", "✅ Appointment booked!")
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select an appointment first.")
            return
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE appointments SET patient_id=%s,doctor_id=%s,"
                "appointment_date=%s,appointment_time=%s,status=%s,notes=%s WHERE id=%s",
                (self._patients[self.patient_var.get()],
                 self._doctors[self.doctor_var.get()],
                 self.e_date.get(), get_val(self.e_time),
                 self.status_var.get(), get_val(self.e_notes), self._sel_id))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Appointment updated!")
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select an appointment first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this appointment?"):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM appointments WHERE id=%s", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "🗑 Appointment deleted.")
            self._sel_id = None
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _load(self, *_):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            q = self.sv.get().strip()
            sql = ("SELECT a.id, p.name, d.name, a.appointment_date, "
                   "a.appointment_time, a.status, a.notes "
                   "FROM appointments a "
                   "JOIN patients p ON a.patient_id=p.id "
                   "JOIN doctors  d ON a.doctor_id=d.id")
            if q:
                sql += " WHERE p.name LIKE %s OR d.name LIKE %s ORDER BY a.id DESC"
                cur.execute(sql, (f"%{q}%", f"%{q}%"))
            else:
                sql += " ORDER BY a.id DESC"
                cur.execute(sql)
            for i, row in enumerate(cur.fetchall()):
                self.tree.insert("", "end", values=row,
                                 tags=("even" if i % 2 == 0 else "odd",))
        except:
            pass
        finally:
            conn.close()

    def _on_sel(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._sel_id = v[0]
        self.status_var.set(v[5])
        self.e_date.delete(0, "end")
        self.e_date.insert(0, str(v[3]))
        for e, val in [(self.e_time, v[4]), (self.e_notes, v[6] or "")]:
            e.delete(0, "end")
            e.insert(0, str(val))
            e.config(fg=TEXT)
            e._active = True


#  ROOMS PAGE
class RoomsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._sel_id = None
        self._build()

    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(paned, bg=CARD, padx=20, pady=15)
        paned.add(form, minsize=330)
        section_title(form, "Room Details")

        make_label(form, "Room Number *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_num = make_entry(form, "e.g. 101", width=30)
        self.e_num.frame.pack(fill="x", ipady=2)

        make_label(form, "Room Type *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.type_var = tk.StringVar(value="General")
        ttk.Combobox(form, textvariable=self.type_var,
            values=["General", "Private", "ICU", "Emergency", "Maternity", "Pediatric"],
            state="readonly", font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        make_label(form, "Floor", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_floor = make_entry(form, "e.g. 2", width=30)
        self.e_floor.frame.pack(fill="x", ipady=2)

        make_label(form, "Capacity *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_cap = make_entry(form, "Number of beds, e.g. 2", width=30)
        self.e_cap.frame.pack(fill="x", ipady=2)

        make_label(form, "Price Per Day (Rs.) *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_price = make_entry(form, "e.g. 2500.00", width=30)
        self.e_price.frame.pack(fill="x", ipady=2)

        make_label(form, "Status", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.status_var = tk.StringVar(value="Available")
        ttk.Combobox(form, textvariable=self.status_var,
            values=["Available", "Occupied", "Under Maintenance"],
            state="readonly", font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        make_label(form, "Assigned Patient", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
            state="readonly", font=("Consolas", 10), width=28)
        self.patient_combo.pack(fill="x", ipady=4)
        tk.Label(form, text="(optional — assign when Occupied)",
                 bg=CARD, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w")

        btn_f = tk.Frame(form, bg=CARD)
        btn_f.pack(fill="x", pady=15)
        make_btn(btn_f, "➕ Add Room",   self._add,         color=SUCCESS).pack(side="left", padx=(0, 5))
        make_btn(btn_f, "✏️ Update",      self._update,      color=WARNING).pack(side="left", padx=5)
        make_btn(btn_f, "🗑 Delete",       self._delete,      color=DANGER ).pack(side="left", padx=5)
        make_btn(form, "🔄 Refresh",       self._refresh_all, color=ACCENT, fg=BG, width=30).pack(fill="x")

        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=500)
        self.sv = tk.StringVar()
        search_bar(right, self.sv, self._load)
        cols = ("ID", "Room No.", "Type", "Floor", "Capacity", "Price/Day", "Status", "Patient")
        self.tree = make_treeview(right, cols, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        # Summary bar
        self.summary_lbl = tk.Label(right, text="", bg=CARD, fg=ACCENT2,
                                    font=("Segoe UI", 11, "bold"))
        self.summary_lbl.pack(fill="x", padx=10, pady=5)

        self._load_patients()
        self._load()

    def _load_patients(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM patients ORDER BY name")
            self._patients = {"(None)": None}
            self._patients.update({f"{r[0]} - {r[1]}": r[0] for r in cur.fetchall()})
            self.patient_combo["values"] = list(self._patients.keys())
            self.patient_var.set("(None)")
        except:
            pass
        finally:
            conn.close()

    def _refresh_all(self):
        self._load_patients()
        self._load()

    def _validate(self):
        room_num = get_val(self.e_num)
        floor_val = get_val(self.e_floor)
        floor_check = validate_non_negative_int(floor_val, "Floor") if floor_val else (True, "")
        errs = collect_errors([
            (len(room_num) >= 1, "Room Number is required"),
            validate_non_negative_int(get_val(self.e_cap), "Capacity"),
            validate_positive_float(get_val(self.e_price), "Price Per Day"),
            floor_check,
        ])
        if errs:
            messagebox.showerror("Validation", "\n".join(f"• {e}" for e in errs))
            return False
        return True

    def _get_patient_id(self):
        key = self.patient_var.get()
        return self._patients.get(key)

    def _add(self):
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            floor = get_val(self.e_floor) or None
            cur.execute(
                "INSERT INTO rooms "
                "(room_number, room_type, floor, capacity, price_per_day, status, patient_id) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (get_val(self.e_num), self.type_var.get(),
                 int(floor) if floor else None,
                 int(get_val(self.e_cap)),
                 float(get_val(self.e_price)),
                 self.status_var.get(),
                 self._get_patient_id()))
            conn.commit()
            messagebox.showinfo("Added", "✅ Room added!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a room first.")
            return
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            floor = get_val(self.e_floor) or None
            cur.execute(
                "UPDATE rooms SET room_number=%s, room_type=%s, floor=%s, "
                "capacity=%s, price_per_day=%s, status=%s, patient_id=%s WHERE id=%s",
                (get_val(self.e_num), self.type_var.get(),
                 int(floor) if floor else None,
                 int(get_val(self.e_cap)),
                 float(get_val(self.e_price)),
                 self.status_var.get(),
                 self._get_patient_id(),
                 self._sel_id))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Room updated!")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a room first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this room?"):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM rooms WHERE id=%s", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "🗑 Room deleted.")
            self._clear()
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _clear(self):
        self._sel_id = None
        for e, ph in [(self.e_num,   "e.g. 101"),
                      (self.e_floor, "e.g. 2"),
                      (self.e_cap,   "Number of beds, e.g. 2"),
                      (self.e_price, "e.g. 2500.00")]:
            e.delete(0, "end")
            e.insert(0, ph)
            e.config(fg=SUBTEXT)
            e._active = False
        self.type_var.set("General")
        self.status_var.set("Available")
        self.patient_var.set("(None)")

    def _load(self, *_):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            q = self.sv.get().strip()
            sql = ("SELECT r.id, r.room_number, r.room_type, r.floor, "
                   "r.capacity, r.price_per_day, r.status, "
                   "IFNULL(p.name, '—') "
                   "FROM rooms r LEFT JOIN patients p ON r.patient_id = p.id")
            if q:
                sql += (" WHERE r.room_number LIKE %s OR r.room_type LIKE %s "
                        "OR r.status LIKE %s ORDER BY r.id DESC")
                cur.execute(sql, (f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                sql += " ORDER BY r.id DESC"
                cur.execute(sql)
            for i, row in enumerate(cur.fetchall()):
                self.tree.insert("", "end", values=row,
                                 tags=("even" if i % 2 == 0 else "odd",))
            # Summary counts
            cur.execute("SELECT status, COUNT(*) FROM rooms GROUP BY status")
            counts = {row[0]: row[1] for row in cur.fetchall()}
            avail = counts.get("Available", 0)
            occup = counts.get("Occupied", 0)
            maint = counts.get("Under Maintenance", 0)
            self.summary_lbl.config(
                text=f"  🟢 Available: {avail}   🔴 Occupied: {occup}"
                     f"   🟡 Maintenance: {maint}")
        except:
            pass
        finally:
            conn.close()

    def _on_sel(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._sel_id = v[0]
        for e, val in [(self.e_num,   v[1]),
                       (self.e_floor, v[3] if v[3] else ""),
                       (self.e_cap,   v[4]),
                       (self.e_price, v[5])]:
            e.delete(0, "end")
            e.insert(0, str(val))
            e.config(fg=TEXT)
            e._active = True
        self.type_var.set(v[2])
        self.status_var.set(v[6])
        # Match patient name back to combo key
        patient_name = v[7]
        matched = next((k for k in self._patients if patient_name in k), "(None)")
        self.patient_var.set(matched)


#  BILLING PAGE
class BillingPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._sel_id = None
        self._build()

    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(paned, bg=CARD, padx=20, pady=15)
        paned.add(form, minsize=330)
        section_title(form, "Billing Details")

        make_label(form, "Patient *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
            state="readonly", font=("Consolas", 10), width=28)
        self.patient_combo.pack(fill="x", ipady=4)

        make_label(form, "Total Amount (Rs.) *", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_total = make_entry(form, "e.g. 5000", width=30)
        self.e_total.frame.pack(fill="x", ipady=2)

        make_label(form, "Paid Amount (Rs.)", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_paid = make_entry(form, "e.g. 2500 (default 0)", width=30)
        self.e_paid.frame.pack(fill="x", ipady=2)

        make_label(form, "Payment Date (YYYY-MM-DD)", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_pdate = make_entry(form, "Optional", width=30)
        self.e_pdate.frame.pack(fill="x", ipady=2)

        make_label(form, "Description", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.e_desc = make_entry(form, "Services rendered", width=30)
        self.e_desc.frame.pack(fill="x", ipady=2)

        make_label(form, "Payment Status", size=10, color=SUBTEXT).pack(anchor="w", pady=(6, 1))
        self.status_var = tk.StringVar(value="Pending")
        ttk.Combobox(form, textvariable=self.status_var,
            values=["Pending", "Partial", "Paid"],
            state="readonly", font=("Consolas", 11), width=28).pack(fill="x", ipady=4)

        btn_f = tk.Frame(form, bg=CARD)
        btn_f.pack(fill="x", pady=15)
        make_btn(btn_f, "➕ Add Bill",  self._add,         color=SUCCESS).pack(side="left", padx=(0, 5))
        make_btn(btn_f, "✏️ Update",     self._update,      color=WARNING).pack(side="left", padx=5)
        make_btn(btn_f, "🗑 Delete",      self._delete,      color=DANGER ).pack(side="left", padx=5)
        make_btn(form,  "🔄 Refresh Patients", self._load_combos,
                 color=ACCENT, fg=BG, width=30).pack(fill="x")

        right = tk.Frame(paned, bg=BG)
        paned.add(right, minsize=500)
        self.sv = tk.StringVar()
        search_bar(right, self.sv, self._load)
        cols = ("ID", "Patient", "Total", "Paid", "Status", "Pay Date", "Description")
        self.tree = make_treeview(right, cols, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self.summary_lbl = tk.Label(right, text="", bg=CARD, fg=ACCENT2,
                                    font=("Segoe UI", 11, "bold"))
        self.summary_lbl.pack(fill="x", padx=10, pady=5)
        self._load_combos()
        self._load()

    def _load_combos(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id,name FROM patients ORDER BY name")
            self._patients = {f"{r[0]} - {r[1]}": r[0] for r in cur.fetchall()}
            self.patient_combo["values"] = list(self._patients.keys())
        except:
            pass
        finally:
            conn.close()

    def _validate(self):
        paid_val = get_val(self.e_paid)
        paid_check = validate_positive_float(paid_val, "Paid Amount") if paid_val else (True, "")
        pdate_val = get_val(self.e_pdate)
        pdate_check = validate_date(pdate_val) if pdate_val else (True, "")
        errs = collect_errors([
            (bool(self.patient_var.get()), "Select a patient"),
            validate_positive_float(get_val(self.e_total), "Total Amount"),
            paid_check,
            pdate_check,
        ])
        if errs:
            messagebox.showerror("Validation", "\n".join(f"• {e}" for e in errs))
            return False
        return True

    def _add(self):
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            paid = get_val(self.e_paid) or "0"
            cur.execute(
                "INSERT INTO billing "
                "(patient_id,total_amount,paid_amount,payment_status,payment_date,description) "
                "VALUES(%s,%s,%s,%s,%s,%s)",
                (self._patients[self.patient_var.get()],
                 float(get_val(self.e_total)), float(paid),
                 self.status_var.get(),
                 get_val(self.e_pdate) or None,
                 get_val(self.e_desc)))
            conn.commit()
            messagebox.showinfo("Added", "✅ Bill added!")
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a bill first.")
            return
        if not self._validate():
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            paid = get_val(self.e_paid) or "0"
            cur.execute(
                "UPDATE billing SET patient_id=%s,total_amount=%s,paid_amount=%s,"
                "payment_status=%s,payment_date=%s,description=%s WHERE id=%s",
                (self._patients[self.patient_var.get()],
                 float(get_val(self.e_total)), float(paid),
                 self.status_var.get(),
                 get_val(self.e_pdate) or None,
                 get_val(self.e_desc), self._sel_id))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Bill updated!")
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select a bill first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this bill?"):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM billing WHERE id=%s", (self._sel_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "🗑 Bill deleted.")
            self._sel_id = None
            self._load()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def _load(self, *_):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            q = self.sv.get().strip()
            sql = ("SELECT b.id, p.name, b.total_amount, b.paid_amount, "
                   "b.payment_status, b.payment_date, b.description "
                   "FROM billing b JOIN patients p ON b.patient_id=p.id")
            if q:
                sql += " WHERE p.name LIKE %s ORDER BY b.id DESC"
                cur.execute(sql, (f"%{q}%",))
            else:
                sql += " ORDER BY b.id DESC"
                cur.execute(sql)
            for i, row in enumerate(cur.fetchall()):
                self.tree.insert("", "end", values=row,
                                 tags=("even" if i % 2 == 0 else "odd",))
            cur.execute("SELECT SUM(total_amount), SUM(paid_amount) FROM billing")
            tot, paid = cur.fetchone()
            tot = tot or 0
            paid = paid or 0
            self.summary_lbl.config(
                text=f"  💰 Total: Rs.{tot:,.0f}   ✅ Collected: Rs.{paid:,.0f}"
                     f"   ⏳ Pending: Rs.{tot - paid:,.0f}")
        except:
            pass
        finally:
            conn.close()

    def _on_sel(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._sel_id = v[0]
        for e, val in [(self.e_total, v[2]), (self.e_paid, v[3]),
                       (self.e_pdate, v[5] or ""), (self.e_desc, v[6] or "")]:
            e.delete(0, "end")
            e.insert(0, str(val))
            e.config(fg=TEXT)
            e._active = True
        self.status_var.set(v[4])


#  ENTRY POINT
if __name__ == "__main__":
    print("🏥 MediCore Hospital Management System v2.0")
    print("=" * 50)
    print("IMPORTANT: Make sure you have already run")
    print("           hospital_db.sql in MySQL Workbench!")
    print("=" * 50)
    app = HospitalApp()
    app.mainloop()