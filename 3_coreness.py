"""
Calculates the coreness (and occupation in relation to coreness) of each person in the graph
and writes the stats to a file.

For this project, coreness is calculated based on in-degree,
i.e. the k-core of a graph is the maximal subgraph such that all nodes have _in-degree_ of at least k.

To get the k-core, we cannot just filter out all nodes with in-degree less than k once,
because deleting a node decreases the in-degree of its neighbors, which may then have to be deleted as well.

A person has coreness k if they are contained in the k-core of a graph but not the k+1-core,
e.g. if they are deleted while calculating the 3-core, they have coreness 2.
"""

import copy
import os
from collections import Counter, defaultdict

people_file_path = 'data/in/people.txt'
people_graph_file_path = 'data/in/people-graph.txt'
stats_file_path = 'data/out/coreness.txt'
occupation_stats_file_path = 'data/out/coreness-occupations.txt'


def k_core(k, in_degrees, edges):
    """
    Calculates the k-core of a graph.
    Given a dict of in-degrees (=list of nodes) and a dict of edges, it returns the in-degrees and edges of the k-core.
    Also returns a list of nodes that were deleted from the graph.
    """
    deleted_people = []

    while True:

        num_deleted_this_iteration = 0

        new_in_degrees = copy.deepcopy(in_degrees)
        for person in in_degrees:

            # check if the person has in-degree less than k
            if in_degrees[person] >= k:  # because the dict is sorted, we can abort once we find an in-degree >= k
                break

            # delete the person from the graph
            del new_in_degrees[person]
            num_deleted_this_iteration += 1
            deleted_people.append(person)

            # decrease the in-degree of all their link targets by one
            for other_person in edges[person]:
                if other_person in new_in_degrees:
                    new_in_degrees[other_person] -= 1

            # we don't need to delete the person's edges because in_degrees has all the information we care about
            # (improves performance, but also means edges is not kept consistent with the graph)

        in_degrees = copy.deepcopy(new_in_degrees)
        in_degrees = {k: v for k, v in sorted(in_degrees.items(), key=lambda item: item[1])}

        # repeat until no more people need to be deleted
        if num_deleted_this_iteration == 0:
            break

    return in_degrees, edges, deleted_people


def main():
    if not os.path.isfile(people_graph_file_path):
        print(f'file {people_graph_file_path} doesn\'t exist. Run 0_preprocess.py first.')
        return

    print('reading occupations')

    occupations_by_person = {}
    with open(people_file_path, encoding='utf-8') as people_file:
        for line in people_file:
            person, *occupations = line.strip().split('|')
            if len(occupations) == 1 and occupations[0] == '':
                occupations = []
            occupations_by_person[person] = occupations

    print()
    print('reading graph')

    people = set()
    in_degrees_by_person = Counter()
    edges = defaultdict(list)

    with open(people_graph_file_path, encoding='utf-8') as people_graph_file:
        i = 0

        for line in people_graph_file:
            start_node, end_node = line.strip().split('|')
            people.add(start_node)
            edges[start_node].append(end_node)

            # the in-degree of a person is just how many times that person appears as the end node
            # (unless it's an empty string)
            if end_node:
                in_degrees_by_person[end_node] += 1

            i += 1
            if i % 10000 == 0:
                print(f'\r    {i}', end='')

        print(f'\r    {i}')

    people_without_incoming_links = people - set(in_degrees_by_person.keys())
    for person in people_without_incoming_links:
        in_degrees_by_person[person] = 0

    in_degrees_by_person = {k: v for k, v in sorted(in_degrees_by_person.items(), key=lambda item: item[1])}

    print()
    print('calculating corenesses')

    corenesses = {}
    occupation_stats_by_coreness = {}
    num_people_by_coreness = defaultdict(int)
    k = 1
    num_people_with_coreness_assigned = 0
    total_num_people = len(in_degrees_by_person)

    while True:

        print(f'    {k}-core')

        # overwrite old edges and in-degrees with those from the k-core
        # (so we can use them as new input for the next core)
        in_degrees_by_person, edges, deleted_people = k_core(k, in_degrees_by_person, edges)

        # all people deleted for the k-core have coreness k-1
        for person in deleted_people:
            corenesses[person] = k - 1
        num_people_by_coreness[k - 1] = len(deleted_people)

        # determine the most common occupations among all deleted people
        # (let's say the top occupations that together make up at least half of all occupations, but at most 2,
        # which together with "other/unknown" will be at most 3)
        deleted_people_occupations = Counter()
        total_num_occupations = 0
        for person in deleted_people:
            for occupation in occupations_by_person[person]:
                deleted_people_occupations[occupation] += 1
                total_num_occupations += 1
        threshold = total_num_occupations / 2
        running_total = 0
        most_common_occupations = []
        for occupation, count in deleted_people_occupations.most_common():
            if running_total >= threshold or len(most_common_occupations) >= 2:
                break
            most_common_occupations.append(occupation)
            running_total += count

        # for each deleted person, determine which of the most common occupations (if any) they have
        occupation_stats = Counter()
        for person in deleted_people:
            for occupation in most_common_occupations:
                if occupation in occupations_by_person[person]:
                    occupation_stats[occupation] += 1
                    break
            else:
                occupation_stats['other/unknown'] += 1
        occupation_stats_by_coreness[k - 1] = occupation_stats

        print(f'       {len(deleted_people)} have coreness {k - 1}')
        print(f'       {occupation_stats.most_common()}')

        # calculate next core until all people have a coreness assigned
        num_people_with_coreness_assigned += len(deleted_people)
        if num_people_with_coreness_assigned >= total_num_people:
            break

        k += 1

    print()
    print('writing stats')

    corenesses = {k: v for k, v in sorted(corenesses.items(), key=lambda item: item[1], reverse=True)}
    with open(stats_file_path, 'w', encoding='utf-8') as stats_file:
        for person, coreness in corenesses.items():
            stats_file.write(f'{coreness}\t{person}\n')

    with open(occupation_stats_file_path, 'w', encoding='utf-8') as occupation_stats_file:
        for coreness, occupation_stats in occupation_stats_by_coreness.items():
            occupation_stats_file.write(f'{coreness}\t')
            occupation_stats_file.write(f'{num_people_by_coreness[coreness]}\t')
            for occupation, count in occupation_stats.most_common():
                occupation_stats_file.write(f'{occupation}\t{count}\t')
            occupation_stats_file.write('\n')


if __name__ == '__main__':
    main()
