import wx
from pyvis.network import Network
import wx.html2
import os
import social_network
import datetime
from faker import Faker
from wx.lib.newevent import NewEvent
import time
import random
import threading


network_cpp = social_network.SocialNetwork()
UpdateWebViewEvent, EVT_UPDATE_WEBVIEW = NewEvent()


class ShadowPanel(wx.Panel):
    def __init__(self, parent, pos, size, color=(0, 0, 0, 128)):
        super().__init__(parent, pos=pos, size=size, style=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.Colour(*color))
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 50)))
        dc.DrawRectangle(0, 0, self.GetSize().x, self.GetSize().y)


class SocialNetworkApp(wx.Frame):
    def __init__(self, parent, title):
        super(SocialNetworkApp, self).__init__(
            parent,
            title=title,
            size=(800, 600),
            style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER,
        )
        self.save_folder = "Savedata"
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)

        self.users = {}
        self.connections = {}

        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_panel.SetBackgroundColour(wx.Colour(75, 0, 130))
        self.panel_with_content = wx.Panel(self.main_panel)
        self.panel_with_content.SetBackgroundColour(wx.Colour(75, 0, 130))
        self.main_sizer.Add(self.panel_with_content, 1, wx.EXPAND | wx.ALL, 10)
        self.panel_with_content.Bind(wx.EVT_PAINT, self.web_paint)

        self.panel_with_content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_with_content.SetSizer(self.panel_with_content_sizer)

        ShadowPanel(
            self.panel_with_content, pos=(50, 50), size=(300, 220), color=(0, 0, 0, 100)
        )
        ShadowPanel(
            self.panel_with_content,
            pos=(450, 50),
            size=(300, 220),
            color=(0, 0, 0, 100),
        )
        ShadowPanel(
            self.panel_with_content,
            pos=(50, 300),
            size=(300, 220),
            color=(0, 0, 0, 100),
        )

        self.webview = wx.html2.WebView.New(
            self.panel_with_content, pos=(450, 290), size=(300, 240)
        )
        self.main_panel.SetSizer(self.main_sizer)
        self.Bind(EVT_UPDATE_WEBVIEW, self.on_update_webview)
        self.create_widgets()
        self.update_visualization()
        self.Show()

    def create_widgets(self):
        panel = self.main_panel

        add_user_btn = wx.Button(panel, label="Add User", pos=(80, 100))
        add_user_btn.Bind(wx.EVT_BUTTON, self.add_user_window)

        remove_user_btn = wx.Button(panel, label="Remove User", pos=(200, 100))
        remove_user_btn.Bind(wx.EVT_BUTTON, self.remove_user_window)

        view_connections_btn = wx.Button(
            panel, label="View Connections", pos=(120, 150)
        )
        view_connections_btn.Bind(wx.EVT_BUTTON, self.view_connections_window)

        user_managment_label = wx.StaticText(
            panel, label="User Managment", pos=(130, 30)
        )

        user_managment_label.SetForegroundColour("white")
        user_managment_label.SetBackgroundColour(wx.Colour(0, 0, 0, 150))

        connection_managment_label = wx.StaticText(
            panel, label="Connection Managment", pos=(520, 30)
        )
        connection_managment_label.SetForegroundColour("white")
        connection_managment_label.SetBackgroundColour(wx.Colour(0, 0, 0, 150))

        network_managment_label = wx.StaticText(
            panel, label="Network Managment", pos=(128, 280)
        )
        network_managment_label.SetForegroundColour("white")
        network_managment_label.SetBackgroundColour(wx.Colour(0, 0, 0, 150))

        network_analysis_label = wx.StaticText(
            panel, label="Network Analysis", pos=(520, 280)
        )
        network_analysis_label.SetForegroundColour("white")
        network_analysis_label.SetBackgroundColour(wx.Colour(0, 0, 0, 150))

        connection_sizer = wx.BoxSizer(wx.HORIZONTAL)
        create_connection_btn = wx.Button(
            panel, label="Create Connection", pos=(520, 150)
        )
        create_connection_btn.Bind(wx.EVT_BUTTON, self.create_connection_window)
        connection_sizer.Add(create_connection_btn, 0, wx.ALL, 5)

        update_connection_btn = wx.Button(
            panel, label="Update Connection", pos=(520, 190)
        )
        update_connection_btn.Bind(wx.EVT_BUTTON, self.update_connection_weight_window)
        connection_sizer.Add(update_connection_btn, 0, wx.ALL, 5)

        save_network_btn = wx.Button(panel, label="Save", pos=(500, 100))
        save_network_btn.Bind(wx.EVT_BUTTON, self.save_network)
        connection_sizer.Add(save_network_btn, 0, wx.ALL, 5)

        load_network_btn = wx.Button(panel, label="Load", pos=(610, 100))
        load_network_btn.Bind(wx.EVT_BUTTON, self.load_network)
        connection_sizer.Add(load_network_btn, 0, wx.ALL, 5)

        random_network_btn = wx.Button(
            panel, label="Generate Random Network", pos=(90, 320)
        )
        random_network_btn.Bind(wx.EVT_BUTTON, self.generate_random_network_window)

        visualize_btn = wx.Button(panel, label="Visualize Network", pos=(90, 360))
        visualize_btn.Bind(wx.EVT_BUTTON, lambda evt: self.update_visualization())

        friend_req_btn = wx.Button(panel, label="Friends Recommendation", pos=(90, 400))
        friend_req_btn.Bind(wx.EVT_BUTTON, self.recommend_friends_window)

        detect_comm_btn = wx.Button(panel, label="Detect Communities", pos=(90, 440))
        detect_comm_btn.Bind(wx.EVT_BUTTON, self.detect_communities_window)

        short_path_btn = wx.Button(panel, label="Find shortest Path", pos=(90, 480))
        short_path_btn.Bind(wx.EVT_BUTTON, self.shortest_path_window)

    def web_paint(self, event):
        dc = wx.PaintDC(self.panel_with_content)
        gc = wx.GraphicsContext.Create(dc)

        gc.SetPen(wx.Pen(wx.Colour(230, 230, 250), width=1))

        width, height = self.panel_with_content.GetSize()
        num_lines = 500

        for _ in range(num_lines):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            gc.StrokeLine(x1, y1, x2, y2)

    def add_user_window(self, event):
        window = wx.Dialog(self, title="Add User", size=(400, 300))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user_id_label = wx.StaticText(window, label="User ID:")
        sizer.Add(user_id_label, 0, wx.ALL, 5)
        user_id_entry = wx.TextCtrl(window)
        sizer.Add(user_id_entry, 0, wx.EXPAND | wx.ALL, 5)

        name_Label = wx.StaticText(window, label="Name (optional):")
        sizer.Add(name_Label, 0, wx.ALL, 5)
        name_entry = wx.TextCtrl(window)
        sizer.Add(name_entry, 0, wx.EXPAND | wx.ALL, 5)

        interests_Label = wx.StaticText(
            window, label="Interests (Separate by using ;):"
        )
        sizer.Add(interests_Label, 0, wx.ALL, 5)
        interests_entry = wx.TextCtrl(window)
        sizer.Add(interests_entry, 0, wx.EXPAND | wx.ALL, 5)

        add_usr_button = wx.Button(window, label="Add user")
        add_usr_button.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.add_user(
                user_id_entry, name_entry, interests_entry, window
            ),
        )

        sizer.Add(add_usr_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        window.SetSizer(sizer)
        window.ShowModal()

    def add_user(self, user_id_entry, name_entry, interests_entry, window=None):
        try:
            user_id = user_id_entry.GetValue().strip()
            name = name_entry.GetValue().strip()
            interests = interests_entry.GetValue().strip()
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
                wx.MessageBox(f"User {user_id} added successfully.", "Success")
                window.Destroy()
        else:
            if window != None:
                wx.MessageBox("User ID is required or already exists.", "Error")
        self.update_visualization()

    def remove_user_window(self, event):
        window = wx.Dialog(self, title="Remove User", size=(220, 150))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user_id_label = wx.StaticText(window, label="User ID:")
        sizer.Add(user_id_label, 0, wx.ALL, 5)
        user_id_entry = wx.TextCtrl(window)
        sizer.Add(user_id_entry, 0, wx.EXPAND | wx.ALL, 5)
        remove_usr_button = wx.Button(window, label="Remove user")
        remove_usr_button.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.remove_user(user_id_entry.GetValue().strip(), window),
        )

        sizer.Add(remove_usr_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def remove_user(self, user_id, window):
        if user_id not in self.users:
            wx.MessageBox("Error", "User ID does not exist!")
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
        wx.MessageBox("Success!", f"User {user_id} has been deleted successfully!")
        window.Destroy()

    def view_connections_window(self, event):
        window = wx.Dialog(self, title="view Connection", size=(220, 150))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user_id_label = wx.StaticText(window, label="User ID:")
        sizer.Add(user_id_label, 0, wx.ALL, 5)

        user_entry = wx.TextCtrl(window)
        sizer.Add(user_entry, 0, wx.EXPAND | wx.ALL, 5)

        view_connection_button = wx.Button(window, label="View Connection")
        view_connection_button.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.view_connections(user_entry.GetValue().strip(), window),
        )

        sizer.Add(view_connection_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        window.SetSizer(sizer)
        window.ShowModal()

    def view_connections(self, user_id, window):
        if user_id not in self.users:
            wx.MessageBox("User ID does not exist!", "Error", wx.OK | wx.ICON_ERROR)
            return

        connections = self.users[user_id]["connections"]
        if connections:
            message = "\n".join(f"{uid}: {date}" for uid, date in connections.items())
        else:
            message = "No connections found."
        wx.MessageBox(
            f"Connections:\n{message}", "View Connections", wx.OK | wx.ICON_INFORMATION
        )
        window.Destroy()

    def create_connection_window(self, event):
        window = wx.Dialog(self, title="Create connection", size=(400, 300))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user1_Label = wx.StaticText(window, label="User 1 ID:")
        sizer.Add(user1_Label, 0, wx.ALL, 5)
        user1_entry = wx.TextCtrl(window)
        sizer.Add(user1_entry, 0, wx.EXPAND | wx.ALL, 5)

        user2_Label = wx.StaticText(window, label="User 2 ID:")
        sizer.Add(user2_Label, 0, wx.ALL, 5)
        user2_entry = wx.TextCtrl(window)
        sizer.Add(user2_entry, 0, wx.EXPAND | wx.ALL, 5)

        weight_Label = wx.StaticText(window, label="Connection Weight (0.01 - 1):")
        sizer.Add(weight_Label, 0, wx.ALL, 5)
        weight_entry = wx.TextCtrl(window)
        sizer.Add(weight_entry, 0, wx.EXPAND | wx.ALL, 5)

        view_connection_button = wx.Button(window, label="View Connection")
        view_connection_button.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.create_connection(
                user1_entry.GetValue().strip(),
                user2_entry.GetValue().strip(),
                weight_entry.GetValue().strip(),
                window,
            ),
        )
        sizer.Add(view_connection_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def create_connection(self, user1, user2, weight, window=None):
        if not all(user in self.users for user in [user1, user2]):
            if window != None:
                wx.MessageBox("Error", "One or Both users do not exist!")
                window.Destroy()
            return
        if user1 == user2:
            if window != None:
                wx.MessageBox("Error", "Can't connect with yourself!")
                window.Destroy()
            return

        try:
            weight = float(weight)
            if not (0.01 <= weight <= 1):
                raise ValueError
        except ValueError:
            if window != None:
                wx.MessageBox("Weight must be in between 0.01 and 1!", "Error")
            return

        self.connections[(user1, user2)] = weight
        date = datetime.date.today().isoformat()
        self.users[user1]["connections"][user2] = date
        self.users[user2]["connections"][user1] = date

        network_cpp.add_connection(user1, user2, weight)
        if window != None:
            wx.MessageBox(
                f"Connection between {user1} and {user2} has been made!", "Success!"
            )
            window.Destroy()
        self.update_visualization()

    def save_network(self, event):
        files = [f for f in os.listdir(self.save_folder) if f.endswith(".xyz")]
        next_file = f"save{len(files):02}.xyz"
        save_path = os.path.join(self.save_folder, next_file)

        with open(save_path, "w") as file:
            file.write(f"Users={self.users}\n")
            file.write(f"Connections={self.connections}\n")
        wx.MessageBox(f"Network saved to {save_path}.", "Save Network")

    def load_network(self, event):
        files = [f for f in os.listdir(self.save_folder) if f.endswith(".xyz")]
        if not files:
            wx.MessageBox("No saved networks found.", "Load Network")
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
        self.update_visualization()
        wx.MessageBox(f"Network loaded from {load_path}.", "Load Network")

    def generate_random_network_window(self, event):
        window = wx.Dialog(self, title="Create a random network", size=(400, 300))
        sizer = wx.BoxSizer(wx.VERTICAL)

        generate_label = wx.StaticText(window, label="Choose network size generation:")
        sizer.Add(generate_label, 0, wx.ALL, 5)

        self.get_size = wx.Slider(
            window, value=1, minValue=1, maxValue=1000, name=wx.SliderNameStr
        )
        sizer.Add(self.get_size, 0, wx.EXPAND | wx.ALL, 5)

        self.value_label = wx.StaticText(window, label="Current size: 1")
        sizer.Add(self.value_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.get_size.Bind(wx.EVT_SLIDER, self.on_slider_change)

        generate_btn = wx.Button(window, label="Generate Network")
        generate_btn.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.generate_random_network(self.get_size.GetValue(), window),
        )

        sizer.Add(generate_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def on_slider_change(self, event):
        value = self.get_size.GetValue()
        self.value_label.SetLabel(f"Current size: {value}")

    def generate_random_network(self, size, window):
        self.users = {}
        self.connections = {}
        network_cpp.clear_network()
        size = int(size)
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
                    network_cpp.add_connection(user_id_f, user_id_s, weight)
                    existing_connections.add((user_id_f, user_id_s))
                    break

    def update_connection_weight(self, user1, user2, new_weight, window):
        if user1 not in self.users or user2 not in self.users:
            wx.MessageBox("One or Both users do not exist!", "Error")
            window.Destroy()
            return
        if user1 not in self.users[user2]["connections"]:
            wx.MessageBox("Users do not share a connection!", "Error")
            window.Destroy()
            return
        try:
            new_weight = float(new_weight.GetValue().strip())
            if not (0.01 <= new_weight <= 1):
                raise ValueError
        except ValueError:
            wx.MessageBox("Error", "Weight must be in between 0.01 and 1!")
            return
        self.connections[(user1, user2)] = new_weight
        wx.MessageBox(
            f"Connection between {user1} and {user2} has been updated!", "Success!"
        )
        self.update_visualization(run_window=False)
        window.Destroy()

    def update_connection_weight_window(self, event):
        window = wx.Dialog(self, title="Update Connection Weight", size=(400, 300))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user1_label = wx.StaticText(window, label="User 1 ID:")
        sizer.Add(user1_label, 0, wx.ALL, 5)
        user1_entry = wx.TextCtrl(window)
        sizer.Add(user1_entry, 0, wx.EXPAND | wx.ALL, 5)

        user2_label = wx.StaticText(window, label="User 2 ID:")
        sizer.Add(user2_label, 0, wx.ALL, 5)
        user2_entry = wx.TextCtrl(window)
        sizer.Add(user2_entry, 0, wx.EXPAND | wx.ALL, 5)

        connection_label = wx.StaticText(window, label="Connection Weight (0.01 - 1):")
        sizer.Add(connection_label, 0, wx.ALL, 5)
        new_weight_entry = wx.TextCtrl(window)
        sizer.Add(new_weight_entry, 0, wx.EXPAND | wx.ALL, 5)

        update_weight_btn = wx.Button(window, label="Update Weight")
        update_weight_btn.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.update_connection_weight(
                user1_entry.GetValue().strip(),
                user2_entry.GetValue().strip(),
                new_weight_entry,
                window,
            ),
        )

        sizer.Add(update_weight_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def recommend_friends_window(self, event):
        window = wx.Dialog(self, title="Friend Recommendation", size=(220, 150))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user_label = wx.StaticText(window, label="User ID:")
        sizer.Add(user_label, 0, wx.ALL, 5)
        user_entry = wx.TextCtrl(window)
        sizer.Add(user_entry, 0, wx.EXPAND | wx.ALL, 5)

        def recommend_friends():
            user_id = user_entry.GetValue().strip()
            if user_id not in self.users:
                wx.MessageBox("User ID does not exist!", "Error")
                window.Destroy()
                return

            recommendations = network_cpp.recommend_friends(user_id)
            if not recommendations:
                wx.MessageBox("No friends found!", "Recommendations")
                window.Destroy()
                return
            else:
                message = "\n".join(recommendations)
                wx.MessageBox(message, "Recommendations")

        get_recommendation_btn = wx.Button(window, label="Get Recommendations")
        get_recommendation_btn.Bind(wx.EVT_BUTTON, lambda evt: recommend_friends())

        sizer.Add(get_recommendation_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def detect_communities_window(self, event):
        window = wx.Dialog(self, title="Detect Communities", size=(220, 150))
        sizer = wx.BoxSizer(wx.VERTICAL)

        threshold_label = wx.StaticText(window, label="Threshold: 0.01 - 1:")
        sizer.Add(threshold_label, 0, wx.ALL, 5)

        threshold_entry = wx.TextCtrl(window)
        sizer.Add(threshold_entry, 0, wx.EXPAND | wx.ALL, 5)

        def community_detection():
            try:
                threshold = float(threshold_entry.GetValue().strip())
                if not (0.01 <= threshold <= 1):
                    raise ValueError
                communities = network_cpp.detect_communities(threshold)
                if not communities:
                    wx.MessageBox("No communities found!", "Communities")
                else:
                    communities_message = "\n\n".join(
                        [
                            f"Community {i+1}: " + ", ".join(community)
                            for i, community in enumerate(communities)
                        ]
                    )
                    wx.MessageBox(communities_message, "Communities")
            except ValueError:
                wx.MessageBox("Threshold must be between 0.01 and 1.", "Error")
                window.Destroy()

        detect_communities_btn = wx.Button(window, label="Detect Communities")
        detect_communities_btn.Bind(wx.EVT_BUTTON, lambda evt: community_detection())
        sizer.Add(detect_communities_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def shortest_path_window(self, event):
        window = wx.Dialog(self, title="Shortest Path", size=(400, 300))
        sizer = wx.BoxSizer(wx.VERTICAL)

        user_start = wx.StaticText(window, label="Start User ID:")
        sizer.Add(user_start, 0, wx.ALL, 5)
        start_entry = wx.TextCtrl(window)
        sizer.Add(start_entry, 0, wx.EXPAND | wx.ALL, 5)

        user_end = wx.StaticText(window, label="End User ID:")
        sizer.Add(user_end, 0, wx.ALL, 5)
        end_entry = wx.TextCtrl(window)
        sizer.Add(end_entry, 0, wx.EXPAND | wx.ALL, 5)

        def shortest_path():
            start = start_entry.GetValue().strip()
            end = end_entry.GetValue().strip()
            if start not in self.users or end not in self.users:
                wx.MessageBox("Both Users must exist!", "Error")
                return
            path = network_cpp.dijkstra(start, end)
            if not path:
                wx.MessageBox("No path found!", "Error")
            else:
                path_message = " ->".join(path)
                wx.MessageBox(f"Shortest path: {path_message}", "Shortest Path")
                self.update_visualization(shortestpath=path)

        shortest_path_btn = wx.Button(window, label="Find Shortest Path")
        shortest_path_btn.Bind(wx.EVT_BUTTON, lambda evt: shortest_path())
        sizer.Add(shortest_path_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        window.SetSizer(sizer)
        window.ShowModal()

    def update_visualization(self, shortestpath=False):
        def worker_thread():
            net = Network(notebook=True, cdn_resources="in_line")
            net.nodes = []
            net.edges = []

            for user_id in self.users:
                user_data = self.users[user_id]
                net.add_node(user_id, label=user_data["name"] + f" ({user_id})")

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

            temp_file_path = os.path.join(os.getcwd(), "temp_network.html")
            net.show(temp_file_path)

            while not os.path.exists(temp_file_path):
                time.sleep(0.1)

            wx.PostEvent(self, UpdateWebViewEvent(filepath=temp_file_path))

        threading.Thread(target=worker_thread, daemon=True).start()

    def on_update_webview(self, event):
        self.webview.SetZoomType(wx.html2.WEBVIEW_ZOOM_TYPE_TEXT)
        self.webview.LoadURL(f"file://{event.filepath}")

    def add_overlay_info(self, html_file):
        total_nodes = len(self.users)
        total_edges = len(self.connections)

        overlay_html = f"""
        <div style="position: absolute; top: 10px; left: 10px; background-color: rgba(255, 255, 255, 0.8); padding: 10px; border: 1px solid white; z-index: 1000;">
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
    app = wx.App(False)
    frame = SocialNetworkApp(None, title="Social Network - Georgios Tzanopoulos")
    frame.Show()
    app.MainLoop()
