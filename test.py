import itertools
import functools

word_dict = {"test1": ["kuchen_0", "cake_1"], "test2": ["quite_2", "the_0", "shite_3"]}


def combine():
    components = ["test1", "test2", "djkwakjdawkj", "test1"]

    to_permutate = []

    for comp in components:
        if comp in word_dict:
            to_permutate.append(word_dict[comp])
        else:
            to_permutate.append([f"{comp}"])

    permutations = list(itertools.product(*to_permutate))

    def parse_keyword(word):
        return word.split("_")[0]

    def parse_score(word):
        return int(word.split("_")[1])

    for permutation in permutations:
        individual_words = list(map(parse_keyword, permutation))
        score_permutations = filter(lambda w: "_" in w, permutation)
        scores = list(map(parse_score, score_permutations))

        print(individual_words, scores, functools.reduce(lambda a, b: a + b, scores) / len(scores))

combine()
