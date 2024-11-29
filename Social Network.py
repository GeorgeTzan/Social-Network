import tkinter as tk
from tkinter import messagebox

class SocialNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Network - Georgios Tzanopoulos")
        self.users = {}
        self.connections = {}

        self.create_widgets()

    def create_widgets(self):
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        user_frame = tk.Frame(self.root)
        user_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(user_frame, text="User Management", font=("Arial", 12, "bold")).pack()
        tk.Button(user_frame, text="Add User", command=self.add_user_window).pack(fill=tk.X)
        tk.Button(user_frame, text="Remove User", command=self.remove_user_window).pack(fill=tk.X)
        tk.Button(user_frame, text="View Connections", command=self.view_connections).pack(fill=tk.X)


        connection_frame = tk.Frame(self.root)
        connection_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(connection_frame, text="Connection Management", font=("Arial", 12, "bold")).pack()
        tk.Button(connection_frame, text="Create Connection", command=self.create_connection_window).pack(fill=tk.X)
        tk.Button(connection_frame, text="Update Connection Weight", command=self.update_connection_weight_window).pack(fill=tk.X)

        network_analysis_frame = tk.Frame(self.root)
        network_analysis_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        tk.Label(network_analysis_frame, text="Network Analysis", font=("Arial", 12, "bold")).pack()


    # Placeholder methods
    def add_user_window(self):
        messagebox.showinfo("Add User", "Functionality not implemented yet.")

    def remove_user_window(self):
        messagebox.showinfo("Remove User", "Functionality not implemented yet.")

    def view_connections(self):
        messagebox.showinfo("View Connections", "Functionality not implemented yet.")

    def create_connection_window(self):
        messagebox.showinfo("Create Connection", "Functionality not implemented yet.")

    def update_connection_weight_window(self):
        messagebox.showinfo("Update Connection Weight", "Functionality not implemented yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
