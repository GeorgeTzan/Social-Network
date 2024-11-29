import tkinter as tk
from tkinter import messagebox
import os
import random
import datetime

class SocialNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Network - Georgios Tzanopoulos")
        self.save_folder = "Savedata"
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)
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
        tk.Button(user_frame, text="View Connections", command=self.view_connections_window).pack(fill=tk.X)


        connection_frame = tk.Frame(self.root)
        connection_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(connection_frame, text="Connection Management", font=("Arial", 12, "bold")).pack()
        tk.Button(connection_frame, text="Create Connection", command=self.create_connection_window).pack(fill=tk.X)
        tk.Button(connection_frame, text="Update Connection Weight", command=self.update_connection_weight_window).pack(fill=tk.X)
        tk.Button(connection_frame, text="Save Network", command=self.save_network).pack(fill=tk.X)
        tk.Button(connection_frame, text="Load Network", command=self.load_network).pack(fill=tk.X)

        network_analysis_frame = tk.Frame(self.root)
        network_analysis_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        tk.Label(network_analysis_frame, text="Network Analysis", font=("Arial", 12, "bold")).pack()
        tk.Button(network_analysis_frame, text="Generate Random Network", command=self.generate_random_network_window).pack(fill=tk.X)

        coming_soon_frame = tk.Frame(self.root)
        coming_soon_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        tk.Label(coming_soon_frame, text="Coming Soon (TDL)", font=("Arial", 14, "bold")).pack()

    def add_user_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add new user")

        tk.Label(window, text="User ID:").pack()
        user_id_entry = tk.Entry(window)
        user_id_entry.pack()

        tk.Label(window, text="Name (optional):").pack()
        name_entry = tk.Entry(window)
        name_entry.pack()

        tk.Label(window, text="Interests(Seperate by using ;):").pack()
        interests_entry = tk.Entry(window)
        interests_entry.pack()


        def add_user():
            user_id = user_id_entry.get()
            name = name_entry.get()
            interests = interests_entry.get()
            if user_id and not(user_id in self.users):
                self.users[user_id] = {'name': name, 'interests': interests, 'connections': {}}
                messagebox.showinfo("Add User", f"User {user_id} added successfully.")
                window.destroy()
            else:
                messagebox.showerror("Error", "User ID is required or already exists.")

        tk.Button(window, text="Add User", command=add_user).pack()
    def remove_user_window(self):
        window = tk.Toplevel(self.root)
        window.title("Remove a user")

        tk.Label(window, text="USer ID:").pack()
        user_id_entry = tk.Entry(window)
        user_id_entry.pack()

        tk.Button(window,text="Remove User", command=lambda: self.remove_user(user_id_entry.get(), window)).pack()

    def remove_user(self, user_id, window):
        if user_id not in self.users:
            messagebox.showerror("Error", "User ID does not exist!")
            return
        del self.users[user_id]
        messagebox.showinfo("Success!", f"User {user_id} has been deleted successfully!")
        window.destroy()

    def view_connections_window(self):
        window = tk.Toplevel(self.root)
        window.title("View Connection")

        tk.Label(window, text="User ID:").pack()
        user_entry = tk.Entry(window)
        user_entry.pack()

        tk.Button(window,text="View connection", command=lambda: self.view_connections(user_entry.get(), window)).pack()


    def view_connections(self, user_id, window):
        if user_id not in self.users:
            messagebox.showerror("Error", "User ID does not exist!")
            return
        connections = self.users[user_id]["connections"]
        message = "\n".join(f"{uid}: {date}" for uid, date in connections.items())
        messagebox.showinfo("Connections", message or "No connections found.")
        window.destroy()


    def create_connection_window(self):
        window = tk.Toplevel(self.root)
        window.title("Create Connection")

        tk.Label(window, text="User 1 ID:").pack()
        user1_entry = tk.Entry(window)
        user1_entry.pack()

        tk.Label(window, text="User 2 ID:").pack()
        user2_entry= tk.Entry(window)
        user2_entry.pack()

        tk.Label(window, text="Connection Weight (0.01 - 1):").pack()
        weight_entry = tk.Entry(window)
        weight_entry.pack()

        tk.Button(window,text="Create connection", command=lambda: self.create_connection(user1_entry.get(), user2_entry.get(), weight_entry.get(), window)).pack()

    def create_connection(self, user1, user2, weight, window):
        print(self.users)
        if user1 not in self.users or user2 not in self.users:
            messagebox.showerror("Error", "One or Both users do not exist!")
            return
        if user1 == user2:
            messagebox.showerror("Error", "Can't connect with yourself!")
            return

        try:
            weight = float(weight)
            if not(0.01 <= weight <= 1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Weight must be in between 0.01 and 1!")
        self.connections[(user1, user2)] = weight
        date = datetime.date.today().isoformat()
        self.users[user1]['connections'][user2] = date
        self.users[user2]['connections'][user1] = date
        messagebox.showinfo("Success!", f"Connection between {user1} and {user2} has been made!")
        window.destroy()

    def save_network(self):
        files = [f for f in os.listdir(self.save_folder) if f.endswith(".xyz")]
        next_file = f"save{len(files):02}.xyz"
        save_path = os.path.join(self.save_folder, next_file)

        with open(save_path, "w") as file:
            file.write(f"Users={self.users}\n")
            file.write(f"Connections={self.connections}\n")
        messagebox.showinfo("Save Network", f"Network saved to {save_path}.")

    def load_network(self):
        files = [f for f in os.listdir(self.save_folder) if f.endswith(".xyz")]
        if not files:
            messagebox.showerror("Load Network", "No saved networks found.")
            return

        load_path = os.path.join(self.save_folder, files[-1])
        with open(load_path, "r") as file:
            data = file.readlines()
            self.users = eval(data[0].split("=", 1)[1])
            self.connections = eval(data[1].split("=", 1)[1])
        messagebox.showinfo("Load Network", f"Network loaded from {load_path}.")

    def generate_random_network_window(self):
        pass

    def update_connection_weight(self, user1, user2, new_weight, window):
        if user1 not in self.users or user2 not in self.users:
            messagebox.showerror("Error", "One or Both users do not exist!")
            return
        try:
            new_weight = float(new_weight)
            if not(0.01 <= new_weight <= 1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Weight must be in between 0.01 and 1!")
        self.connections[(user1, user2)] = new_weight
        messagebox.showinfo("Success!", f"Connection between {user1} and {user2} has been updated!")
        window.destroy()

    def update_connection_weight_window(self):
        window = tk.Toplevel(self.root)
        window.title("Update Connection Weight")

        tk.Label(window, text="User 1 ID:").pack()
        user1_entry = tk.Entry(window)
        user1_entry.pack()

        tk.Label(window, text="User 2 ID:").pack()
        user2_entry= tk.Entry(window)
        user2_entry.pack()

        tk.Label(window, text="Connection Weight (0.01 - 1):").pack()
        new_weight_entry = tk.Entry(window)
        new_weight_entry.pack()

        tk.Button(window,text="Update weight", command=lambda: self.update_connection_weight(user1_entry.get(), user2_entry.get(), new_weight_entry, window)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
