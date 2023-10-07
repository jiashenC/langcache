def read():
    path = "train.csv"
    with open(path) as f:
        for i, line in enumerate(f.read().splitlines()):
            if i == 0:
                continue
            line = line.strip('"')
            line = line.split('","')
            yield {
                "qid1": int(line[1]),
                "qid2": int(line[2]),
                "q1": line[3],
                "q2": line[4],
                "duplicate": True if line[5] == "1" else False,
            }
