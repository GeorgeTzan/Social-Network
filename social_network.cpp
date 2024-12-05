#include <iostream>
#include <vector>
#include <map>
#include <climits>
#include <string>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <functional>
#include <algorithm>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  

using namespace std;
namespace py = pybind11;

typedef pair<double, string> Edge; // for pair(weight, user_id)

class SocialNetwork {
public:
    map<string, vector<Edge>> adjList;
    unordered_map<string, pair<string, string>> users; 

    void clear_network() {
        adjList.clear();
        users.clear();
    }

    void add_user(const string &user_id, const string &name, const string &interests) {
        if (adjList.find(user_id) == adjList.end()) {
            adjList[user_id] = {};
            users[user_id] = {name, interests};
        }
    }

    void add_connection(const string &user, const string &other_user, double weight) {
        adjList[user].push_back({weight, other_user});
        adjList[other_user].push_back({weight, user});
    }

    vector<string> dijkstra(const string& start, const string& end) {
        if (adjList.find(start) == adjList.end() || adjList.find(end) == adjList.end()) {
            return {};
        }

        unordered_map<string, double> distances;
        unordered_map<string, string> previous;
        priority_queue<pair<double, string>, vector<pair<double, string>>, greater<pair<double, string>>> pq;

        for (const auto& user : adjList) {
            distances[user.first] = numeric_limits<double>::infinity();
        }
        distances[start] = 0;
        pq.push({0, start});

        while (!pq.empty()) {
            auto [current_distance, current_user] = pq.top();
            pq.pop();

            if (current_distance > distances[current_user]) continue;

            for (const auto& [weight, neighbor] : adjList[current_user]) {
                double new_distance = current_distance + weight;
                if (new_distance < distances[neighbor]) {
                    distances[neighbor] = new_distance;
                    previous[neighbor] = current_user;
                    pq.push({new_distance, neighbor});
                }
            }
        }

        vector<string> path;
        for (string at = end; at != start && previous.find(at) != previous.end(); at = previous[at]) {
            path.push_back(at);
        }
        if (!path.empty() || start == end) {
            path.push_back(start);
        }
        reverse(path.begin(), path.end());
        return path;
    }

    vector<unordered_set<string>> detect_communities(double threshold = 0.01) {
        unordered_set<string> visited;
        vector<unordered_set<string>> communities;

        function<void(const string&, unordered_set<string>&)> dfs = [&](const string& user, unordered_set<string>& community) {
            visited.insert(user);
            community.insert(user);
            for (const auto& [weight, neighbor] : adjList[user]) {
                if (weight >= threshold && visited.find(neighbor) == visited.end()) {
                    dfs(neighbor, community);
                }
            }
        };

        for (const auto& user : adjList) {
            if (visited.find(user.first) == visited.end()) {
                unordered_set<string> community;
                dfs(user.first, community);
                communities.push_back(community);
            }
        }
        return communities;
    }

    vector<string> recommend_friends(const string& user_id) {
        if (adjList.find(user_id) == adjList.end()) {
            return {};
        }

        unordered_map<string, int> friend_count;
        vector<string> recommendations;

        unordered_set<string> direct_friends;
        for (const auto& [weight, friend_id] : adjList[user_id]) {
            direct_friends.insert(friend_id);
        }

        for (const auto& [weight, friend_id] : adjList[user_id]) {
            for (const auto& [weight2, mutual_friend] : adjList[friend_id]) {
                if (mutual_friend != user_id && direct_friends.find(mutual_friend) == direct_friends.end()) {
                    friend_count[mutual_friend]++;
                }
            }
        }

        for (const auto& [recommendation, count] : friend_count) {
            recommendations.push_back(recommendation);
        }

        sort(recommendations.begin(), recommendations.end(), [&](const string& a, const string& b) {
            return friend_count[a] > friend_count[b];
        });

        return recommendations;
    }
};

// Pybind11
PYBIND11_MODULE(social_network, m) {
    py::class_<SocialNetwork>(m, "SocialNetwork")
        .def(py::init<>())
        .def("add_user", &SocialNetwork::add_user)
        .def("add_connection", &SocialNetwork::add_connection)
        .def("dijkstra", &SocialNetwork::dijkstra)
        .def("detect_communities", &SocialNetwork::detect_communities)
        .def("recommend_friends", &SocialNetwork::recommend_friends)
        .def("clear_network", &SocialNetwork::clear_network);
}
