#include "map_reduce.hpp"

/**
* @brief Helper function to count word frequencies
* @param text text to process
* @return word frequencies
*/
static unordered_map<string, int> _mapper(const string& text) {
    unordered_map<string, int> word_count;
    istringstream stream(text);
    string word;

    while (stream >> word) {
        // Remove punctuation and convert to lowercase
        word.erase(remove_if(word.begin(), word.end(), ::ispunct), word.end());
        transform(word.begin(), word.end(), word.begin(), ::tolower);

        // Skip stop words
        if (stop_words.find(word) == stop_words.end()) {
            ++word_count[word];
        }
    }

    return word_count;
}

void mapper(const string& input_text, vector<unordered_map<string, int>>& freq_results) {
    // Split the input into chunks (simple line-based splitting for example)
    vector<string> chunks;
    istringstream stream(input_text);
    string line;

    while (getline(stream, line)) {
        chunks.push_back(line);
    }

    // Mutex for thread-safe accumulation of results
    mutex result_mutex;

    // Run the map phase in parallel using threads
    vector<thread> threads;
    for (const string& chunk : chunks) {
        threads.push_back(thread([&, chunk]() {
            auto word_count = _mapper(chunk);  // Mapper function processes the chunk

            lock_guard<mutex> lock(result_mutex);
            freq_results.push_back(word_count);  // Collect result safely
        }));
    }

    // Wait for all threads to complete
    for (auto& t : threads) {
        t.join();
    }
}

unordered_map<string, int> reducer(const vector<unordered_map<string, int>>& freq_results) {
    unordered_map<string, int> final_count;

    for (const auto& result : freq_results) {
        for (const auto& [word, count] : result) {
            final_count[word] += count;
        }
    }

    return final_count;
}

