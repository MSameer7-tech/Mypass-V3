import customtkinter as ctk
from PIL import Image
try:
    img = ctk.CTkImage(Image.open("assets/icons/add.svg"))
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
