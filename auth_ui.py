"""Authentication UI for Chat System"""

import tkinter as tk
from tkinter import ttk, messagebox
from auth_db import AuthDB
from russian_spy_names import get_random_spy_name, generate_unique_spy_name


class AuthUI:
    """Authentication interface for login, registration, and anonymous mode."""

    def __init__(self, root, on_auth_success):
        """Initialize authentication UI.

        Args:
            root: Parent tkinter window
            on_auth_success: Callback function(username, password, is_anon) called on successful auth
        """
        self.root = root
        self.on_auth_success = on_auth_success
        self.db = AuthDB()
        self.auth_window = None

    def show_auth_screen(self):
        """Display the authentication selection screen."""
        # Create modal window
        self.auth_window = tk.Toplevel(self.root)
        self.auth_window.title("SHNet Secure Terminal - Authentication")
        self.auth_window.geometry("400x380")
        self.auth_window.resizable(False, False)
        self.auth_window.configure(bg='#1e1e1e')

        # Make it modal
        self.auth_window.transient(self.root)
        self.auth_window.grab_set()

        # Center relative to parent window
        self.auth_window.update_idletasks()
        self.root.update_idletasks()

        # Get parent window position and size
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width // 2) - (400 // 2)
        y = parent_y + (parent_height // 2) - (380 // 2)
        self.auth_window.geometry(f"400x380+{x}+{y}")

        # Header
        header_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        header_frame.pack(pady=20)

        title = tk.Label(
            header_frame,
            text="┌─[ SHNet Secure Terminal ]─┐",
            font=('Courier New', 14, 'bold'),
            fg='#50fa7b',
            bg='#1e1e1e'
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text="Authentication Required",
            font=('Courier New', 10),
            fg='#8be9fd',
            bg='#1e1e1e'
        )
        subtitle.pack(pady=5)

        # Button container
        button_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        button_frame.pack(pady=30)

        # Login button
        login_btn = tk.Button(
            button_frame,
            text="LOGIN",
            command=self.show_login_form,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#f8f8f2',
            activebackground='#6272a4',
            activeforeground='#f8f8f2',
            relief=tk.RAISED,
            bd=2,
            width=20,
            height=2
        )
        login_btn.pack(pady=8)

        # Register button
        register_btn = tk.Button(
            button_frame,
            text="REGISTER",
            command=self.show_register_form,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#f8f8f2',
            activebackground='#6272a4',
            activeforeground='#f8f8f2',
            relief=tk.RAISED,
            bd=2,
            width=20,
            height=2
        )
        register_btn.pack(pady=8)

        # Anonymous button
        anon_btn = tk.Button(
            button_frame,
            text="ANONYMOUS MODE",
            command=self.login_anonymous,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#ff5555',
            activebackground='#6272a4',
            activeforeground='#ff5555',
            relief=tk.RAISED,
            bd=2,
            width=20,
            height=2
        )
        anon_btn.pack(pady=8)

        # Footer
        footer = tk.Label(
            self.auth_window,
            text="[ Encrypted Connection Established ]",
            font=('Courier New', 8),
            fg='#6272a4',
            bg='#1e1e1e'
        )
        footer.pack(side=tk.BOTTOM, pady=10)

    def show_login_form(self):
        """Display login form."""
        # Clear current window
        for widget in self.auth_window.winfo_children():
            widget.destroy()

        # Header
        header_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        header_frame.pack(pady=20)

        title = tk.Label(
            header_frame,
            text="┌─[ LOGIN ]─┐",
            font=('Courier New', 14, 'bold'),
            fg='#50fa7b',
            bg='#1e1e1e'
        )
        title.pack()

        # Form frame
        form_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        form_frame.pack(pady=20)

        # Username
        tk.Label(
            form_frame,
            text="Username:",
            font=('Courier New', 10),
            fg='#f8f8f2',
            bg='#1e1e1e'
        ).grid(row=0, column=0, sticky='e', padx=10, pady=10)

        username_entry = tk.Entry(
            form_frame,
            font=('Courier New', 10),
            bg='#44475a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            width=25
        )
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        username_entry.focus()

        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=('Courier New', 10),
            fg='#f8f8f2',
            bg='#1e1e1e'
        ).grid(row=1, column=0, sticky='e', padx=10, pady=10)

        password_entry = tk.Entry(
            form_frame,
            font=('Courier New', 10),
            bg='#44475a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            show='*',
            width=25
        )
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Bind Enter key
        password_entry.bind('<Return>', lambda e: self.attempt_login(
            username_entry.get(), password_entry.get()
        ))

        # Buttons
        button_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        button_frame.pack(pady=20)

        login_btn = tk.Button(
            button_frame,
            text="LOGIN",
            command=lambda: self.attempt_login(
                username_entry.get(), password_entry.get()
            ),
            font=('Courier New', 10, 'bold'),
            bg='#44475a',
            fg='#50fa7b',
            activebackground='#6272a4',
            width=12
        )
        login_btn.pack(side=tk.LEFT, padx=5)

        back_btn = tk.Button(
            button_frame,
            text="BACK",
            command=self.show_auth_screen,
            font=('Courier New', 10, 'bold'),
            bg='#44475a',
            fg='#f8f8f2',
            activebackground='#6272a4',
            width=12
        )
        back_btn.pack(side=tk.LEFT, padx=5)

    def show_register_form(self):
        """Display registration form."""
        # Clear current window
        for widget in self.auth_window.winfo_children():
            widget.destroy()

        # Header
        header_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        header_frame.pack(pady=20)

        title = tk.Label(
            header_frame,
            text="┌─[ REGISTER ]─┐",
            font=('Courier New', 14, 'bold'),
            fg='#50fa7b',
            bg='#1e1e1e'
        )
        title.pack()

        # Form frame
        form_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        form_frame.pack(pady=20)

        # Username
        tk.Label(
            form_frame,
            text="Username:",
            font=('Courier New', 10),
            fg='#f8f8f2',
            bg='#1e1e1e'
        ).grid(row=0, column=0, sticky='e', padx=10, pady=10)

        username_entry = tk.Entry(
            form_frame,
            font=('Courier New', 10),
            bg='#44475a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            width=25
        )
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        username_entry.focus()

        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=('Courier New', 10),
            fg='#f8f8f2',
            bg='#1e1e1e'
        ).grid(row=1, column=0, sticky='e', padx=10, pady=10)

        password_entry = tk.Entry(
            form_frame,
            font=('Courier New', 10),
            bg='#44475a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            show='*',
            width=25
        )
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Confirm Password
        tk.Label(
            form_frame,
            text="Confirm:",
            font=('Courier New', 10),
            fg='#f8f8f2',
            bg='#1e1e1e'
        ).grid(row=2, column=0, sticky='e', padx=10, pady=10)

        confirm_entry = tk.Entry(
            form_frame,
            font=('Courier New', 10),
            bg='#44475a',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            show='*',
            width=25
        )
        confirm_entry.grid(row=2, column=1, padx=10, pady=10)

        # Bind Enter key
        confirm_entry.bind('<Return>', lambda e: self.attempt_register(
            username_entry.get(), password_entry.get(), confirm_entry.get()
        ))

        # Buttons
        button_frame = tk.Frame(self.auth_window, bg='#1e1e1e')
        button_frame.pack(pady=20)

        register_btn = tk.Button(
            button_frame,
            text="REGISTER",
            command=lambda: self.attempt_register(
                username_entry.get(), password_entry.get(), confirm_entry.get()
            ),
            font=('Courier New', 10, 'bold'),
            bg='#44475a',
            fg='#50fa7b',
            activebackground='#6272a4',
            width=12
        )
        register_btn.pack(side=tk.LEFT, padx=5)

        back_btn = tk.Button(
            button_frame,
            text="BACK",
            command=self.show_auth_screen,
            font=('Courier New', 10, 'bold'),
            bg='#44475a',
            fg='#f8f8f2',
            activebackground='#6272a4',
            width=12
        )
        back_btn.pack(side=tk.LEFT, padx=5)

    def attempt_login(self, username, password):
        """Attempt to log in with provided credentials."""
        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return

        if self.db.authenticate_user(username, password):
            self.auth_window.destroy()
            self.on_auth_success(username, password, False)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def attempt_register(self, username, password, confirm):
        """Attempt to register a new user."""
        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields required")
            return

        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        success, message = self.db.register_user(username, password, is_anon=False)

        if success:
            # Auto-login after successful registration
            self.auth_window.destroy()
            self.on_auth_success(username, password, False)
        else:
            messagebox.showerror("Registration Failed", message)

    def login_anonymous(self):
        """Log in anonymously with a random Russian spy name."""
        # Generate unique spy name
        spy_name = get_random_spy_name()

        # Register as anonymous user (no password required)
        success, message = self.db.register_user(spy_name, "", is_anon=True)

        # If name taken, try generating another
        attempts = 0
        while not success and attempts < 10:
            spy_name = get_random_spy_name()
            success, message = self.db.register_user(spy_name, "", is_anon=True)
            attempts += 1

        if success:
            self.auth_window.destroy()
            self.on_auth_success(spy_name, "", True)  # Empty password for anon users
        else:
            messagebox.showerror("Error", "Could not generate anonymous identity. Please try again.")
