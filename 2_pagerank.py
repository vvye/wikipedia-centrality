"""
Calculates the (approximate) PageRank score for each person in the graph
and writes the stats to a file.
"""

import os
import random
from collections import Counter, defaultdict

people_graph_file_path = 'data/in/sample-graph.txt'
stats_file_path = 'data/out/sample-pagerank.txt'


def main():
    if not os.path.isfile(people_graph_file_path):
        print(f'file {people_graph_file_path} doesn\'t exist. Run 0_preprocess.py first.')
        return

    with (open(people_graph_file_path, encoding='utf-8') as people_graph_file,
          open(stats_file_path, 'w', encoding='utf-8') as stats_file):

        print('reading graph')

        people = set()
        edges = defaultdict(list)

        i = 0

        for line in people_graph_file:
            start_node, end_node = line.strip().split('|')
            if start_node:
                people.add(start_node)
                if end_node:
                    edges[start_node].append(end_node)

            i += 1
            if i % 10000 == 0:
                print(f'\r    {i}', end='')

        print(f'\r    {i}')

        print()
        print('calculating PageRank scores')

        random_teleport_probability = 0.1
        random.seed(123)  # for reproducible results

        people_list = list(sorted(people))
        num_people = len(people)
        pagerank_scores = Counter()

        current_person = random.choice(people_list)
        num_visits = 0
        min_visits_per_person = 500
        num_people_visited_often_enough = 0

        while True:

            pagerank_scores[current_person] += 1

            if pagerank_scores[current_person] == min_visits_per_person:
                num_people_visited_often_enough += 1
                if num_people_visited_often_enough == num_people:
                    break

            next_edges = edges[current_person]

            # if the current person has no outgoing links, or with some probability,
            # teleport to a random person
            if len(next_edges) == 0 or random.uniform(0, 1) < random_teleport_probability:
                current_person = random.choice(people_list)
            # otherwise, randomly follow one of the edges
            else:
                current_person = random.choice(next_edges)

            num_visits += 1

            if num_visits % 10000 == 0:
                print(f'\r    {num_visits} ({num_people_visited_often_enough} of {num_people} '
                      f'visited at least {min_visits_per_person} times)', end='')

        print(f'\r    {num_visits}')

        print()
        print('writing stats')

        for person, score in pagerank_scores.most_common():
            stats_file.write(f'{score}\t{(score / num_visits):.12f} {person}' + '\n')


if __name__ == '__main__':
    main()
