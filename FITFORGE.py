from tkinter.font import Font
import mysql.connector
from tkinter import *
from tkinter import messagebox, ttk
import time
from PIL import Image, ImageTk
import webbrowser
import smtplib
import random
from email.mime.text import MIMEText
import configparser
import os
from io import BytesIO
import requests
import datetime

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'priyamysql@30',
    'database': 'gym_trainer'
}

# Global variable to track the current window
current_window = None
timer_running = False
timer_start_time = 0
timer_paused_time = 0
otp_verified = False
generated_otp = ""
current_user_type = None  # 'admin' or 'user'

def get_db_connection():
    return mysql.connector.connect(**db_config)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'priyamysql@30',  # Use your actual MySQL password
    'database': 'gym_trainer',    # Add this line
    'auth_plugin': 'mysql_native_password'
}
# Close the current window before opening a new one
def close_current_window():
    global current_window
    if current_window:
        current_window.destroy()

# Exit Function to close the whole application
def exit_application():
    root.quit()

# Modern Color Scheme inspired by cult.fit
PRIMARY_COLOR = "#ffffff"  # White
SECONDARY_COLOR = "#ff764a"  # Cult.fit orange
ACCENT_COLOR = "#2d2d2d"  # Dark gray
TEXT_COLOR = "#333333"  # Dark text
LIGHT_GRAY = "#f5f5f5"  # Light gray background
BUTTON_HOVER = "#e5673e"  # Darker orange for hover
COACHING_COLOR = "#6a1b9a"  # Purple for coaching feature
ADMIN_COLOR = "#1976D2"  # Blue for admin features

# Font styles
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_REGULAR = ("Segoe UI", 12)
FONT_LARGE = ("Segoe UI", 24, "bold")
FONT_TITLE = ("Segoe UI", 36, "bold")
FONT_SUBTITLE = ("Segoe UI", 16)

class EmailCredentialsDialog:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.sender_email = ""
        self.app_password = ""
        
        self.dialog = Toplevel(parent)
        self.dialog.title("Enter Email Credentials")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        Label(self.dialog, text="Email Configuration", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        Label(self.dialog, text="Sender Email:").pack()
        self.email_entry = ttk.Entry(self.dialog, width=40)
        self.email_entry.pack(pady=5)
        
        Label(self.dialog, text="App Password:").pack()
        self.password_entry = ttk.Entry(self.dialog, width=40, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.dialog, text="Save Credentials", command=self.save_credentials).pack(pady=20)
        
        # Load existing credentials if available
        self.load_existing_credentials()
        
        self.dialog.grab_set()  # Make window modal
    
    def load_existing_credentials(self):
        """Load credentials from config file if exists"""
        config = configparser.ConfigParser()
        config_file = "email_config.ini"
        
        if os.path.exists(config_file):
            config.read(config_file)
            if 'EMAIL' in config:
                self.email_entry.insert(0, config['EMAIL'].get('sender_email', ''))
                self.password_entry.insert(0, config['EMAIL'].get('app_password', ''))
    
    def save_credentials(self):
        self.sender_email = self.email_entry.get().strip()
        self.app_password = self.password_entry.get().strip()
        
        if not self.sender_email or not self.app_password:
            messagebox.showerror("Error", "Both fields are required!", parent=self.dialog)
            return
            
        # Save to config file
        config = configparser.ConfigParser()
        config['EMAIL'] = {
            'sender_email': self.sender_email,
            'app_password': self.app_password
        }
        
        with open("email_config.ini", 'w') as configfile:
            config.write(configfile)
            
        self.dialog.destroy()
        self.callback(self.sender_email, self.app_password)
    
    def load_existing_credentials(self):
        """Load credentials from config file if exists"""
        config = configparser.ConfigParser()
        config_file = "email_config.ini"
        
        if os.path.exists(config_file):
            config.read(config_file)
            if 'EMAIL' in config:
                self.email_entry.insert(0, config['EMAIL'].get('sender_email', ''))
                self.password_entry.insert(0, config['EMAIL'].get('app_password', ''))
    
    def save_credentials(self):
        self.sender_email = self.email_entry.get().strip()
        self.app_password = self.password_entry.get().strip()
        
        if not self.sender_email or not self.app_password:
            messagebox.showerror("Error", "Both fields are required!", parent=self.dialog)
            return
            
        # Save to config file
        config = configparser.ConfigParser()
        config['EMAIL'] = {
            'sender_email': self.sender_email,
            'app_password': self.app_password
        }
        
        with open("email_config.ini", 'w') as configfile:
            config.write(configfile)
            
        self.dialog.destroy()
        self.callback(self.sender_email, self.app_password)

# Timer functions
def start_timer(timer_label, seconds=0):
    global timer_running, timer_start_time
    if not timer_running:
        timer_running = True
        timer_start_time = time.time() - (seconds if seconds > 0 else 0)
        update_timer(timer_label)

def pause_timer():
    global timer_running, timer_paused_time
    timer_running = False
    timer_paused_time = time.time()

def reset_timer(timer_label):
    global timer_running, timer_start_time, timer_paused_time
    timer_running = False
    timer_start_time = 0
    timer_paused_time = 0
    timer_label.config(text="00:00:00")

def update_timer(timer_label):
    if timer_running:
        elapsed = time.time() - timer_start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        timer_label.after(1000, lambda: update_timer(timer_label))

# Function to add home button to any window
def add_home_button(window, user_id):
    home_btn = Button(window, text="🏠 Home", command=lambda: open_dashboard(user_id),
                     width=10, height=1, bg=PRIMARY_COLOR, fg=ACCENT_COLOR, 
                     font=FONT_BOLD, relief=FLAT, borderwidth=0, activebackground=LIGHT_GRAY)
    home_btn.place(relx=0.95, rely=0.05, anchor=CENTER)

# Signup Function with age and weight
def signup():
    username = username_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    age = age_entry.get().strip()
    weight = weight_entry.get().strip()

    if not username or not email or not password or not age or not weight:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        age = int(age)
        weight = float(weight)
    except ValueError:
        messagebox.showerror("Error", "Age must be a whole number and weight must be a number!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password, age, weight) VALUES (%s, %s, %s, %s, %s)', 
                      (username, email, password, age, weight))
        conn.commit()
        messagebox.showinfo("Success", "Signup successful! Please login.")
        open_login_page()
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Email already exists.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to send OTP
def send_otp(email, sender_email, app_password):
    global generated_otp
    generated_otp = str(random.randint(100000, 999999))  # 6-digit random number
    
    # Email content
    msg = MIMEText(f"Your verification code is: {generated_otp}\n\nThis code will expire after 10 minutes.")
    msg['Subject'] = "Your OTP Verification Code"
    msg['From'] = sender_email
    msg['To'] = email
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email, msg.as_string())
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")
        return False

# Function to verify OTP
def verify_otp(entered_otp):
    global otp_verified, generated_otp
    if entered_otp == generated_otp:
        otp_verified = True
        return True
    else:
        messagebox.showerror("Error", "Invalid OTP! Please try again.")
        return False

# Login Function with OTP verification
def login(is_admin=False):
    global otp_verified, current_user_type
    
    email = login_email_entry.get().strip()
    password = login_password_entry.get().strip()

    # Validate that both fields are filled
    if not email or email == "Email":
        messagebox.showerror("Error", "Email is required!")
        return
    if not password or password == "Password":
        messagebox.showerror("Error", "Password is required!")
        return

    # First verify credentials against database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if is_admin:
            # Check admin credentials
            cursor.execute('SELECT * FROM admins WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            if user:
                current_user_type = 'admin'
                open_admin_dashboard()
                return
            else:
                messagebox.showerror("Error", "Invalid admin credentials.")
                return
        else:
            # Check user credentials
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            
            if user:
                current_user_type = 'user'
                # If credentials are valid, check if OTP is already verified
                if otp_verified:
                    open_dashboard(user['id'])
                    otp_verified = False  # Reset for next login
                else:
                    # Show OTP verification frame
                    login_otp_frame.pack(pady=20)
                    login_btn.pack_forget()
                    
                    # Try to load email credentials from config file
                    config = configparser.ConfigParser()
                    config_file = "email_config.ini"
                    
                    if os.path.exists(config_file):
                        config.read(config_file)
                        if 'EMAIL' in config:
                            sender_email = config['EMAIL'].get('sender_email', '')
                            app_password = config['EMAIL'].get('app_password', '')
                            
                            if sender_email and app_password:
                                if send_otp(email, sender_email, app_password):
                                    messagebox.showinfo("Success", f"OTP sent successfully to {email}!\nPlease check your inbox.")
                                else:
                                    login_otp_frame.pack_forget()
                                    login_btn.pack()
                                return
                    
                    # If no valid credentials found, show configuration dialog
                    EmailCredentialsDialog(current_window, lambda s, p: on_credentials_set(s, p, email))
            else:
                messagebox.showerror("Error", "Invalid email or password.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

def on_credentials_set(sender_email, app_password, recipient_email):
    if send_otp(recipient_email, sender_email, app_password):
        messagebox.showinfo("Success", f"OTP sent successfully to {recipient_email}!\nPlease check your inbox.")
    else:
        login_otp_frame.pack_forget()
        login_btn.pack()
# Function to handle OTP verification during login
def verify_login_otp():
    entered_otp = login_otp_entry.get().strip()
    
    if not entered_otp:
        messagebox.showerror("Error", "Please enter the OTP code!")
        return
        
    if verify_otp(entered_otp):
        # If OTP is verified, proceed with login
        login_otp_frame.pack_forget()
        login_btn.pack()
        login()  # This will now proceed to open dashboard since otp_verified is True

# Open user profile edit window
def open_profile_edit(user_id):
    edit_window = Toplevel(root)
    edit_window.title("Edit Profile - FitForge")
    edit_window.geometry("600x400")
    edit_window.configure(bg=PRIMARY_COLOR)

    # Fetch current user data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Header
    header_frame = Frame(edit_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Edit Profile", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(edit_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Form frame
    form_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=40, pady=40)
    form_frame.pack(fill=BOTH, expand=True)

    # Username field
    Label(form_frame, text="Username", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    username_entry = Entry(form_frame, font=FONT_REGULAR)
    username_entry.insert(0, user['username'])
    username_entry.pack(fill=X, pady=5)

    # Age field
    Label(form_frame, text="Age", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    age_entry = Entry(form_frame, font=FONT_REGULAR)
    age_entry.insert(0, user['age'] if user['age'] else "")
    age_entry.pack(fill=X, pady=5)

    # Weight field
    Label(form_frame, text="Weight (kg)", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    weight_entry = Entry(form_frame, font=FONT_REGULAR)
    weight_entry.insert(0, user['weight'] if user['weight'] else "")
    weight_entry.pack(fill=X, pady=5)

    def save_profile():
        new_username = username_entry.get().strip()
        new_age = age_entry.get().strip()
        new_weight = weight_entry.get().strip()

        if not new_username or not new_age or not new_weight:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            new_age = int(new_age)
            new_weight = float(new_weight)
        except ValueError:
            messagebox.showerror("Error", "Age must be a whole number and weight must be a number!")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET username = %s, age = %s, weight = %s WHERE id = %s', 
                         (new_username, new_age, new_weight, user_id))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            edit_window.destroy()
            # Refresh dashboard to show updated info
            open_dashboard(user_id)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()
            conn.close()

    # Save button
    Button(form_frame, text="Save Changes", command=save_profile,
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground=BUTTON_HOVER).pack(fill=X, pady=20)

    # Footer
    footer_frame = Frame(edit_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=edit_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

# Admin Dashboard
def open_admin_dashboard():
    global current_window
    close_current_window()

    admin_window = Toplevel(root)
    admin_window.title("FitForge Admin Dashboard")
    admin_window.geometry("1200x800")
    admin_window.configure(bg=PRIMARY_COLOR)
    current_window = admin_window

    # Header
    header_frame = Frame(admin_window, bg=ADMIN_COLOR, height=80)
    header_frame.pack(fill=X)
    
    Label(header_frame, text="FitForge Admin", font=FONT_TITLE, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # Navigation buttons
    nav_frame = Frame(header_frame, bg=ADMIN_COLOR)
    nav_frame.pack(side=RIGHT, padx=20)
    
    Button(nav_frame, text="Manage Users", command=manage_users,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#1565C0").pack(side=LEFT, padx=5)
    
    Button(nav_frame, text="View All Plans", command=view_all_plans,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#1565C0").pack(side=LEFT, padx=5)

    # Content
    content_frame = Frame(admin_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

    # Dashboard cards
    card_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    card_frame.pack(fill=BOTH, expand=True)

    # Card 1: Manage Users
    users_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    users_card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    users_card.grid_propagate(False)
    
    Label(users_card, text="👥 Manage Users", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack(pady=(20,10))
    Label(users_card, text="View, edit and manage all users", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(users_card, text="Go to Users", command=manage_users, 
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#1565C0").pack(pady=20)

    # Card 2: View All Plans
    plans_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    plans_card.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    plans_card.grid_propagate(False)
    
    Label(plans_card, text="📋 All Plans", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack(pady=(20,10))
    Label(plans_card, text="View all diet and exercise plans", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(plans_card, text="View Plans", command=view_all_plans, 
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#1565C0").pack(pady=20)

    # Card 3: Statistics
    stats_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    stats_card.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
    stats_card.grid_propagate(False)
    
    Label(stats_card, text="📊 Statistics", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack(pady=(20,10))
    Label(stats_card, text="View system statistics and analytics", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(stats_card, text="View Stats", command=view_statistics, 
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#1565C0").pack(pady=20)

    # Configure grid weights
    card_frame.grid_columnconfigure(0, weight=1)
    card_frame.grid_columnconfigure(1, weight=1)
    card_frame.grid_columnconfigure(2, weight=1)

    # Footer
    footer_frame = Frame(admin_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Logout", command=admin_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)
    
    Button(footer_frame, text="Exit", command=exit_application, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

def manage_users():
    global current_window
    close_current_window()

    users_window = Toplevel(root)
    users_window.title("Manage Users - FitForge Admin")
    users_window.geometry("1200x800")
    users_window.configure(bg=PRIMARY_COLOR)
    current_window = users_window

    # Header
    header_frame = Frame(users_window, bg=ADMIN_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Manage Users", font=FONT_TITLE, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # Back button
    Button(header_frame, text="Back", command=lambda: [users_window.destroy(), open_admin_dashboard()],
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#1565C0").pack(side=RIGHT, padx=20)

    # Content
    content_frame = Frame(users_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Fetch all users from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, username, email, age, weight FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create Treeview with scrollbar
    tree_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    tree_frame.pack(fill=BOTH, expand=True)
    
    # Create Treeview with style
    style = ttk.Style()
    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=FONT_REGULAR)
    style.configure("mystyle.Treeview.Heading", font=FONT_BOLD)
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
    
    tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Email", "Age", "Weight"), show="headings", style="mystyle.Treeview")
    
    # Define headings
    tree.heading("ID", text="ID")
    tree.heading("Username", text="Username")
    tree.heading("Email", text="Email")
    tree.heading("Age", text="Age")
    tree.heading("Weight", text="Weight (kg)")
    
    # Configure columns
    tree.column("ID", width=50, anchor="center")
    tree.column("Username", width=150, anchor="w")
    tree.column("Email", width=200, anchor="w")
    tree.column("Age", width=50, anchor="center")
    tree.column("Weight", width=80, anchor="center")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill=BOTH, expand=True)
    
    # Insert data
    for user in users:
        tree.insert("", "end", values=(
            user['id'],
            user['username'],
            user['email'],
            user['age'] if user['age'] else "-",
            user['weight'] if user['weight'] else "-"
        ))
    
    # Action buttons frame
    button_frame = Frame(content_frame, bg=PRIMARY_COLOR, pady=20)
    button_frame.pack(fill=X)
    
    def edit_selected_user():
        selected_item = tree.focus()
        if selected_item:
            user_data = tree.item(selected_item)
            user_id = user_data['values'][0]
            edit_user(user_id)
    
    def delete_selected_user():
        selected_item = tree.focus()
        if selected_item:
            user_data = tree.item(selected_item)
            user_id = user_data['values'][0]
            username = user_data['values'][1]
            
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {username}?")
            if confirm:
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    # First delete user's diet charts
                    cursor.execute('DELETE FROM diet_charts WHERE user_id = %s', (user_id,))
                    # Then delete the user
                    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "User deleted successfully!")
                    # Refresh the treeview
                    users_window.destroy()
                    manage_users()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Database error: {err}")
                finally:
                    cursor.close()
                    conn.close()
    
    Button(button_frame, text="Edit User", command=edit_selected_user,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#1565C0").pack(side=LEFT, padx=5)
    
    Button(button_frame, text="Delete User", command=delete_selected_user,
           bg="#D32F2F", fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#B71C1C").pack(side=LEFT, padx=5)
    
    Button(button_frame, text="Add New User", command=add_new_user,
           bg="#388E3C", fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#2E7D32").pack(side=RIGHT, padx=5)

def edit_user(user_id):
    edit_window = Toplevel(root)
    edit_window.title(f"Edit User - FitForge Admin")
    edit_window.geometry("500x400")
    edit_window.configure(bg=PRIMARY_COLOR)

    # Fetch user data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Header
    header_frame = Frame(edit_window, bg=ADMIN_COLOR, height=60)
    header_frame.pack(fill=X)
    Label(header_frame, text=f"Edit User: {user['username']}", font=FONT_BOLD, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(edit_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Form frame
    form_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    form_frame.pack(fill=BOTH, expand=True)

    # Username
    Label(form_frame, text="Username", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    username_entry = Entry(form_frame, font=FONT_REGULAR)
    username_entry.insert(0, user['username'])
    username_entry.pack(fill=X, pady=5)

    # Email
    Label(form_frame, text="Email", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    email_entry = Entry(form_frame, font=FONT_REGULAR)
    email_entry.insert(0, user['email'])
    email_entry.pack(fill=X, pady=5)

    # Age
    Label(form_frame, text="Age", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    age_entry = Entry(form_frame, font=FONT_REGULAR)
    age_entry.insert(0, user['age'] if user['age'] else "")
    age_entry.pack(fill=X, pady=5)

    # Weight
    Label(form_frame, text="Weight (kg)", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    weight_entry = Entry(form_frame, font=FONT_REGULAR)
    weight_entry.insert(0, user['weight'] if user['weight'] else "")
    weight_entry.pack(fill=X, pady=5)

    def save_changes():
        new_username = username_entry.get().strip()
        new_email = email_entry.get().strip()
        new_age = age_entry.get().strip()
        new_weight = weight_entry.get().strip()

        if not new_username or not new_email:
            messagebox.showerror("Error", "Username and email are required!")
            return

        try:
            if new_age:
                new_age = int(new_age)
            if new_weight:
                new_weight = float(new_weight)
        except ValueError:
            messagebox.showerror("Error", "Age must be a whole number and weight must be a number!")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users 
                SET username = %s, email = %s, age = %s, weight = %s 
                WHERE id = %s
            ''', (new_username, new_email, new_age if new_age else None, new_weight if new_weight else None, user_id))
            conn.commit()
            messagebox.showinfo("Success", "User updated successfully!")
            edit_window.destroy()
            # Refresh the user list
            manage_users()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()
            conn.close()

    # Save button
    Button(form_frame, text="Save Changes", command=save_changes,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground="#1565C0").pack(fill=X, pady=20)

    # Footer
    footer_frame = Frame(edit_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=edit_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

def add_new_user():
    add_window = Toplevel(root)
    add_window.title("Add New User - FitForge Admin")
    add_window.geometry("500x400")
    add_window.configure(bg=PRIMARY_COLOR)

    # Header
    header_frame = Frame(add_window, bg=ADMIN_COLOR, height=60)
    header_frame.pack(fill=X)
    Label(header_frame, text="Add New User", font=FONT_BOLD, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(add_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Form frame
    form_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    form_frame.pack(fill=BOTH, expand=True)

    # Username
    Label(form_frame, text="Username", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    username_entry = Entry(form_frame, font=FONT_REGULAR)
    username_entry.pack(fill=X, pady=5)

    # Email
    Label(form_frame, text="Email", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    email_entry = Entry(form_frame, font=FONT_REGULAR)
    email_entry.pack(fill=X, pady=5)

    # Password
    Label(form_frame, text="Password", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    password_entry = Entry(form_frame, font=FONT_REGULAR, show="*")
    password_entry.pack(fill=X, pady=5)

    # Age
    Label(form_frame, text="Age", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    age_entry = Entry(form_frame, font=FONT_REGULAR)
    age_entry.pack(fill=X, pady=5)

    # Weight
    Label(form_frame, text="Weight (kg)", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    weight_entry = Entry(form_frame, font=FONT_REGULAR)
    weight_entry.pack(fill=X, pady=5)

    def save_user():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        age = age_entry.get().strip()
        weight = weight_entry.get().strip()

        if not username or not email or not password:
            messagebox.showerror("Error", "Username, email and password are required!")
            return

        try:
            if age:
                age = int(age)
            if weight:
                weight = float(weight)
        except ValueError:
            messagebox.showerror("Error", "Age must be a whole number and weight must be a number!")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, age, weight)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, email, password, age if age else None, weight if weight else None))
            conn.commit()
            messagebox.showinfo("Success", "User added successfully!")
            add_window.destroy()
            # Refresh the user list
            manage_users()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()
            conn.close()

    # Save button
    Button(form_frame, text="Add User", command=save_user,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground="#1565C0").pack(fill=X, pady=20)

    # Footer
    footer_frame = Frame(add_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=add_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

def view_all_plans():
    global current_window
    close_current_window()

    plans_window = Toplevel(root)
    plans_window.title("All Diet Plans - FitForge Admin")
    plans_window.geometry("1200x800")
    plans_window.configure(bg=PRIMARY_COLOR)
    current_window = plans_window

    # Header
    header_frame = Frame(plans_window, bg=ADMIN_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="All Diet Plans", font=FONT_TITLE, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # Back button
    Button(header_frame, text="Back", command=lambda: [plans_window.destroy(), open_admin_dashboard()],
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#1565C0").pack(side=RIGHT, padx=20)

    # Content
    content_frame = Frame(plans_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Fetch all diet plans with user info
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT dc.id, dc.user_id, u.username, dc.diet_type, dc.diet_details, dc.created_at 
        FROM diet_charts dc
        JOIN users u ON dc.user_id = u.id
        ORDER BY dc.created_at DESC
    ''')
    diet_plans = cursor.fetchall()
    cursor.close()
    conn.close()

    if not diet_plans:
        Label(content_frame, text="No diet plans found.", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=50)
    else:
        # Create Treeview with scrollbar
        tree_frame = Frame(content_frame, bg=PRIMARY_COLOR)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=FONT_REGULAR)
        style.configure("mystyle.Treeview.Heading", font=FONT_BOLD)
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "User", "Type", "Created"), show="headings", style="mystyle.Treeview")
        
        # Define headings
        tree.heading("ID", text="Plan ID")
        tree.heading("User", text="User")
        tree.heading("Type", text="Diet Type")
        tree.heading("Created", text="Created At")
        
        # Configure columns
        tree.column("ID", width=80, anchor="center")
        tree.column("User", width=150, anchor="w")
        tree.column("Type", width=150, anchor="w")
        tree.column("Created", width=150, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill=BOTH, expand=True)
        
        # Insert data
        for plan in diet_plans:
            tree.insert("", "end", values=(
                plan['id'],
                plan['username'],
                plan['diet_type'],
                plan['created_at'].strftime('%Y-%m-%d %H:%M')
            ))
        
        # Function to view selected diet plan
        def view_selected_plan():
            selected_item = tree.focus()
            if selected_item:
                item_data = tree.item(selected_item)
                plan_id = item_data['values'][0]
                # Find the full plan data
                for plan in diet_plans:
                    if plan['id'] == plan_id:
                        display_diet_plan_admin(plan)
                        break
        
        # View button
        Button(content_frame, text="View Selected Plan", command=view_selected_plan, 
               bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=10,
               activebackground="#1565C0").pack(pady=20)

def display_diet_plan_admin(plan):
    plan_window = Toplevel(root)
    plan_window.title(f"Diet Plan #{plan['id']} - FitForge Admin")
    plan_window.geometry("900x700")
    plan_window.configure(bg=PRIMARY_COLOR)

    # Header
    header_frame = Frame(plan_window, bg=ADMIN_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text=f"Diet Plan for {plan['username']}", font=FONT_TITLE, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(plan_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Info frame
    info_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    info_frame.pack(fill=X, pady=(0, 20))
    
    Label(info_frame, text=f"Plan ID: {plan['id']}", font=FONT_BOLD, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(side=LEFT)
    Label(info_frame, text=f"User: {plan['username']} (ID: {plan['user_id']})", font=FONT_BOLD, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(side=LEFT, padx=20)
    Label(info_frame, text=f"Created: {plan['created_at'].strftime('%Y-%m-%d %H:%M')}", font=FONT_BOLD, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(side=LEFT)

    # Plan details
    details_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT)
    details_frame.pack(fill=BOTH, expand=True)
    
    scrollbar = Scrollbar(details_frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    plan_text = Text(details_frame, wrap=WORD, yscrollcommand=scrollbar.set,
                    font=FONT_REGULAR, bg="white", fg=TEXT_COLOR, padx=20, pady=20,
                    bd=0, highlightthickness=0)
    plan_text.pack(fill=BOTH, expand=True)
    scrollbar.config(command=plan_text.yview)
    
    # Format and insert the plan details
    plan_text.insert(END, f"{plan['diet_type']} Diet Plan\n\n", "title")
    plan_text.insert(END, plan['diet_details'])
    
    # Configure tags for styling
    plan_text.tag_config("title", font=("Segoe UI", 20, "bold"), foreground=ADMIN_COLOR, spacing3=10)
    
    # Make the text read-only
    plan_text.config(state=DISABLED)
    
    # Footer
    footer_frame = Frame(plan_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    
    def delete_plan():
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this diet plan?")
        if confirm:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM diet_charts WHERE id = %s', (plan['id'],))
                conn.commit()
                messagebox.showinfo("Success", "Diet plan deleted successfully!")
                plan_window.destroy()
                # Refresh the plans list
                view_all_plans()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")
            finally:
                cursor.close()
                conn.close()
    
    Button(footer_frame, text="Delete Plan", command=delete_plan,
           bg="#D32F2F", fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#B71C1C").pack(side=LEFT, padx=20)
    
    Button(footer_frame, text="Close", command=plan_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

def view_statistics():
    stats_window = Toplevel(root)
    stats_window.title("System Statistics - FitForge Admin")
    stats_window.geometry("800x600")
    stats_window.configure(bg=PRIMARY_COLOR)

    # Header
    header_frame = Frame(stats_window, bg=ADMIN_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="System Statistics", font=FONT_TITLE, bg=ADMIN_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # Back button
    Button(header_frame, text="Back", command=stats_window.destroy,
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#1565C0").pack(side=RIGHT, padx=20)

    # Content
    content_frame = Frame(stats_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Fetch statistics from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # User count
    cursor.execute('SELECT COUNT(*) as user_count FROM users')
    user_count = cursor.fetchone()['user_count']
    
    # Admin count
    cursor.execute('SELECT COUNT(*) as admin_count FROM admins')
    admin_count = cursor.fetchone()['admin_count']
    
    # Diet plans count
    cursor.execute('SELECT COUNT(*) as plan_count FROM diet_charts')
    plan_count = cursor.fetchone()['plan_count']
    
    # Diet types distribution
    cursor.execute('''
        SELECT diet_type, COUNT(*) as count 
        FROM diet_charts 
        GROUP BY diet_type 
        ORDER BY count DESC
    ''')
    diet_types = cursor.fetchall()
    
    cursor.close()
    conn.close()

    # Statistics cards
    stats_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    stats_frame.pack(fill=BOTH, expand=True)

    # Card 1: Users
    user_card = Frame(stats_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    user_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    Label(user_card, text="👥 Total Users", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack()
    Label(user_card, text=str(user_count), font=("Segoe UI", 36, "bold"), bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=10)

    # Card 2: Admins
    admin_card = Frame(stats_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    admin_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    Label(admin_card, text="🛡️ Total Admins", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack()
    Label(admin_card, text=str(admin_count), font=("Segoe UI", 36, "bold"), bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=10)

    # Card 3: Diet Plans
    plan_card = Frame(stats_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    plan_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    
    Label(plan_card, text="📋 Total Diet Plans", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ADMIN_COLOR).pack()
    Label(plan_card, text=str(plan_count), font=("Segoe UI", 36, "bold"), bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=10)

    # Diet types distribution
    dist_frame = Frame(content_frame, bg=PRIMARY_COLOR, pady=20)
    dist_frame.pack(fill=BOTH, expand=True)
    
    Label(dist_frame, text="Diet Plans Distribution", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=ADMIN_COLOR).pack(anchor="w")
    
    # Create a frame for the distribution table
    table_frame = Frame(dist_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT)
    table_frame.pack(fill=BOTH, expand=True, pady=10)
    
    # Create table headers
    header1 = Frame(table_frame, bg=ADMIN_COLOR)
    header1.pack(fill=X)
    Label(header1, text="Diet Type", font=FONT_BOLD, bg=ADMIN_COLOR, fg="white", width=30).pack(side=LEFT, padx=1, pady=1)
    Label(header1, text="Count", font=FONT_BOLD, bg=ADMIN_COLOR, fg="white", width=15).pack(side=LEFT, padx=1, pady=1)
    Label(header1, text="Percentage", font=FONT_BOLD, bg=ADMIN_COLOR, fg="white", width=15).pack(side=LEFT, padx=1, pady=1)
    
    # Add diet type rows
    for diet in diet_types:
        row = Frame(table_frame, bg="white")
        row.pack(fill=X)
        
        percentage = (diet['count'] / plan_count) * 100 if plan_count > 0 else 0
        
        Label(row, text=diet['diet_type'], font=FONT_REGULAR, bg="white", fg=ACCENT_COLOR, width=30).pack(side=LEFT, padx=1, pady=1)
        Label(row, text=str(diet['count']), font=FONT_REGULAR, bg="white", fg=ACCENT_COLOR, width=15).pack(side=LEFT, padx=1, pady=1)
        Label(row, text=f"{percentage:.1f}%", font=FONT_REGULAR, bg="white", fg=ACCENT_COLOR, width=15).pack(side=LEFT, padx=1, pady=1)

    # Configure grid weights
    stats_frame.grid_columnconfigure(0, weight=1)
    stats_frame.grid_columnconfigure(1, weight=1)
    stats_frame.grid_columnconfigure(2, weight=1)

    # Footer
    footer_frame = Frame(stats_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=stats_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

# Open Dashboard with modern UI
def open_dashboard(user_id):
    global current_window
    close_current_window()

    dashboard_window = Toplevel(root)
    dashboard_window.title("FitForge Dashboard")
    dashboard_window.geometry("1200x800")
    dashboard_window.configure(bg=PRIMARY_COLOR)
    current_window = dashboard_window

    # Header with cult.fit inspired design
    header_frame = Frame(dashboard_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    
    Label(header_frame, text="FitForge", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # User info
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username, age, weight FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # User info frame
    user_frame = Frame(header_frame, bg=SECONDARY_COLOR)
    user_frame.pack(side=RIGHT, padx=20)
    
    Label(user_frame, text=f"Hello, {user['username']}!", font=FONT_SUBTITLE, bg=SECONDARY_COLOR, fg="white").pack(anchor="e")
    if user['age'] and user['weight']:
        Label(user_frame, text=f"Age: {user['age']} | Weight: {user['weight']} kg", 
              font=FONT_REGULAR, bg=SECONDARY_COLOR, fg="white").pack(anchor="e")
    
    # Edit profile button
    Button(user_frame, text="Edit Profile", command=lambda: open_profile_edit(user_id),
           bg=SECONDARY_COLOR, fg="white", font=FONT_REGULAR, relief=FLAT, bd=0,
           activebackground=BUTTON_HOVER).pack(anchor="e")

    # Main content
    content_frame = Frame(dashboard_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

    # Dashboard cards
    card_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    card_frame.pack(fill=BOTH, expand=True)

    # Card 1: Exercise Plan
    exercise_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    exercise_card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    exercise_card.grid_propagate(False)
    
    Label(exercise_card, text="🏋️ Exercise Plans", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=(20,10))
    Label(exercise_card, text="Custom workout routines for your goals", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(exercise_card, text="Get Started", command=lambda: open_exercise_page(user_id), 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground=BUTTON_HOVER).pack(pady=20)

    # Card 2: Diet Plan
    diet_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    diet_card.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    diet_card.grid_propagate(False)
    
    Label(diet_card, text="🥗 Diet Plans", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=(20,10))
    Label(diet_card, text="Personalized nutrition for your fitness journey", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(diet_card, text="Get Started", command=lambda: generate_diet(user_id), 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground=BUTTON_HOVER).pack(pady=20)

    # Card 3: View Diet Charts
    view_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    view_card.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
    view_card.grid_propagate(False)
    
    Label(view_card, text="📊 My Plans", font=FONT_LARGE, bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=(20,10))
    Label(view_card, text="View your saved exercise and diet plans", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(view_card, text="View", command=lambda: view_diet_charts(user_id), 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground=BUTTON_HOVER).pack(pady=20)

    # Card 4: Virtual Coaching (NEW)
    coaching_card = Frame(card_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=300, height=200)
    coaching_card.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    coaching_card.grid_propagate(False)
    
    Label(coaching_card, text="🎯 Virtual Coach", font=FONT_LARGE, bg=LIGHT_GRAY, fg=COACHING_COLOR).pack(pady=(20,10))
    Label(coaching_card, text="Get expert guidance and feedback", font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack()
    Button(coaching_card, text="Start Session", command=lambda: open_virtual_coaching(user_id), 
           bg=COACHING_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground="#7b1fa2").pack(pady=20)

    # Configure grid weights
    card_frame.grid_columnconfigure(0, weight=1)
    card_frame.grid_columnconfigure(1, weight=1)
    card_frame.grid_columnconfigure(2, weight=1)
    card_frame.grid_rowconfigure(0, weight=1)
    card_frame.grid_rowconfigure(1, weight=1)

    # Footer
    footer_frame = Frame(dashboard_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    
    Button(footer_frame, text="Logout", command=dashboard_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)
    
    Button(footer_frame, text="Exit", command=exit_application, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

# Virtual Coaching Feature
def open_virtual_coaching(user_id):
    global current_window
    close_current_window()

    coaching_window = Toplevel(root)
    coaching_window.title("Virtual Coaching - FitForge")
    coaching_window.geometry("1200x800")
    coaching_window.configure(bg=PRIMARY_COLOR)
    current_window = coaching_window

    # Header
    header_frame = Frame(coaching_window, bg=COACHING_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Virtual Coaching", font=FONT_TITLE, bg=COACHING_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(coaching_window, user_id)

    # Content
    content_frame = Frame(coaching_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Main coaching interface
    main_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    main_frame.pack(fill=BOTH, expand=True)

    # Left panel - coach messages
    left_frame = Frame(main_frame, bg=PRIMARY_COLOR, width=400)
    left_frame.pack(side=LEFT, fill=Y, padx=(0, 20))

    # Coach header
    coach_header = Frame(left_frame, bg=COACHING_COLOR, height=60)
    coach_header.pack(fill=X)
    Label(coach_header, text="Your Virtual Coach", font=FONT_BOLD, bg=COACHING_COLOR, fg="white").pack(side=LEFT, padx=15)

    # Coach messages area
    messages_frame = Frame(left_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT)
    messages_frame.pack(fill=BOTH, expand=True, pady=(0, 20))

    scrollbar = Scrollbar(messages_frame)
    scrollbar.pack(side=RIGHT, fill=Y)

    messages_text = Text(messages_frame, wrap=WORD, yscrollcommand=scrollbar.set,
                        font=FONT_REGULAR, bg="white", fg=TEXT_COLOR, padx=15, pady=15,
                        bd=0, highlightthickness=0)
    messages_text.pack(fill=BOTH, expand=True)
    scrollbar.config(command=messages_text.yview)

    # Sample coaching messages
    welcome_message = """Welcome to your virtual coaching session!
    
I'm Coach Alex, your AI-powered fitness assistant. I'm here to guide you through your fitness journey with personalized advice and real-time feedback.

How can I help you today?"""

    messages_text.insert(END, f"Coach Alex [{datetime.datetime.now().strftime('%H:%M')}]:\n", "coach_time")
    messages_text.insert(END, welcome_message + "\n\n", "coach_msg")
    
    # Configure tags for styling
    messages_text.tag_config("coach_time", font=("Segoe UI", 10), foreground="#666666")
    messages_text.tag_config("coach_msg", font=("Segoe UI", 12), foreground=ACCENT_COLOR, spacing3=5)
    messages_text.tag_config("user_msg", font=("Segoe UI", 12), foreground=SECONDARY_COLOR, spacing3=5)
    
    # Make the text read-only
    messages_text.config(state=DISABLED)

    # Right panel - user input and resources
    right_frame = Frame(main_frame, bg=PRIMARY_COLOR)
    right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # Resources section
    resources_frame = Frame(right_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    resources_frame.pack(fill=BOTH, expand=True)

    Label(resources_frame, text="Quick Resources", font=FONT_LARGE, bg="white", fg=COACHING_COLOR).pack(anchor="w")

    # Quick help buttons
    quick_help_frame = Frame(resources_frame, bg="white")
    quick_help_frame.pack(fill=X, pady=10)

    Button(quick_help_frame, text="Form Check", command=lambda: send_coach_message("Can you check my exercise form?", messages_text),
           bg=COACHING_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground="#7b1fa2").pack(side=LEFT, padx=5)

    Button(quick_help_frame, text="Progress Tips", command=lambda: send_coach_message("How can I improve my progress?", messages_text),
           bg=COACHING_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground="#7b1fa2").pack(side=LEFT, padx=5)

    Button(quick_help_frame, text="Motivation", command=lambda: send_coach_message("I need some motivation today", messages_text),
           bg=COACHING_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground="#7b1fa2").pack(side=LEFT, padx=5)

    # Video call button
    Button(resources_frame, text="📹 Start Video Call", command=lambda: start_video_call(),
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=10,
           activebackground=BUTTON_HOVER).pack(fill=X, pady=20)

    # User input area
    input_frame = Frame(right_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=20, pady=20)
    input_frame.pack(fill=BOTH)

    Label(input_frame, text="Ask Your Coach", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")

    user_input = Text(input_frame, height=3, wrap=WORD, font=FONT_REGULAR, bg=LIGHT_GRAY, fg=TEXT_COLOR,
                     bd=0, highlightthickness=1, highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    user_input.pack(fill=X, pady=10)

    def send_message():
        message = user_input.get("1.0", END).strip()
        if message:
            # Display user message
            messages_text.config(state=NORMAL)
            messages_text.insert(END, f"You [{datetime.datetime.now().strftime('%H:%M')}]:\n", "user_time")
            messages_text.insert(END, message + "\n\n", "user_msg")
            
            # Clear input
            user_input.delete("1.0", END)
            
            # Simulate coach response
            messages_text.insert(END, f"Coach Alex [{datetime.datetime.now().strftime('%H:%M')}]:\n", "coach_time")
            coach_response = generate_coach_response(message)
            messages_text.insert(END, coach_response + "\n\n", "coach_msg")
            
            # Scroll to bottom
            messages_text.see(END)
            messages_text.config(state=DISABLED)

    Button(input_frame, text="Send", command=send_message,
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=5,
           activebackground=BUTTON_HOVER).pack(side=RIGHT)

    # Bind Enter key to send message
    user_input.bind('<Return>', lambda event: [send_message(), "break"])

    # Footer
    footer_frame = Frame(coaching_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=coaching_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

def send_coach_message(message, messages_text):
    messages_text.config(state=NORMAL)
    messages_text.insert(END, f"You [{datetime.datetime.now().strftime('%H:%M')}]:\n", "user_time")
    messages_text.insert(END, message + "\n\n", "user_msg")
    
    # Simulate coach response
    messages_text.insert(END, f"Coach Alex [{datetime.datetime.now().strftime('%H:%M')}]:\n", "coach_time")
    coach_response = generate_coach_response(message)
    messages_text.insert(END, coach_response + "\n\n", "coach_msg")
    
    # Scroll to bottom
    messages_text.see(END)
    messages_text.config(state=DISABLED)

def generate_coach_response(message):
    """Generate a simulated coach response based on user input"""
    message = message.lower()
    
    if any(word in message for word in ["form", "technique", "posture"]):
        return """Great question! Proper form is essential for effectiveness and injury prevention. 

For most exercises:
1. Keep your core engaged
2. Maintain a neutral spine
3. Move through a full range of motion
4. Control the movement

Would you like me to analyze a specific exercise?"""
    
    elif any(word in message for word in ["progress", "improve", "better"]):
        return """To improve your progress, I recommend:
        
1. Track your workouts consistently
2. Gradually increase weight or reps
3. Ensure proper recovery (sleep 7-9 hours)
4. Stay hydrated and follow your nutrition plan

What specific area would you like to focus on?"""
    
    elif any(word in message for word in ["motivation", "motivated", "tired"]):
        return """I hear you! Here's some motivation:

Remember why you started! Every workout brings you closer to your goals. 

Try these tips:
1. Set small, achievable targets
2. Find a workout buddy
3. Play energizing music
4. Focus on how good you'll feel AFTER the workout

You've got this! 💪"""
    
    elif any(word in message for word in ["diet", "nutrition", "eat"]):
        return """Nutrition is key! Here are some general guidelines:

1. Prioritize protein with each meal
2. Include plenty of vegetables
3. Stay hydrated (3-4L water/day)
4. Time carbs around workouts

Would you like me to review your current diet plan?"""
    
    else:
        return """Thanks for your message! I'm here to help with:
        
- Exercise technique checks
- Workout programming advice
- Nutrition guidance
- Progress tracking
- Motivation and accountability

What specific question can I help with today?"""

def start_video_call():
    """Simulate starting a video call with a coach"""
    response = messagebox.askyesno("Video Call", "Would you like to start a video call with a certified coach?\n\n(Note: This would connect to a real coach in the full version)")
    if response:
        messagebox.showinfo("Video Call", "Connecting you to a coach now...\n\nIn the full version, this would launch a video call interface.")
        # In a real implementation, this would start a video call using WebRTC or similar technology

# View all diet charts for a user
def view_diet_charts(user_id):
    global current_window
    close_current_window()

    charts_window = Toplevel(root)
    charts_window.title("My Plans - FitForge")
    charts_window.geometry("1200x800")
    charts_window.configure(bg=PRIMARY_COLOR)
    current_window = charts_window

    # Header
    header_frame = Frame(charts_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="My Plans", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(charts_window, user_id)

    # Content
    content_frame = Frame(charts_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Fetch all diet charts for this user
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM diet_charts WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    diet_charts = cursor.fetchall()
    cursor.close()
    conn.close()

    if not diet_charts:
        Label(content_frame, text="No plans found. Generate one first!", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=50)
    else:
        # Create a modern list view
        tree_frame = Frame(content_frame, bg=PRIMARY_COLOR)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=FONT_REGULAR)
        style.configure("mystyle.Treeview.Heading", font=FONT_BOLD)
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        
        tree = ttk.Treeview(tree_frame, columns=("Type", "Date"), show="headings", style="mystyle.Treeview")
        
        # Define headings
        tree.heading("Type", text="Plan Type")
        tree.heading("Date", text="Created Date")
        
        # Configure columns
        tree.column("Type", width=200, anchor="w")
        tree.column("Date", width=150, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill=BOTH, expand=True)
        
        # Insert data
        for chart in diet_charts:
            tree.insert("", "end", values=(chart['diet_type'], chart['created_at'].strftime('%Y-%m-%d')))
        
        # Function to view selected diet chart
        def view_selected_chart():
            selected_item = tree.focus()
            if selected_item:
                item_data = tree.item(selected_item)
                chart_type = item_data['values'][0]
                # Find the full chart data
                for chart in diet_charts:
                    if chart['diet_type'] == chart_type:
                        display_diet_chart(chart, user_id)
                        break
        
        # View button
        Button(content_frame, text="View Selected Plan", command=view_selected_chart, 
               bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=20, pady=10,
               activebackground=BUTTON_HOVER).pack(pady=20)

    # Footer
    footer_frame = Frame(charts_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=charts_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

# Display a single diet chart
def display_diet_chart(chart, user_id):
    chart_window = Toplevel(root)
    chart_window.title(f"{chart['diet_type']} Plan - FitForge")
    chart_window.geometry("900x700")
    chart_window.configure(bg=PRIMARY_COLOR)

    # Header
    header_frame = Frame(chart_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text=f"{chart['diet_type']} Plan", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(chart_window, user_id)

    # Content
    content_frame = Frame(chart_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Create a text widget with modern styling
    text_frame = Frame(content_frame, bg=PRIMARY_COLOR, bd=0, highlightthickness=0)
    text_frame.pack(fill=BOTH, expand=True)
    
    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    diet_text = Text(text_frame, wrap=WORD, yscrollcommand=scrollbar.set,
                    font=FONT_REGULAR, bg="white", fg=TEXT_COLOR, padx=20, pady=20,
                    bd=0, highlightthickness=0)
    diet_text.pack(fill=BOTH, expand=True)
    scrollbar.config(command=diet_text.yview)
    
    # Format and insert the diet details
    diet_details = chart['diet_details']
    diet_text.insert(END, f"Your {chart['diet_type']} Plan\n\n", "title")
    diet_text.insert(END, f"Created on: {chart['created_at'].strftime('%B %d, %Y')}\n\n", "subtitle")
    diet_text.insert(END, diet_details)
    
    # Configure tags for styling
    diet_text.tag_config("title", font=("Segoe UI", 20, "bold"), foreground=SECONDARY_COLOR, spacing3=10)
    diet_text.tag_config("subtitle", font=("Segoe UI", 12), foreground="#666666", spacing2=10)
    
    # Make the text read-only
    diet_text.config(state=DISABLED)
    
    # Footer
    footer_frame = Frame(chart_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=chart_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

# Select Exercise Plan
def open_exercise_page(user_id):
    global current_window
    close_current_window()

    exercise_window = Toplevel(root)
    exercise_window.title("Exercise Plans - FitForge")
    exercise_window.geometry("1200x800")
    exercise_window.configure(bg=PRIMARY_COLOR)
    current_window = exercise_window

    # Header
    header_frame = Frame(exercise_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Exercise Plans", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(exercise_window, user_id)

    # Content
    content_frame = Frame(exercise_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

    Label(content_frame, text="Choose Your Workout Plan", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(pady=(0,20))

    # Exercise options in a modern grid
    exercise_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    exercise_frame.pack(fill=BOTH, expand=True)

    exercises = [
        {"name": "Push", "desc": "Chest, Shoulders & Triceps", "icon": "💪", "image": "https://i.imgur.com/JqYeZ0L.jpg"},
        {"name": "Pull", "desc": "Back & Biceps", "icon": "🏋️", "image": "https://i.imgur.com/vYJ3nPg.jpg"},
        {"name": "Legs", "desc": "Lower Body Workout", "icon": "🦵", "image": "https://i.imgur.com/5XZwWQm.jpg"},
        {"name": "Cardio", "desc": "Heart Health & Endurance", "icon": "🏃", "image": "https://i.imgur.com/8KZQY9x.jpg"},
        {"name": "Core", "desc": "Abs & Core Strength", "icon": "🧘", "image": "https://i.imgur.com/3JvY9ZL.jpg"},
        {"name": "Full Body", "desc": "Complete Workout", "icon": "🔥", "image": "https://i.imgur.com/9QZQZ9Q.jpg"}
    ]

    for i, exercise in enumerate(exercises):
        card = Frame(exercise_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, width=250, height=180)
        card.grid(row=i//3, column=i%3, padx=20, pady=20, sticky="nsew")
        card.grid_propagate(False)
        
        Label(card, text=exercise["icon"], font=("Segoe UI", 24), bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack(pady=(20,5))
        Label(card, text=exercise["name"], font=FONT_LARGE, bg=LIGHT_GRAY, fg=ACCENT_COLOR).pack()
        Label(card, text=exercise["desc"], font=FONT_SUBTITLE, bg=LIGHT_GRAY, fg=TEXT_COLOR).pack(pady=5)
        
        Button(card, text="Select", command=lambda ex=exercise["name"], img=exercise["image"]: open_exercise_detail(user_id, ex, img), 
               bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
               activebackground=BUTTON_HOVER).pack(pady=10)

    # Configure grid weights
    exercise_frame.grid_columnconfigure(0, weight=1)
    exercise_frame.grid_columnconfigure(1, weight=1)
    exercise_frame.grid_columnconfigure(2, weight=1)

    # Footer
    footer_frame = Frame(exercise_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=exercise_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

# Open Exercise Detail with enhanced timer and exercise image
def open_exercise_detail(user_id, exercise_type, image_url):
    global current_window, timer_running, timer_start_time, timer_paused_time
    close_current_window()

    exercise_detail_window = Toplevel(root)
    exercise_detail_window.title(f"{exercise_type} Workout - FitForge")
    exercise_detail_window.geometry("1200x800")
    exercise_detail_window.configure(bg=PRIMARY_COLOR)
    current_window = exercise_detail_window

    # Reset timer state when opening new window
    timer_running = False
    timer_start_time = 0
    timer_paused_time = 0

    # Header
    header_frame = Frame(exercise_detail_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text=f"{exercise_type} Workout", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(exercise_detail_window, user_id)

    # Content
    content_frame = Frame(exercise_detail_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Main content frame with image and exercises
    main_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    main_frame.pack(fill=BOTH, expand=True)

    # Left frame for exercise image
    image_frame = Frame(main_frame, bg=PRIMARY_COLOR, width=400)
    image_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
    
    try:
        # Load image from URL
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((400, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        image_label = Label(image_frame, image=photo, bg=PRIMARY_COLOR)
        image_label.image = photo  # Keep a reference
        image_label.pack(pady=10)
    except Exception as e:
        print(f"Error loading image: {e}")
        Label(image_frame, text="Exercise Image", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(pady=50)

    # Right frame for exercise details
    details_frame = Frame(main_frame, bg=PRIMARY_COLOR)
    details_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # Sample exercise routine (would be fetched from DB in real app)
    if exercise_type == "Push":
        exercises = [
            {"name": "Bench Press", "sets": "4 sets x 8-12 reps", "desc": "Flat bench, focus on form"},
            {"name": "Shoulder Press", "sets": "3 sets x 10-12 reps", "desc": "Dumbbell or barbell"},
            {"name": "Incline Dumbbell Press", "sets": "3 sets x 10 reps", "desc": "30-45 degree incline"},
            {"name": "Tricep Dips", "sets": "3 sets x 12-15 reps", "desc": "Use parallel bars or bench"},
            {"name": "Lateral Raises", "sets": "3 sets x 12 reps", "desc": "Light weight, controlled motion"}
        ]
    elif exercise_type == "Pull":
        exercises = [
            {"name": "Pull-ups", "sets": "4 sets x 8-12 reps", "desc": "Wide grip if possible"},
            {"name": "Bent Over Rows", "sets": "3 sets x 10-12 reps", "desc": "Barbell or dumbbell"},
            {"name": "Lat Pulldown", "sets": "3 sets x 10 reps", "desc": "Focus on squeezing lats"},
            {"name": "Face Pulls", "sets": "3 sets x 12-15 reps", "desc": "Cable machine, rear delt focus"},
            {"name": "Bicep Curls", "sets": "3 sets x 12 reps", "desc": "Various curl variations"}
        ]
    elif exercise_type == "Legs":
        exercises = [
            {"name": "Squats", "sets": "4 sets x 8-12 reps", "desc": "Barbell back squats"},
            {"name": "Romanian Deadlifts", "sets": "3 sets x 10 reps", "desc": "Hamstring focus"},
            {"name": "Leg Press", "sets": "3 sets x 12 reps", "desc": "Controlled movement"},
            {"name": "Walking Lunges", "sets": "3 sets x 12 steps", "desc": "Bodyweight or dumbbells"},
            {"name": "Calf Raises", "sets": "4 sets x 15 reps", "desc": "Bodyweight or weighted"}
        ]
    elif exercise_type == "Cardio":
        exercises = [
            {"name": "Treadmill Run", "sets": "20-30 minutes", "desc": "Interval training recommended"},
            {"name": "Rowing Machine", "sets": "15-20 minutes", "desc": "Full body cardio"},
            {"name": "Jump Rope", "sets": "5 sets x 1 minute", "desc": "High intensity intervals"},
            {"name": "Stair Climber", "sets": "15-20 minutes", "desc": "Steady pace"},
            {"name": "Cycling", "sets": "30 minutes", "desc": "Outdoor or stationary bike"}
        ]
    elif exercise_type == "Core":
        exercises = [
            {"name": "Plank", "sets": "3 sets x 60 sec", "desc": "Maintain straight line"},
            {"name": "Hanging Leg Raises", "sets": "3 sets x 12 reps", "desc": "Control the movement"},
            {"name": "Russian Twists", "sets": "3 sets x 20 reps", "desc": "Weighted for added difficulty"},
            {"name": "Cable Woodchoppers", "sets": "3 sets x 12/side", "desc": "Rotational core strength"},
            {"name": "Ab Wheel Rollouts", "sets": "3 sets x 10 reps", "desc": "Advanced movement"}
        ]
    else:  # Full Body
        exercises = [
            {"name": "Deadlifts", "sets": "4 sets x 6-8 reps", "desc": "Compound movement"},
            {"name": "Squats", "sets": "3 sets x 8-10 reps", "desc": "Barbell or goblet"},
            {"name": "Pull-ups", "sets": "3 sets x 8 reps", "desc": "Assisted if needed"},
            {"name": "Overhead Press", "sets": "3 sets x 8 reps", "desc": "Standing or seated"},
            {"name": "Burpees", "sets": "3 sets x 10 reps", "desc": "Full body conditioning"}
        ]

    # Create exercise cards
    for i, exercise in enumerate(exercises):
        card = Frame(details_frame, bg=LIGHT_GRAY, bd=0, highlightthickness=0, relief=FLAT, padx=15, pady=10)
        card.pack(fill=X, pady=5)
        
        Label(card, text=f"{i+1}. {exercise['name']}", font=FONT_BOLD, bg=LIGHT_GRAY, fg=ACCENT_COLOR, anchor="w").pack(fill=X)
        Label(card, text=exercise['sets'], font=FONT_REGULAR, bg=LIGHT_GRAY, fg=SECONDARY_COLOR, anchor="w").pack(fill=X)
        Label(card, text=exercise['desc'], font=FONT_REGULAR, bg=LIGHT_GRAY, fg=TEXT_COLOR, anchor="w").pack(fill=X)

    # Timer section
    timer_frame = Frame(content_frame, bg=PRIMARY_COLOR, pady=20)
    timer_frame.pack(fill=X)
    
    Label(timer_frame, text="Workout Timer", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack()
    
    timer_label = Label(timer_frame, text="00:00:00", font=("Segoe UI", 36, "bold"), bg=PRIMARY_COLOR, fg=SECONDARY_COLOR)
    timer_label.pack(pady=10)
    
    button_frame = Frame(timer_frame, bg=PRIMARY_COLOR)
    button_frame.pack()
    
    # Timer buttons
    Button(button_frame, text="Start", command=lambda: start_timer(timer_label), 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground=BUTTON_HOVER).pack(side=LEFT, padx=5)
    
    Button(button_frame, text="Pause", command=pause_timer, 
           bg="#FFC107", fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground="#FFA000").pack(side=LEFT, padx=5)
    
    Button(button_frame, text="Reset", command=lambda: reset_timer(timer_label), 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
           activebackground="#444444").pack(side=LEFT, padx=5)

    # Footer
    footer_frame = Frame(exercise_detail_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=exercise_detail_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

# Generate Diet Chart
def generate_diet(user_id):
    global current_window
    close_current_window()

    diet_window = Toplevel(root)
    diet_window.title("Diet Plans - FitForge")
    diet_window.geometry("1200x800")
    diet_window.configure(bg=PRIMARY_COLOR)
    current_window = diet_window

    # Header
    header_frame = Frame(diet_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Diet Plans", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(diet_window, user_id)

    # Content
    content_frame = Frame(diet_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

    Label(content_frame, text="Choose Your Diet Plan", font=FONT_LARGE, bg=PRIMARY_COLOR, fg=ACCENT_COLOR).pack(pady=(0,20))

    # Diet options in modern cards
    diet_frame = Frame(content_frame, bg=PRIMARY_COLOR)
    diet_frame.pack(fill=BOTH, expand=True)

    diet_options = [
        {
            "type": "Weight Loss", 
            "desc": "Calorie deficit plan for fat loss",
            "icon": "⚖️",
            "color": "#4CAF50"
        },
        {
            "type": "Muscle Gain", 
            "desc": "High protein plan for muscle growth",
            "icon": "💪",
            "color": "#2196F3"
        },
        {
            "type": "Maintenance", 
            "desc": "Balanced nutrition for weight maintenance",
            "icon": "🍽️",
            "color": "#9C27B0"
        }
    ]

    for i, diet in enumerate(diet_options):
        card = Frame(diet_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, width=300, height=220)
        card.grid(row=0, column=i, padx=20, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        # Card header with color
        header = Frame(card, bg=diet["color"], height=5)
        header.pack(fill=X)
        
        Label(card, text=diet["icon"], font=("Segoe UI", 36), bg="white", fg=diet["color"]).pack(pady=(20,5))
        Label(card, text=diet["type"], font=FONT_LARGE, bg="white", fg=ACCENT_COLOR).pack()
        Label(card, text=diet["desc"], font=FONT_SUBTITLE, bg="white", fg=TEXT_COLOR, wraplength=250).pack(pady=10, padx=10)
        
        Button(card, text="Select Plan", command=lambda dt=diet["type"]: save_and_show_diet(user_id, dt), 
               bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=15, pady=5,
               activebackground=BUTTON_HOVER).pack(pady=10)

    # Configure grid weights
    diet_frame.grid_columnconfigure(0, weight=1)
    diet_frame.grid_columnconfigure(1, weight=1)
    diet_frame.grid_columnconfigure(2, weight=1)

    # Footer
    footer_frame = Frame(diet_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=diet_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)

# Save Diet to Database and show it
def save_and_show_diet(user_id, diet_type):
    # Define diet details based on type
    diet_details = ""
    if diet_type == "Weight Loss":
        diet_details = """=== WEIGHT LOSS DIET PLAN ===
        
BREAKFAST (7-8 AM):
• Oatmeal with berries and almonds (1 cup)
• Green tea or black coffee
• 1 boiled egg

MID-MORNING SNACK (10-11 AM):
• Greek yogurt with flaxseeds (1 cup)
• Handful of nuts (almonds/walnuts)

LUNCH (1-2 PM):
• Grilled chicken breast (150g) or tofu
• Steamed vegetables (broccoli, carrots, beans)
• Quinoa or brown rice (1/2 cup)

AFTERNOON SNACK (4-5 PM):
• Protein shake or green smoothie
• 1 small apple with peanut butter

DINNER (7-8 PM):
• Baked salmon or grilled fish (150g)
• Large salad with leafy greens
• 1 small sweet potato

HYDRATION:
• Drink at least 3 liters of water daily
• Herbal teas are encouraged

NOTES:
• Avoid processed foods and sugars
• Portion control is key
• Last meal at least 2 hours before bedtime"""
    elif diet_type == "Muscle Gain":
        diet_details = """=== MUSCLE GAIN DIET PLAN ===
        
BREAKFAST (7-8 AM):
• 3 whole eggs + 3 egg whites
• Whole grain toast with avocado
• 1 cup oatmeal with banana
• Protein shake

MID-MORNING SNACK (10-11 AM):
• Chicken breast sandwich on whole wheat
• 1 cup Greek yogurt with granola
• Handful of mixed nuts

LUNCH (1-2 PM):
• Lean beef or salmon (200g)
• Brown rice or sweet potato (1 cup)
• Steamed vegetables
• 1 tbsp olive oil

PRE-WORKOUT (3-4 PM):
• Protein smoothie with banana and peanut butter
• 1 cup cottage cheese

POST-WORKOUT:
• Whey protein shake
• Simple carbs (white rice or banana)

DINNER (7-8 PM):
• Grilled chicken or fish (200g)
• Quinoa or brown rice (1 cup)
• Roasted vegetables
• 1 tbsp olive oil

BEFORE BED:
• Casein protein shake or cottage cheese
• 1 tbsp almond butter

HYDRATION:
• Minimum 4 liters of water daily
• Electrolytes during workouts"""
    elif diet_type == "Maintenance":
        diet_details = """=== MAINTENANCE DIET PLAN ===
        
BREAKFAST (7-8 AM):
• Smoothie with protein powder, spinach, banana, almond milk
• Whole grain toast with avocado
• 2 boiled eggs

MID-MORNING SNACK (10-11 AM):
• Greek yogurt with honey and walnuts
• 1 piece of fruit

LUNCH (1-2 PM):
• Grilled fish or chicken (150g)
• Mixed salad with olive oil dressing
• Quinoa or brown rice (1/2 cup)

AFTERNOON SNACK (4-5 PM):
• Handful of nuts and seeds
• Protein bar or shake

DINNER (7-8 PM):
• Lean protein source (150g)
• Variety of roasted vegetables
• Small portion of complex carbs

HYDRATION:
• 2-3 liters of water daily
• Herbal teas and infused waters

NOTES:
• Balanced macronutrients
• Flexible with occasional treats
• Listen to your body's hunger cues"""

    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO diet_charts (user_id, diet_type, diet_details) VALUES (%s, %s, %s)', 
                  (user_id, diet_type, diet_details))
    conn.commit()
    
    # Get the inserted chart ID
    chart_id = cursor.lastrowid
    cursor.close()
    conn.close()

    # Show the generated diet chart
    display_generated_diet(diet_type, diet_details, user_id)

# Display the newly generated diet chart
def display_generated_diet(diet_type, diet_details, user_id):
    chart_window = Toplevel(root)
    chart_window.title(f"{diet_type} Diet Plan - FitForge")
    chart_window.geometry("900x700")
    chart_window.configure(bg=PRIMARY_COLOR)

    # Header
    header_frame = Frame(chart_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text=f"{diet_type} Diet Plan", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    add_home_button(chart_window, user_id)

    # Content
    content_frame = Frame(chart_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Create a text widget with modern styling
    text_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT)
    text_frame.pack(fill=BOTH, expand=True)
    
    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    diet_text = Text(text_frame, wrap=WORD, yscrollcommand=scrollbar.set,
                    font=FONT_REGULAR, bg="white", fg=TEXT_COLOR, padx=20, pady=20,
                    bd=0, highlightthickness=0)
    diet_text.pack(fill=BOTH, expand=True)
    scrollbar.config(command=diet_text.yview)
    
    # Format and insert the diet details
    diet_text.insert(END, f"{diet_type} Diet Plan\n\n", "title")
    diet_text.insert(END, "Generated just for you!\n\n", "subtitle")
    diet_text.insert(END, diet_details)
    
    # Configure tags for styling
    diet_text.tag_config("title", font=("Segoe UI", 20, "bold"), foreground=SECONDARY_COLOR, spacing3=10)
    diet_text.tag_config("subtitle", font=("Segoe UI", 12), foreground="#666666", spacing2=10)
    
    # Make the text read-only
    diet_text.config(state=DISABLED)
    
    # Footer
    footer_frame = Frame(chart_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Close", command=chart_window.destroy, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

# Open Signup Page with modern design and age/weight fields
def open_signup_page():
    global current_window, username_entry, email_entry, password_entry, age_entry, weight_entry
    close_current_window()

    signup_window = Toplevel(root)
    signup_window.title("Signup - FitForge")
    signup_window.geometry("1200x800")
    signup_window.configure(bg=PRIMARY_COLOR)
    current_window = signup_window

    # Header
    header_frame = Frame(signup_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Create Account", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(signup_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=150, pady=50)

    # Form frame with shadow effect
    form_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=40, pady=40)
    form_frame.pack(fill=BOTH, expand=True)
    
    # Add subtle shadow
    shadow_frame = Frame(content_frame, bg="#e0e0e0")
    shadow_frame.place(in_=form_frame, x=2, y=2, relwidth=1, relheight=1)
    form_frame.lift()

    Label(form_frame, text="Join FitForge Today", font=FONT_LARGE, bg="white", fg=ACCENT_COLOR).pack(pady=(0,30))

    def on_entry_click(entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, END)
            if placeholder == "Password":
                entry.config(show="*")
    
    def on_focusout(entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            if placeholder == "Password":
                entry.config(show="")

    # Username field
    username_frame = Frame(form_frame, bg="white", pady=10)
    username_frame.pack(fill=X)
    Label(username_frame, text="Username", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    username_entry = Entry(username_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                         highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    username_entry.insert(0, "Username")
    username_entry.bind('<FocusIn>', lambda e: on_entry_click(username_entry, "Username"))
    username_entry.bind('<FocusOut>', lambda e: on_focusout(username_entry, "Username"))
    username_entry.pack(fill=X, ipady=5)

    # Email field
    email_frame = Frame(form_frame, bg="white", pady=10)
    email_frame.pack(fill=X)
    Label(email_frame, text="Email", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    email_entry = Entry(email_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                       highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    email_entry.insert(0, "Email")
    email_entry.bind('<FocusIn>', lambda e: on_entry_click(email_entry, "Email"))
    email_entry.bind('<FocusOut>', lambda e: on_focusout(email_entry, "Email"))
    email_entry.pack(fill=X, ipady=5)

    # Password field
    password_frame = Frame(form_frame, bg="white", pady=10)
    password_frame.pack(fill=X)
    Label(password_frame, text="Password", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    password_entry = Entry(password_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                          highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    password_entry.insert(0, "Password")
    password_entry.bind('<FocusIn>', lambda e: on_entry_click(password_entry, "Password"))
    password_entry.bind('<FocusOut>', lambda e: on_focusout(password_entry, "Password"))
    password_entry.pack(fill=X, ipady=5)

    # Age field
    age_frame = Frame(form_frame, bg="white", pady=10)
    age_frame.pack(fill=X)
    Label(age_frame, text="Age", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    age_entry = Entry(age_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                     highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    age_entry.insert(0, "Age")
    age_entry.bind('<FocusIn>', lambda e: on_entry_click(age_entry, "Age"))
    age_entry.bind('<FocusOut>', lambda e: on_focusout(age_entry, "Age"))
    age_entry.pack(fill=X, ipady=5)

    # Weight field
    weight_frame = Frame(form_frame, bg="white", pady=10)
    weight_frame.pack(fill=X)
    Label(weight_frame, text="Weight (kg)", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    weight_entry = Entry(weight_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                        highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    weight_entry.insert(0, "Weight")
    weight_entry.bind('<FocusIn>', lambda e: on_entry_click(weight_entry, "Weight"))
    weight_entry.bind('<FocusOut>', lambda e: on_focusout(weight_entry, "Weight"))
    weight_entry.pack(fill=X, ipady=5)

    # Signup button
    Button(form_frame, text="Sign Up", command=signup, 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground=BUTTON_HOVER).pack(fill=X, pady=20)

    # Already have account
    login_frame = Frame(form_frame, bg="white")
    login_frame.pack()
    Label(login_frame, text="Already have an account?", font=FONT_REGULAR, bg="white", fg=TEXT_COLOR).pack(side=LEFT)
    Button(login_frame, text="Login", command=lambda: [signup_window.destroy(), open_login_page()], 
           bg="white", fg=SECONDARY_COLOR, font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground=LIGHT_GRAY).pack(side=LEFT)

    # Footer
    footer_frame = Frame(signup_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=lambda: [signup_window.destroy(), open_welcome_page()], 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)
    
    # Bind Enter key to signup
    signup_window.bind('<Return>', lambda event: signup())
    username_entry.bind('<Return>', lambda event: signup())
    email_entry.bind('<Return>', lambda event: signup())
    password_entry.bind('<Return>', lambda event: signup())
    age_entry.bind('<Return>', lambda event: signup())
    weight_entry.bind('<Return>', lambda event: signup())

# Open Login Page with modern design and OTP integration
def open_login_page():
    global current_window, login_email_entry, login_password_entry, login_otp_frame, login_otp_entry, login_btn
    close_current_window()

    login_window = Toplevel(root)
    login_window.title("Login - FitForge")
    login_window.geometry("1200x800")
    login_window.configure(bg=PRIMARY_COLOR)
    current_window = login_window

    # Header
    header_frame = Frame(login_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    Label(header_frame, text="Welcome Back", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)

    # Content
    content_frame = Frame(login_window, bg=PRIMARY_COLOR)
    content_frame.pack(fill=BOTH, expand=True, padx=150, pady=50)

    # Form frame with shadow effect
    form_frame = Frame(content_frame, bg="white", bd=0, highlightthickness=0, relief=FLAT, padx=40, pady=40)
    form_frame.pack(fill=BOTH, expand=True)
    
    # Add subtle shadow
    shadow_frame = Frame(content_frame, bg="#e0e0e0")
    shadow_frame.place(in_=form_frame, x=2, y=2, relwidth=1, relheight=1)
    form_frame.lift()

    Label(form_frame, text="Login to Your Account", font=FONT_LARGE, bg="white", fg=ACCENT_COLOR).pack(pady=(0,30))

    def on_entry_click(entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, END)
            if placeholder == "Password":
                entry.config(show="*")
    
    def on_focusout(entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            if placeholder == "Password":
                entry.config(show="")

    # Email field
    email_frame = Frame(form_frame, bg="white", pady=10)
    email_frame.pack(fill=X)
    Label(email_frame, text="Email", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    login_email_entry = Entry(email_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                            highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    login_email_entry.insert(0, "Email")
    login_email_entry.bind('<FocusIn>', lambda e: on_entry_click(login_email_entry, "Email"))
    login_email_entry.bind('<FocusOut>', lambda e: on_focusout(login_email_entry, "Email"))
    login_email_entry.pack(fill=X, ipady=5)

    # Password field
    password_frame = Frame(form_frame, bg="white", pady=10)
    password_frame.pack(fill=X)
    Label(password_frame, text="Password", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    login_password_entry = Entry(password_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                               highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    login_password_entry.insert(0, "Password")
    login_password_entry.bind('<FocusIn>', lambda e: on_entry_click(login_password_entry, "Password"))
    login_password_entry.bind('<FocusOut>', lambda e: on_focusout(login_password_entry, "Password"))
    login_password_entry.pack(fill=X, ipady=5)

    # Login button
    login_btn = Button(form_frame, text="Login", command=lambda: login(False), 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground=BUTTON_HOVER)
    login_btn.pack(fill=X, pady=20)

    # Admin login button
    Button(form_frame, text="Admin Login", command=lambda: login(True), 
           bg=ADMIN_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=10,
           activebackground="#1565C0").pack(fill=X, pady=(0, 20))

    # OTP Verification Frame (initially hidden)
    login_otp_frame = Frame(form_frame, bg="white")
    
    Label(login_otp_frame, text="Enter OTP Sent to Your Email", font=FONT_BOLD, bg="white", fg=ACCENT_COLOR).pack(anchor="w")
    
    login_otp_entry = Entry(login_otp_frame, font=FONT_REGULAR, bd=0, highlightthickness=1, 
                           highlightbackground="#cccccc", highlightcolor=SECONDARY_COLOR)
    login_otp_entry.pack(fill=X, ipady=5, pady=(5, 10))
    
    Button(login_otp_frame, text="Verify OTP", command=verify_login_otp, 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, pady=5,
           activebackground=BUTTON_HOVER).pack(fill=X)
    
    Button(login_otp_frame, text="Cancel", command=lambda: [login_otp_frame.pack_forget(), login_btn.pack()], 
           bg="white", fg=ACCENT_COLOR, font=FONT_BOLD, relief=FLAT, bd=0, pady=5,
           activebackground=LIGHT_GRAY).pack(fill=X, pady=(5, 0))

    # Don't have account
    signup_frame = Frame(form_frame, bg="white")
    signup_frame.pack()
    Label(signup_frame, text="Don't have an account?", font=FONT_REGULAR, bg="white", fg=TEXT_COLOR).pack(side=LEFT)
    Button(signup_frame, text="Sign Up", command=lambda: [login_window.destroy(), open_signup_page()], 
           bg="white", fg=SECONDARY_COLOR, font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground=LIGHT_GRAY).pack(side=LEFT)

    # Footer
    footer_frame = Frame(login_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    Button(footer_frame, text="Back", command=lambda: [login_window.destroy(), open_welcome_page()], 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=LEFT, padx=20)
    
    # Bind Enter key to login
    login_window.bind('<Return>', lambda event: login())
    login_email_entry.bind('<Return>', lambda event: login())
    login_password_entry.bind('<Return>', lambda event: login())
    login_otp_entry.bind('<Return>', lambda event: verify_login_otp())

# Welcome Page with modern design
def open_welcome_page():
    global current_window
    close_current_window()

    welcome_window = Toplevel(root)
    welcome_window.title("FitForge - Your Fitness Companion")
    welcome_window.geometry("1200x800")
    welcome_window.configure(bg=PRIMARY_COLOR)
    current_window = welcome_window

    # Header/navbar
    header_frame = Frame(welcome_window, bg=SECONDARY_COLOR, height=80)
    header_frame.pack(fill=X)
    
    Label(header_frame, text="FitForge", font=FONT_TITLE, bg=SECONDARY_COLOR, fg="white").pack(side=LEFT, padx=20, pady=15)
    
    # Navigation buttons
    nav_frame = Frame(header_frame, bg=SECONDARY_COLOR)
    nav_frame.pack(side=RIGHT, padx=20)
    
    Button(nav_frame, text="Login", command=lambda: [welcome_window.destroy(), open_login_page()], 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground=BUTTON_HOVER).pack(side=LEFT, padx=10)
    
    Button(nav_frame, text="Sign Up", command=lambda: [welcome_window.destroy(), open_signup_page()], 
           bg="white", fg=SECONDARY_COLOR, font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground=LIGHT_GRAY).pack(side=LEFT)

    # Hero section
    hero_frame = Frame(welcome_window, bg=PRIMARY_COLOR)
    hero_frame.pack(fill=BOTH, expand=True)
    
    # Left side - text content
    text_frame = Frame(hero_frame, bg=PRIMARY_COLOR, padx=80)
    text_frame.pack(side=LEFT, fill=BOTH, expand=True)
    
    Label(text_frame, text="Your Personal\nFitness Companion", font=("Segoe UI", 48, "bold"), 
          bg=PRIMARY_COLOR, fg=ACCENT_COLOR, justify=LEFT).pack(pady=(100,20), anchor="w")
    
    Label(text_frame, text="Achieve your fitness goals with personalized workout and diet plans", 
          font=FONT_SUBTITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR, justify=LEFT).pack(pady=(0,40), anchor="w")
    
    Button(text_frame, text="Get Started", command=lambda: [welcome_window.destroy(), open_login_page()], 
           bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0, padx=30, pady=15,
           activebackground=BUTTON_HOVER).pack(anchor="w")

    # Right side - placeholder for image (would be an actual image in production)
    image_frame = Frame(hero_frame, bg=LIGHT_GRAY, width=500)
    image_frame.pack(side=RIGHT, fill=BOTH, expand=True)
    
    # Try to load an actual fitness image
    try:
        # Using a placeholder fitness image URL
        image_url = "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80"
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((500, 800), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        image_label = Label(image_frame, image=photo, bg=LIGHT_GRAY)
        image_label.image = photo  # Keep a reference
        image_label.pack(expand=True)
    except Exception as e:
        print(f"Error loading image: {e}")
        Label(image_frame, text="[Fitness Image]", font=("Segoe UI", 24), bg=LIGHT_GRAY, fg="#999999").pack(expand=True)

    # Footer
    footer_frame = Frame(welcome_window, bg=ACCENT_COLOR, height=60)
    footer_frame.pack(fill=X, side=BOTTOM)
    
    Label(footer_frame, text="© 2025 FitForge. All rights reserved By Pranav.", 
          font=FONT_REGULAR, bg=ACCENT_COLOR, fg="white").pack(side=LEFT, padx=20)
    
    Button(footer_frame, text="Exit", command=exit_application, 
           bg=ACCENT_COLOR, fg="white", font=FONT_BOLD, relief=FLAT, bd=0,
           activebackground="#444444").pack(side=RIGHT, padx=20)

# Initialize database tables
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create users table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                age INT,
                weight DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create diet_charts table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_charts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                diet_type VARCHAR(255) NOT NULL,
                diet_details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create admins table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if admin exists, if not create default admin
        cursor.execute('SELECT * FROM admins WHERE email = "admin@fitforge.com"')
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO admins (username, email, password)
                VALUES ("Admin", "admin@fitforge.com", "admin123")
            ''')
        
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
    finally:
        cursor.close()
        conn.close()

# Main application start
root = Tk()
root.withdraw()  # Hide the initial window

# Set application icon (would need actual .ico file)
try:    
    root.iconbitmap("fitforge.ico")
except:
    pass

# Initialize database tables
initialize_database()

# Start with welcome page
open_welcome_page()
root.mainloop()