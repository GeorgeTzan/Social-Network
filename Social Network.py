import tkinter as tk
from tkinter import messagebox
from pyvis.network import Network
import os
import social_network
import datetime
import webview
from faker import Faker
import random

os.environ["PYWEBVIEW_GUI"] = "qt"
network_cpp = social_network.SocialNetwork()


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
        self.root.rowconfigure(2, weight=1)

        user_frame = tk.Frame(self.root)
        user_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(user_frame, text="User Management", font=("Arial", 12, "bold")).pack()
        tk.Button(user_frame, text="Add User", command=self.add_user_window).pack(
            fill=tk.X
        )
        tk.Button(user_frame, text="Remove User", command=self.remove_user_window).pack(
            fill=tk.X
        )
        tk.Button(
            user_frame, text="View Connections", command=self.view_connections_window
        ).pack(fill=tk.X)

        connection_frame = tk.Frame(self.root)
        connection_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(
            connection_frame, text="Connection Management", font=("Arial", 12, "bold")
        ).pack()
        tk.Button(
            connection_frame,
            text="Create Connection",
            command=self.create_connection_window,
        ).pack(fill=tk.X)
        tk.Button(
            connection_frame,
            text="Update Connection Weight",
            command=self.update_connection_weight_window,
        ).pack(fill=tk.X)
        tk.Button(
            connection_frame, text="Save Network", command=self.save_network
        ).pack(fill=tk.X)
        tk.Button(
            connection_frame, text="Load Network", command=self.load_network
        ).pack(fill=tk.X)

        network_analysis_frame = tk.Frame(self.root)
        network_analysis_frame.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        tk.Label(
            network_analysis_frame, text="Network Analysis", font=("Arial", 12, "bold")
        ).pack()
        tk.Button(
            network_analysis_frame,
            text="Generate Random Network",
            command=self.generate_random_network_window,
        ).pack(fill=tk.X)
        tk.Button(
            network_analysis_frame,
            text="Live Network",
            command=self.update_visualization,
        ).pack(fill=tk.X)
        tk.Button(
            network_analysis_frame,
            text="Friend Recommendations",
            command=self.recommend_friends_window,
        ).pack(fill=tk.X)
        tk.Button(
            network_analysis_frame,
            text="Detect Communities",
            command=self.detect_communities_window,
        ).pack(fill=tk.X)
        tk.Button(
            network_analysis_frame,
            text="Shortest Path",
            command=self.shortest_path_window,
        ).pack(fill=tk.X)

    def add_user_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add new user")

        tk.Label(window, text="User ID:").pack()
        user_id_entry = tk.Entry(window)
        user_id_entry.pack()

        tk.Label(window, text="Name (optional):").pack()
        name_entry = tk.Entry(window)
        name_entry.pack()

        tk.Label(window, text="Interests (Separate by using ;):").pack()
        interests_entry = tk.Entry(window)
        interests_entry.pack()

        tk.Button(
            window,
            text="Add User",
            command=lambda: self.add_user(
                user_id_entry, name_entry, interests_entry, window
            ),
        ).pack()

    def add_user(self, user_id_entry, name_entry, interests_entry, window=None):
        try:
            user_id = user_id_entry.get()
            name = name_entry.get()
            interests = interests_entry.get()
        except:
            user_id = user_id_entry
            name = name_entry
            interests = interests_entry
        if user_id and not (user_id in self.users):
            network_cpp.add_user(user_id, name, interests)
            self.users[user_id] = {
                "name": name,
                "interests": interests,
                "connections": {},
            }
            if window != None:
                messagebox.showinfo("Add User", f"User {user_id} added successfully.")
                window.destroy()
        else:
            if window != None:
                messagebox.showerror("Error", "User ID is required or already exists.")
        self.update_visualization(run_window=False)

    def remove_user_window(self):
        window = tk.Toplevel(self.root)
        window.title("Remove a user")

        tk.Label(window, text="User ID:").pack()
        user_id_entry = tk.Entry(window)
        user_id_entry.pack()

        tk.Button(
            window,
            text="Remove User",
            command=lambda: self.remove_user(user_id_entry.get(), window),
        ).pack()

    def remove_user(self, user_id, window):
        if user_id not in self.users:
            messagebox.showerror("Error", "User ID does not exist!")
            return

        del self.users[user_id]

        for connection in list(self.connections):
            if user_id in connection:
                del self.connections[connection]

        for other_user in self.users:
            if user_id in self.users[other_user]["connections"]:
                del self.users[other_user]["connections"][user_id]
        network_cpp.remove_user(user_id)
        self.update_visualization(run_window=False)
        messagebox.showinfo(
            "Success!", f"User {user_id} has been deleted successfully!"
        )
        window.destroy()

    def view_connections_window(self):
        window = tk.Toplevel(self.root)
        window.title("View Connection")

        tk.Label(window, text="User ID:").pack()
        user_entry = tk.Entry(window)
        user_entry.pack()

        tk.Button(
            window,
            text="View connection",
            command=lambda: self.view_connections(user_entry.get(), window),
        ).pack()

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
        user2_entry = tk.Entry(window)
        user2_entry.pack()

        tk.Label(window, text="Connection Weight (0.01 - 1):").pack()
        weight_entry = tk.Entry(window)
        weight_entry.pack()

        tk.Button(
            window,
            text="Create connection",
            command=lambda: self.create_connection(
                user1_entry.get(), user2_entry.get(), weight_entry.get(), window
            ),
        ).pack()

    def create_connection(self, user1, user2, weight, window=None):
        if not all(user in self.users for user in [user1, user2]):
            if window != None:
                messagebox.showerror("Error", "One or Both users do not exist!")
                window.destroy()
            return
        if user1 == user2:
            if window != None:
                messagebox.showerror("Error", "Can't connect with yourself!")
                window.destroy()
            return

        try:
            weight = float(weight)
            if not (0.01 <= weight <= 1):
                raise ValueError
        except ValueError:
            if window != None:
                messagebox.showerror("Error", "Weight must be in between 0.01 and 1!")
            return

        self.connections[(user1, user2)] = weight
        date = datetime.date.today().isoformat()
        self.users[user1]["connections"][user2] = date
        self.users[user2]["connections"][user1] = date

        network_cpp.add_connection(user1, user2, weight)
        if window != None:
            messagebox.showinfo(
                "Success!", f"Connection between {user1} and {user2} has been made!"
            )
            window.destroy()
        self.update_visualization(run_window=False)

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

        files = sorted(files, key=lambda x: int(x[4:6]))

        load_path = os.path.join(self.save_folder, files[-1])
        with open(load_path, "r") as file:
            data = file.readlines()
            self.users = eval(data[0].split("=", 1)[1])
            self.connections = eval(data[1].split("=", 1)[1])

        network_cpp.clear_network()
        for user_id, user_data in self.users.items():
            name = user_data.get("name", "")
            interests = user_data.get("interests", "")
            network_cpp.add_user(user_id, name, interests)
        for (user1, user2), weight in self.connections.items():
            network_cpp.add_connection(user1, user2, weight)
        self.update_visualization(run_window=False)
        messagebox.showinfo("Load Network", f"Network loaded from {load_path}.")

    def generate_random_network_window(self):
        window = tk.Toplevel(self.root)
        window.title("Generate a random network")

        generate_label = tk.Label(window, text="Choose network size generation:").pack()
        numbers_scale = tk.Scale(window, from_=1, to=1000, orient=tk.HORIZONTAL)

        numbers_scale.pack()

        tk.Button(
            window,
            text="Generate Network",
            command=lambda: self.generate_random_network(numbers_scale.get(), window),
        ).pack()

    def generate_random_network(self, size, window):
        self.users = {}
        self.connections = {}
        fake = Faker()
        for i in range(size):
            user_id = str(i)
            name = fake.name()
            if "." in name[0]:
                name = name.split()[1]
            else:
                name = name.split()[0]

            self.add_user(user_id, name, "")

        existing_connections = set()
        for _ in range(int(size)):
            while True:
                user_id_f = str(random.randint(0, size - 1))
                user_id_s = str(random.randint(0, size - 1))
                if (
                    user_id_f != user_id_s
                    and (user_id_f, user_id_s) not in existing_connections
                    and (user_id_s, user_id_f) not in existing_connections
                ):
                    weight = round(random.uniform(0.01, 1.0), 2)
                    self.create_connection(user_id_f, user_id_s, weight, window=None)
                    existing_connections.add((user_id_f, user_id_s))
                    break

    def update_connection_weight(self, user1, user2, new_weight, window):
        if user1 not in self.users or user2 not in self.users:
            messagebox.showerror("Error", "One or Both users do not exist!")
            window.destroy()
            return
        if user1 not in self.users[user2]["connections"]:
            messagebox.showerror("Error", "Users do not share a connection!")
            window.destroy()
            return
        try:
            new_weight = float(new_weight.get())
            if not (0.01 <= new_weight <= 1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Weight must be in between 0.01 and 1!")
            return
        self.connections[(user1, user2)] = new_weight
        messagebox.showinfo(
            "Success!", f"Connection between {user1} and {user2} has been updated!"
        )
        self.update_visualization(run_window=False)
        window.destroy()

    def update_connection_weight_window(self):
        window = tk.Toplevel(self.root)
        window.title("Update Connection Weight")

        tk.Label(window, text="User 1 ID:").pack()
        user1_entry = tk.Entry(window)
        user1_entry.pack()

        tk.Label(window, text="User 2 ID:").pack()
        user2_entry = tk.Entry(window)
        user2_entry.pack()

        tk.Label(window, text="Connection Weight (0.01 - 1):").pack()
        new_weight_entry = tk.Entry(window)
        new_weight_entry.pack()

        tk.Button(
            window,
            text="Update weight",
            command=lambda: self.update_connection_weight(
                user1_entry.get(), user2_entry.get(), new_weight_entry, window
            ),
        ).pack()

    def recommend_friends_window(self):
        window = tk.Toplevel(self.root)
        window.title("Friend recommendations")

        tk.Label(window, text="User ID:").pack()
        user_entry = tk.Entry(window)
        user_entry.pack()

        def recommend_friends():
            user_id = user_entry.get()
            if user_id not in self.users:
                messagebox.showerror("Error", "User ID does not exist!")
                window.destroy()
                return

            recommendations = network_cpp.recommend_friends(user_id)
            if not recommendations:
                messagebox.showerror("Recommendations", "No friends found!")
                window.destroy()
                return
            else:
                message = "\n".join(recommendations)
                messagebox.showinfo("Recommendations", message)

        tk.Button(window, text="Get Recommendations", command=recommend_friends).pack()

    def detect_communities_window(self):
        window = tk.Toplevel(self.root)
        window.title("Detect Communities")

        tk.Label(window, text="Threshold: 0.01 - 1:").pack()
        threshold_entry = tk.Entry(window)
        threshold_entry.pack()

        def community_detection():
            try:
                threshold = float(threshold_entry.get())
                if not (0.01 <= threshold <= 1):
                    raise ValueError
                communities = network_cpp.detect_communities(threshold)
                if not communities:
                    messagebox.showinfo("Communities", "No communities found!")
                else:
                    communities_message = "\n\n".join(
                        [
                            f"Community {i+1}: " + ", ".join(community)
                            for i, community in enumerate(communities)
                        ]
                    )
                    messagebox.showinfo("Communities", communities_message)
            except ValueError:
                messagebox.showerror("Error", "Threshold must be between 0.01 and 1.")
                window.destroy()

        tk.Button(window, text="Detect Communities", command=community_detection).pack()

    def shortest_path_window(self):
        window = tk.Toplevel(self.root)
        window.title("Shortest Path")

        tk.Label(window, text="Start User ID:").pack()
        start_entry = tk.Entry(window)
        start_entry.pack()

        tk.Label(window, text="End User ID:").pack()
        end_entry = tk.Entry(window)
        end_entry.pack()

        def shortest_path():
            start = start_entry.get()
            end = end_entry.get()

            if start not in self.users or end not in self.users:
                messagebox.showerror("Error", "Both Users must exist!")
                return
            path = network_cpp.dijkstra(start, end)
            if not path:
                messagebox.showinfo("Shortest path", "No path found!")
            else:
                path_message = " ->".join(path)
                messagebox.showinfo("Shortest Path", f"Shortest path: {path_message}")
                self.update_visualization(shortestpath=path)

        tk.Button(window, text="Find shortest path", command=shortest_path).pack()

    def update_visualization(self, run_window=True, shortestpath=None):
        net = Network(notebook=True, cdn_resources="in_line")
        net.nodes = []
        net.edges = []

        for user_id in self.users:
            user_data = self.users[user_id]
            net.add_node(user_id, label=user_data["name"] + f"({user_id})")
        for (user1, user2), weight in self.connections.items():
            net.add_edge(user1, user2, value=weight)
        if shortestpath:
            for i in range(len(shortestpath) - 1):
                start_node = shortestpath[i]
                end_node = shortestpath[i + 1]
                for edge in net.get_edges():
                    if (edge["from"] == start_node and edge["to"] == end_node) or (
                        edge["from"] == end_node and edge["to"] == start_node
                    ):
                        edge["color"] = "red"
                        edge["width"] = 2
        net.show("temp_network.html")
        self.add_overlay_info("temp_network.html")
        if run_window:

            current_path = os.getcwd()
            file_path = os.path.join(current_path, "temp_network.html")

            webview.create_window("Social Network Visualization", file_path)
            webview.start()

    def add_overlay_info(self, html_file):
        total_nodes = len(self.users)
        total_edges = len(self.connections)

        overlay_html = f"""
        <div style="position: absolute; top: 10px; left: 10px; background-color: rgba(255, 255, 255, 0.8); padding: 10px; border: 1px solid black; z-index: 1000;">
            <p>Total Nodes: {total_nodes}</p>
            <p>Total Edges: {total_edges}</p>
        </div>
        """

        with open(html_file, "r") as file:
            content = file.read()

        content = content.replace("<body>", f"<body>{overlay_html}")

        with open(html_file, "w") as file:
            file.write(content)


if __name__ == "__main__":
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
