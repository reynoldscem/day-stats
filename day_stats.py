from math import isclose
import matplotlib
import os

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt # noQA


def build_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('input_filename')

    return parser


def parse_line(line):
    line = line.rstrip(',')
    import re
    match_expression = re.compile('(\d+\.?\d+) (.*)')
    fields = line.split(',')
    return [
        re.match(match_expression, field.strip()).groups()
        for field in fields
    ]


def topic_equivalence(topic):
    bnn_topic = 'Reading BNNs'
    ensemble_topic = 'Reading ensembles'
    ig_topic = 'Reading Information Geometry'
    maths_topic = 'Maths'
    writing_topic = 'Writing / admin'
    misc_reading_topic = 'Reading miscellaneous'

    topic_equivalences = {
        'Bnns': bnn_topic,
        'Reading bnns': bnn_topic,
        'Ensembles': ensemble_topic,
        'Reading ensembles': ensemble_topic,
        'Information geometry': ig_topic,
        'Lectures (information geometry)': ig_topic,
        'Reading information geometry': ig_topic,
        'Studying maths': maths_topic,
        'Maths': maths_topic,
        'Reading misc': misc_reading_topic,
        'Writing / admin': writing_topic,
        'Writing': writing_topic,
    }
    if topic in topic_equivalences:
        return topic_equivalences[topic]
    else:
        return topic
    raise ValueError


def line_to_time_map(line):
    matches = parse_line(line)
    time_map = {}
    for proportion, topic in matches:
        key, value = topic_equivalence(topic.capitalize()), float(proportion)
        if key in time_map:
            value = value + time_map[key]
            print('Some granularity lost, two tasks on day are \'the same\':')
            print(line)
            print()
        time_map[key] = value
    assert isclose(sum(time_map.values()), 1.0), (
        'Proportions in line: [{}] do not sum to 1.0'.format(line)
    )
    return time_map


def main():
    args = build_parser().parse_args()
    assert os.path.isfile(args.input_filename), (
        '{} must exist'.format(args.input_filename)
    )
    with open(args.input_filename) as fd:
        lines = fd.read().splitlines()
    time_maps_for_days = [line_to_time_map(line) for line in lines]
    all_activities = sorted(list(set(
        key for day_map in time_maps_for_days for key in day_map.keys()
    )))
    print('Check for duplicates:')
    for line in all_activities:
        print(line)

    from collections import defaultdict
    day_totals = defaultdict(float)
    for day in time_maps_for_days:
        for key, value in day.items():
            day_totals[key] += value / len(time_maps_for_days)
    assert isclose(sum(day_totals.values()), 1.0)

    plt.figure(figsize=(12, 12))
    plt.pie(
        day_totals.values(),
        explode=[0.05]*len(day_totals),
        labels=day_totals.keys(),
        autopct=lambda x: '{:.2f}%'.format(x),
        wedgeprops={'width': 0.3}
    )
    plt.title('Time breakdown of different tasks.')
    plt.show()


if __name__ == '__main__':
    main()
