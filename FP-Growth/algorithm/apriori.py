import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class Apriori:
    def __init__(self, input_data, minsup):
        self.minsup = minsup

        input_dataset = list(map(set, input_data))
        item_counts = self._count_min_items(input_dataset)
        item_set = set(frozenset([item]) for item in item_counts.keys())

        self.fp_dict = self._generate_fp(input_dataset, item_set, item_counts)

    #
    # Part 1: Basic Process
    #
    # filter items which counts small than minsup
    def _count_min_items(self, input_dataset):
        def count_items(input_data):
            item_counts = {}
            for data in input_data:
                for item in data:
                    if item not in item_counts:
                        item_counts[item] = 1
                    else:
                        item_counts[item] += 1
            return item_counts

        item_counts = count_items(input_dataset)
        return {key: value for key, value in item_counts.items() if value >= self.minsup}

    #
    # Part 2: Candidates
    #
    def _generate_next_candidates(self, last_candidates):
        def self_joining(candidates):
            candidates_set = set()
            for itemset_a in candidates:
                for itemset_b in candidates:
                    new_set = itemset_a | itemset_b
                    if len(new_set) == (len(itemset_a) + 1):
                        candidates_set.add(frozenset(new_set))
            return candidates_set

        def pruning(join_candidates, last_candidates):
            fp_set = set()
            for join_candidate in join_candidates:
                for last_candidate in last_candidates:
                    check_set = join_candidate.union(last_candidate)
                    if len(check_set) == len(join_candidate):
                        fp_set.add(join_candidate)
            return fp_set

        joining_candidates = self_joining(last_candidates)
        pruning_candidates = pruning(joining_candidates, last_candidates)
        return pruning_candidates

    def _filter_minsup(self, input_dataset, candidates):
        def count_candidates(input_dataset, candidates):
            current_fp_dict = {}
            for transaction in input_dataset:
                for candidate in candidates:
                    check_set = transaction.union(candidate)
                    if len(check_set) == len(transaction):
                        key = tuple(candidate)
                        if key not in current_fp_dict:
                            current_fp_dict[key] = 1
                        else:
                            current_fp_dict[key] += 1
            return current_fp_dict

        current_fp_dict = count_candidates(input_dataset, candidates)
        return {key: value for key, value in current_fp_dict.items() if value >= self.minsup}

    def _generate_fp(self, input_dataset, item_set, item_counts):
        final_fp_dict = {**item_counts}

        while True:
            candidates = self._generate_next_candidates(item_set)
            new_fp_dict = self._filter_minsup(input_dataset, candidates)

            if len(new_fp_dict) == 0:
                break
            else:
                final_fp_dict = {**final_fp_dict, **new_fp_dict}

            item_set = set(frozenset(transaction) for transaction in new_fp_dict.keys())

        logger.info(final_fp_dict)
        return final_fp_dict
