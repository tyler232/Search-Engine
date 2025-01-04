#include "map_reduce.hpp"

#include <iostream>
#include <nlohmann/json.hpp>
#include <string>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cctype>
#include <iterator>

using json = nlohmann::json;
using namespace std;

// return word frequencies as JSON
json index_content(const string& url, const string& title, const string& text) {
    // MapReduce
    vector<unordered_map<string, int>> freq_results;
    mapper(text, freq_results);
    unordered_map<string, int> final_count = reducer({freq_results});

    // create a JSON object to store the word frequencies
    json result;
    result["url"] = url;
    result["title"] = title;
    result["word_frequencies"] = final_count;

    return result;
}

int main() {
    // read JSON data from stdin
    string json_input((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());

    try {
        json data = json::parse(json_input);
        string url = data["url"];
        string title = data["title"];
        string text = data["text"];

        // get the word frequencies in JSON format
        json result = index_content(url, title, text);

        // output the result to stdout as JSON
        cout << result.dump() << endl;
    } catch (const json::exception& e) {
        cerr << "Error parsing JSON: " << e.what() << endl;
        return 1;
    }

    return 0;
}