"""
Creates the file data/in/people-graph.txt, which represents a graph of people on Wikipedia.
Each line in the file is a link between two people.
People who don't have any outgoing links (but should of course still be part of the graph)
appear at the end of the file with an empty string for the end node.

See data/in/put-files-here.txt for details on the required input files.
"""

import os

people_file_path = 'data/in/people.txt'
links_file_path = 'data/in/links-filt.txt'
redirects_file_path = 'data/in/redirects.txt'
people_graph_file_path = 'data/in/people-graph.txt'


def main():
    if os.path.isfile(people_graph_file_path):
        print(f'file {people_graph_file_path} already exists, skipping.')
        return

    out_lines = set()
    people_with_outgoing_links = set()

    print('reading list of redirects')

    with open(redirects_file_path, encoding='utf-8') as redirects_file:
        redirects = set([line.strip().split('|')[0] for line in redirects_file if line.strip()])

    print()
    print('reading list of people')

    people = set()
    with open(people_file_path, encoding='utf-8') as people_file:
        for line in people_file:
            person = line.strip().split('|')[0]
            if person not in redirects:
                people.add(person)

    print()
    print('writing list of links between people')

    with (open(links_file_path, 'r', encoding='utf-8') as links_file,
          open(people_graph_file_path, 'w', encoding='utf-8') as out_file):
        i = 0
        for line in links_file:
            start_node, *end_nodes = line.strip().split('|')
            if start_node in people:
                for end_node in end_nodes:
                    if end_node in people and (start_node, end_node) not in out_lines:
                        people_with_outgoing_links.add(start_node)
                        out_file.write(f'{start_node}|{end_node}\n')
                        out_lines.add((start_node, end_node))

            i += 1
            if i % 10000 == 0:
                print(f'\r    {i} {start_node}', end='')

        print(f'\r    {i}')

        for person in people:
            if person not in people_with_outgoing_links:
                out_file.write(f'{person}|\n')



if __name__ == "__main__":
    main()
