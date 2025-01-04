#ifndef MAP_REDUCE_HPP
#define MAP_REDUCE_HPP

#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>
#include <algorithm>
#include <cctype>
#include <thread>
#include <mutex>
#include <sstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace std;

const unordered_set<string> stop_words = {
    "", "a", "an", "the", "and", "but", "or", "nor", "for", "so", "on", "in", "at", "to", "by", "with", "about",
    "against", "between", "into", "through", "during", "before", "after", "above", "below", "from", "up",
    "down", "out", "off", "over", "again", "further", "then", "once", "here", "there", "when", "where", "what",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "now", "my", "me", "are", "is", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "may", "might", "must", "could", "would", "should", "shall", "get", "got", "we",
    "you", "your", "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "i", "am"
};


/**
* @brief mapper function to count word frequencies using multiple threads
* @param input_text text to process
* @param freq_results output parameter to store word frequencies
*/
void mapper(const string& input_text, vector<unordered_map<string, int>>& freq_results);

/**
* @brief reduce function to combine word frequencies
* @param freq_results word frequencies from mappers
* @return combined word frequencies
*/
unordered_map<string, int> reducer(const vector<unordered_map<string, int>>& freq_results);


#endif
