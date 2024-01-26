import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
from instaloader import Instaloader, Profile
import threading
from PIL import Image, ImageTk
import requests
import io

def toggle_password_visibility():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")

def download_posts():
    # Retrieve username, password, and profile name from the input fields
    username = username_entry.get()
    password = password_entry.get()
    profile_name = profile_entry.get()

    # Check if any field is empty
    if not username or not password or not profile_name:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    # Disable download button while downloading
    download_button.config(state=tk.DISABLED)

    L = Instaloader()
    try:
        L.login(username, password)
    except Exception as e:
        messagebox.showerror("Login Error", f"Error: {e}")
        download_button.config(state=tk.NORMAL)  # Re-enable download button
        return

    try:
        profile = Profile.from_username(L.context, profile_name)
    except Exception as e:
        messagebox.showerror("Profile Error", f"Error: {e}")
        download_button.config(state=tk.NORMAL)  # Re-enable download button
        return

    progress_bar['value'] = 0
    progress_bar['maximum'] = len(list(profile.get_posts()))

    def download_post_without_comments(post):
        L.download_post(post, target=profile.username)
        progress_bar.step(1)
        root.update_idletasks()

    def download_thread():
        # Feedback to the user
        download_status.config(text="Downloading...")

        for post in profile.get_posts():
            download_post_without_comments(post)

        # Feedback to the user
        download_status.config(text="Download Complete")
        messagebox.showinfo("Download Complete", "Posts downloaded successfully.")
        download_button.config(state=tk.NORMAL)  # Re-enable download button
        progress_bar['value'] = 0

    # Create a new thread for downloading
    download_thread = threading.Thread(target=download_thread)
    download_thread.start()

def preview_post(post):
    img_bytes = requests.get(post.url).content
    img = Image.open(io.BytesIO(img_bytes))
    img.thumbnail((200, 200))  # Resize image for preview
    return ImageTk.PhotoImage(img)

def display_posts():
    # Retrieve username, password, and profile name from the input fields
    username = username_entry.get()
    password = password_entry.get()
    profile_name = profile_entry.get()

    # Check if any field is empty
    if not username or not password or not profile_name:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    L = Instaloader()
    try:
        L.login(username, password)
    except Exception as e:
        messagebox.showerror("Login Error", f"Error: {e}")
        return

    try:
        profile = Profile.from_username(L.context, profile_name)
    except Exception as e:
        messagebox.showerror("Profile Error", f"Error: {e}")
        return

    # Clear previous previews
    for widget in preview_frame.winfo_children():
        widget.destroy()

    # Create a canvas inside the scrollable frame
    canvas = tk.Canvas(preview_frame, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create a frame inside the canvas to hold the previews
    inner_frame = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Load and store preview images
    preview_images = []
    for post in profile.get_posts():
        img = preview_post(post)
        preview_images.append(img)

    # Display preview images in a grid inside the inner frame
    for i, img in enumerate(preview_images):
        row = i // 3
        col = i % 3
        label = tk.Label(inner_frame, image=img)
        label.grid(row=row, column=col, padx=5, pady=5)
        # Keep a reference to the image to prevent garbage collection
        label.image = img

    # Update the canvas scroll region
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Create the main window
root = tk.Tk()
root.title("Instagram Media Downloader")

# Frame for inputs
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10, anchor="w")

# Instagram Username
tk.Label(input_frame, text="Instagram Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
username_entry = tk.Entry(input_frame)
username_entry.grid(row=0, column=1, padx=5, pady=5)

# Instagram Password
tk.Label(input_frame, text="Instagram Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
password_entry = tk.Entry(input_frame, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

# Show Password Checkbox
show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(input_frame, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
show_password_checkbox.grid(row=1, column=2, padx=5, pady=5)

# Profile Name
tk.Label(input_frame, text="Profile Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
profile_entry = tk.Entry(input_frame)
profile_entry.grid(row=2, column=1, padx=5, pady=5)

# Display and Download button
display_download_frame = tk.Frame(root)
display_download_frame.pack(padx=10, pady=10)

display_button = tk.Button(display_download_frame, text="Display Posts", command=display_posts)
display_button.grid(row=0, column=0, padx=5, pady=5)

download_button = tk.Button(display_download_frame, text="Download Posts", command=download_posts)
download_button.grid(row=0, column=1, padx=5, pady=5)

# Frame for previews (scrollable)
preview_frame = tk.Frame(root)
preview_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Progress bar
progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)

# Download status label
download_status = tk.Label(root, text="", fg="green")
download_status.pack()

# Run the GUI
root.mainloop()
