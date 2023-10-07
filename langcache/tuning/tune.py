from typing import List
from langcache.statistics.simple import SimpleStatistics


def tune(stats_list: List[SimpleStatistics], policy: str):
    if policy == "precision":
        return tune_precision(stats_list)
    elif policy == "recall":
        return tune_recall(stats_list)
    elif policy == "balance":
        return tune_balance(stats_list)
    else:
        raise NotImplementedError(f"{policy} is not supported")


def tune_precision(stats_list: List[SimpleStatistics]):
    distance_threshold = 0xffffffff
    for stats in stats_list:
        if stats.fp > 0:
            distance_threshold = min(distance_threshold, stats.distance - 0.001)
    return distance_threshold


def tune_recall(stats_list: List[SimpleStatistics]):
    distance_threshold = 0x0
    for stats in stats_list:
        if stats.fn > 0:
            distance_threshold = max(distance_threshold, stats.distance + 0.001)
    return distance_threshold 


def tune_balance(stats_list: List[SimpleStatistics]):
    # Simply take an avarage of two extreme for now.
    return (tune_precision(stats_list) + tune_recall(stats_list)) / 2