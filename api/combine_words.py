import functools
from .models.keyword import Keyword
from .models.algorithm import Algorithm
from .models.name import Name
import itertools


def combine_words(keywords: dict, algorithm: Algorithm) -> list[Name]:

    to_permutate = []

    def score_word(word):
        try:
            return f"{word.keyword}_{word.keyword_total_score}"
        except KeyError:
            try:
                return f"{word['prefix']}_2"
            except KeyError:
                return f"{word['suffix']}_2"

    for comp in algorithm.components:
        if comp in keywords:
            to_permutate.append(list(map(score_word, keywords[comp])))
        else:
            to_permutate.append([f"{comp}"])

    permutations = list(itertools.product(*to_permutate))

    name_list: list[Name] = []

    def parse_keyword(word):
        return word.split("_")[0]

    def parse_score(word):
        return int(word.split("_")[1])

    for permutation in permutations:

        individual_words = list(map(parse_keyword, permutation))
        score_permutations = filter(lambda w: "_" in w, permutation)
        scores = list(map(parse_score, score_permutations))

        name = "".join(individual_words)

        # Additional score based on length of name
        name_length_score = 0
        name_length = len(name)
        if name_length <= 6:
            name_length_score = 3
        elif name_length <= 8:
            name_length_score = 2
        elif name_length <= 10:
            name_length_score = 1
        else:
            name_length_score = 0

        name_score = (functools.reduce(lambda a, b: a + b, scores) / len(scores)) + int(
            name_length_score
        )

        name_list.append(
            Name(
                name_length,
                name,
                individual_words,
                scores,
                name_length_score,
                name_score,
            )
        )

    # Filter out names that are more than 15 characters
    temp_set = {
        combined_word for combined_word in name_list if combined_word.length <= 15
    }

    # Sort name list by alphabetical order and length.
    name_list = list(temp_set)
    name_list.sort(
        key=lambda combined_name: getattr(combined_name, "name").lower(), reverse=False
    )
    sorted_by_len_name_list = sorted(
        name_list,
        key=lambda combined_name: getattr(combined_name, "length"),
        reverse=False,
    )

    return sorted_by_len_name_list
