#pragma once

#include <cctype>
#include <cmath>
#include <cstdlib>
#include <string>

// Minimal helpers for flat numeric fields in small hand-written JSON configs.

inline void skip_ws(const std::string& s, size_t& i) {
    while (i < s.size() && std::isspace(static_cast<unsigned char>(s[i]))) {
        ++i;
    }
}

inline bool json_find_float(const std::string& json, const char* key, float& out) {
    const std::string needle = std::string("\"") + key + "\"";
    size_t p = json.find(needle);
    if (p == std::string::npos) {
        return false;
    }
    p = json.find(':', p + needle.size());
    if (p == std::string::npos) {
        return false;
    }
    ++p;
    skip_ws(json, p);
    char* end = nullptr;
    out = std::strtof(json.c_str() + p, &end);
    return end != json.c_str() + p;
}

inline bool json_find_int(const std::string& json, const char* key, int& out) {
    const std::string needle = std::string("\"") + key + "\"";
    size_t p = json.find(needle);
    if (p == std::string::npos) {
        return false;
    }
    p = json.find(':', p + needle.size());
    if (p == std::string::npos) {
        return false;
    }
    ++p;
    skip_ws(json, p);
    char* end = nullptr;
    long v = std::strtol(json.c_str() + p, &end, 10);
    if (end == json.c_str() + p) {
        return false;
    }
    out = static_cast<int>(v);
    return true;
}

inline bool json_find_uint64(const std::string& json, const char* key, unsigned long long& out) {
    const std::string needle = std::string("\"") + key + "\"";
    size_t p = json.find(needle);
    if (p == std::string::npos) {
        return false;
    }
    p = json.find(':', p + needle.size());
    if (p == std::string::npos) {
        return false;
    }
    ++p;
    skip_ws(json, p);
    char* end = nullptr;
    unsigned long long v = std::strtoull(json.c_str() + p, &end, 10);
    if (end == json.c_str() + p) {
        return false;
    }
    out = v;
    return true;
}

inline bool json_find_string_quoted(const std::string& json, const char* key, std::string& out) {
    const std::string needle = std::string("\"") + key + "\"";
    size_t p = json.find(needle);
    if (p == std::string::npos) {
        return false;
    }
    p = json.find(':', p + needle.size());
    if (p == std::string::npos) {
        return false;
    }
    ++p;
    skip_ws(json, p);
    if (p >= json.size() || json[p] != '"') {
        return false;
    }
    ++p;
    size_t end = json.find('"', p);
    if (end == std::string::npos) {
        return false;
    }
    out = json.substr(p, end - p);
    return true;
}
