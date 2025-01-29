import Levenshtein

def are_strings_similar(str1, str2, threshold=0.6):
    similarity = Levenshtein.ratio(str1, str2)
    return similarity > threshold
