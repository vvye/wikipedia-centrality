"""
Calculates the degrees for each person in the graph
and writes the stats to a file.
"""

import os
from collections import Counter

people_graph_file_path = 'data/in/people-graph.txt'
degree_stats_file_path = 'data/out/degree.txt'
in_degree_stats_file_path = 'data/out/in-degree.txt'
out_degree_stats_file_path = 'data/out/out-degree.txt'


def main():
    if not os.path.isfile(people_graph_file_path):
        print(f'file {people_graph_file_path} doesn\'t exist. Run 0_preprocess.py first.')
        return

    people = set()
    degrees_by_person = Counter()
    in_degrees_by_person = Counter()
    out_degrees_by_person = Counter()

    with (open(people_graph_file_path, encoding='utf-8') as people_graph_file,
          open(degree_stats_file_path, 'w', encoding='utf-8') as degree_stats_file,
          open(in_degree_stats_file_path, 'w', encoding='utf-8') as in_degree_stats_file,
          open(out_degree_stats_file_path, 'w', encoding='utf-8') as out_degree_stats_file):
        i = 0

        print('calculating degrees')

        for line in people_graph_file:

            start_node, end_node = line.strip().split('|')
            people.add(start_node)

            if end_node:
                degrees_by_person[end_node] += 1
                in_degrees_by_person[end_node] += 1

            if start_node:
                degrees_by_person[start_node] += 1
                out_degrees_by_person[start_node] += 1

            i += 1
            if i % 10000 == 0:
                print(f'\r    {i}', end='')

        print(f'\r    {i}')

        # fill the missing people's degrees with 0
        for person in people:
            if person not in degrees_by_person:
                degrees_by_person[person] = 0
            if person not in in_degrees_by_person:
                in_degrees_by_person[person] = 0
            if person not in out_degrees_by_person:
                out_degrees_by_person[person] = 0

        print()
        print('writing stats')

        for person, count in degrees_by_person.most_common():
            degree_stats_file.write(f'{degrees_by_person[person]}\t{person}\n')

        for person, count in in_degrees_by_person.most_common():
            in_degree_stats_file.write(f'{in_degrees_by_person[person]}\t{person}\n')

        for person, count in out_degrees_by_person.most_common():
            out_degree_stats_file.write(f'{out_degrees_by_person[person]}\t{person}\n')


if __name__ == '__main__':
    main()
