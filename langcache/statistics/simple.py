from dataclasses import dataclass


@dataclass
class SimpleStatistics:
    tp: int
    fn: int
    fp: int
    distance: float