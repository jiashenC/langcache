import os
import evadb
import openai
import string
import random
import multiprocessing as mp

from langcache.statistics.simple import SimpleStatistics
from langcache.tuning.tune import tune


import os

dir_path = os.path.dirname(os.path.realpath(__file__))


class Cache:
    def __init__(self, name=None, tune_frequency=5, tune_policy="precision"):
        self.cursor = evadb.connect().cursor()

        # Setup needed functions.
        self.cursor.query(
            f"""
            CREATE FUNCTION IF NOT EXISTS SentenceFeature IMPL "{dir_path}/functions/sentence_feature.py"
        """
        ).df()

        # Setup LLM
        self.llm_msg = [
            {
                "role": "system",
                "content": """Reply whether two quetions are semantically equivalent.
                Questions will be wrapped in double quotes and separated by comma. Only reply "Equal" or "Not Equal".""",
            },
            {"role": "user", "content": None},
        ]

        # Setup needed variables.
        if name is not None:
            self.cache_name = name
        else:
            self.cache_name = self._generate_random_name()
        self.init = False

        # Threshold distance and tuning hyper-parameter.
        self.distance_threshold = 4
        self.tune_time = 0
        self.tune_frequency = tune_frequency
        self.tune_policy = tune_policy

        # Statistics.
        self.stats_list = []

    def _replace_str(self, string: str):
        replace_list = [
            ('"', "'"),
            (";", "."),
        ]
        for prev, cur in replace_list:
            string = string.replace(prev, cur)
        return string

    def _generate_random_name(self, size=10):
        chars = string.ascii_lowercase
        return "".join(random.choice(chars) for _ in range(size))

    def _evaluate_and_tune(self, key: str, ret_key: str, distance: float, **kwargs):
        if "response" in kwargs:
            # For testing only.
            response = kwargs["response"]
        else:
            # LLM tuning.
            self.llm_msg[1]["content"] = f""" "{ret_key}" , "{key}" """
            response = (
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=self.llm_msg,
                )
                .choices[0]
                .message.content
            )

        # Append statistics for tuning.
        if response == "Equal":
            if distance < self.distance_threshold:
                self.stats_list.append(
                    SimpleStatistics(tp=1, fn=0, fp=0, distance=distance)
                )
            else:
                self.stats_list.append(
                    SimpleStatistics(tp=0, fn=1, fp=0, distance=distance)
                )
        elif response == "Not Equal":
            if distance < self.distance_threshold:
                self.stats_list.append(
                    SimpleStatistics(tp=0, fn=0, fp=1, distance=distance)
                )

        # Tune the threshold distance.
        self.distance_threshold = tune(self.stats_list, self.tune_policy)

    def _top_k(self, key: str, k: int = 1):
        # Rewrite key double quotes.
        key = self._replace_str(key)

        # Query similar questions.
        df = self.cursor.query(
            f"""
            SELECT T.key, T.value, Similarity(SentenceFeature("{key}"), SentenceFeature(T.key)) FROM
            (SELECT * FROM {self.cache_name} ORDER BY Similarity(SentenceFeature("{key}"), SentenceFeature(key)) LIMIT 1) AS T
        """
        ).df()

        # Extract results.
        ret_distance = float(df["distance"][0])
        ret_key = df["key"][0]
        ret_value = df["value"][0]

        return ret_key, ret_value, ret_distance

    def get(self, key: str):
        if not self.init:
            return None

        # Rewrite key double quotes.
        key = self._replace_str(key)

        # Get top k results.
        ret_key, ret_value, ret_distance = self._top_k(key)

        # Tune threshold hyper-parameter.
        if self.tune_frequency != 0 and self.tune_time % self.tune_frequency == 0:
            self._evaluate_and_tune(key, ret_key, ret_distance)
        self.tune_time += 1

        # Return results.
        if ret_distance < self.distance_threshold:
            return ret_value
        else:
            return None

    def put(self, key: str, value: str):
        key = self._replace_str(key)
        value = self._replace_str(value)

        if not self.init:
            self.cursor.query(
                f"""
                CREATE TABLE {self.cache_name} (key TEXT(1000), value TEXT(1000))
            """
            ).df()
            self.cursor.query(
                f"""
                INSERT INTO {self.cache_name} (key, value) VALUES ("{key}", "{value}")
            """
            ).df()
            self.cursor.query(
                f"""
                CREATE INDEX {self.cache_name} ON {self.cache_name} (SentenceFeature(key)) USING FAISS
            """
            ).df()
            self.init = True
        else:
            self.cursor.query(
                f"""
                INSERT INTO {self.cache_name} (key, value) VALUES ("{key}", "{value}")
            """
            ).df()
