#!/usr/bin/python
# -*- coding: utf-8 -*-

""" description """

import re

# from collections import Counter, defaultdict

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, \
    FileType, ArgumentTypeError
from io import TextIOWrapper
import sys
import json
import logging
from logging import config
import yaml
from lxml import etree


DEFAULT_LOGGING_CONFIG_FILEPATH = 'logging.conf.yml'
APPLICATION_NAME = 'stackoverflow'
logger = logging.getLogger(APPLICATION_NAME)

class EncodedFileType(FileType):
    """ description """

    def __call__(self, string):
        """ description """
        if string == '-':
            if 'r' in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, \
                        encoding=self._encoding)
                return stdin
            if 'w' in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, \
                        encoding=self._encoding)
                return stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)
        try:
            return open(string, self._mode, self._bufsize, \
                            self._encoding, self._errors)
        except OSError as exception:
            message = " can't open %s : %s"
            raise ArgumentTypeError(message % (string, exception))


QUESTIONS_FILE_PATH = 'stackoverflow_posts_sample.xml'

# QUESTIONS_FILE_PATH = "test.xml"
# QUESTIONS_FILE_PATH = "test_russian.xml"

STOP_WORDS_FILE_PATH = 'stop_words_en.txt'

# STOP_WORDS_FILE_PATH = "stop_en.txt"
# STOP_WORDS_FILE_PATH = "stop_russian.txt"

QUERIES_FILE_PATH = 'queries.csv'

POSTTYPEID = 'PostTypeId'
SCORE = 'Score'
TITLE = 'Title'
CREATIONDATE = 'CreationDate'

MAIN_LOG_FILE = 'stackoverflow_analytics.log'
DEBUG_LOG_FILE = 'stackoverflow_analytics.warn'


class Statistics:

    """ Statistics """

    def __init__(self):
        self.nwords = 0
        self.nwords = 0
        self.stop_words = set()
        self.words_dict = {}
        self.words_unique = []
        self.ymin = 0
        self.ymax = 0
        self.index = []

    def load_xml(self, fxml):
        """ description """
        result = []
        self.ymin = 3000
        self.ymax = 0
        for line in fxml:
            result_item = []
            line = line.strip()
            try:
                parser = etree.XMLParser(remove_blank_text=True)
                row = etree.fromstring(line, parser)
            except:
                continue

            attributes = row.attrib
            typeid = attributes.get(POSTTYPEID)
            score = attributes.get(SCORE)
            title = attributes.get(TITLE)

            creation_date = attributes.get(CREATIONDATE)
            if typeid == '2':
                continue

            if title is None:
                continue
            result_item.append(title)

            if score is None:
                continue
            result_item.append(score)

            if creation_date is None:
                continue
            year = creation_date[:4]
            if int(year) < self.ymin:
                self.ymin = int(year)
            if int(year) > self.ymax:
                self.ymax = int(year)
            result_item.append(year)
            result.append(result_item)
        fxml.close()
        return result

    def process_stop_words(self, fin):
        """ description """

        self.stop_words = set()
        for line in fin:
            self.stop_words.add(line.strip().lower())
        return self.stop_words

    def build_index(self, fin, questions):
        """ description """

        self.process_stop_words(fin)
        words_dict = {}
        max_years = self.ymax - self.ymin + 1
        for question in questions:
            title = question[0]
            score = question[1]
            year = question[2]
            words = re.findall('\\w+', title.lower())

            for word in list(set(words)):
                if word in self.stop_words:
                    continue
                if word not in words_dict.keys():
                    words_dict[word] = [0] * max_years

                words_dict[word][int(year) - self.ymin] += int(score)

        # print(words_dict)

        words_unique = list(words_dict.keys())
        self.index = [[0 for j in range(len(words_unique))] for i in
                      range(max_years)]
        self.nwords = len(words_unique)

        # print(index.shape)

        for i in range(max_years):
            for j in range(len(words_unique)):
                self.index[i][j] = words_dict[words_unique[j]][i]
        self.words_unique = words_unique
        self.words_dict = words_dict.copy()
        #logger.info('process XML dataset, ready to serve queries')
        logger.info("process XML dataset, ready to serve queries")
        return self.words_dict

    def process_one_query( \
        self, \
        start_year, \
        end_year, \
        top_n, \
        ):
        """ description """

        # print(start_year)
        # print(end_year)
        # print(top_n)

        #logger.debug('got query "%s,%s,%s"', start_year, end_year, top_n)
        logger.debug("got query \"%s,%s,%s\"", start_year, end_year, top_n)
        rate = [0] * self.nwords
        for year in range(int(start_year), int(end_year) + 1):
            if (year >= self.ymin) & (year <= self.ymax):
                rate = [x + y for (x, y) in zip(rate, self.index[year \
                        - self.ymin])]  # print(self.index[year - self.ymin])
        top = [(-y, x) for (x, y) in zip(self.words_unique, rate)]

        # print(top)

        sorted_top = sorted(top)  # , key=lambda top: top[1])

        # top = sorted(sorted_top, key=lambda top: top[0])
        # print(sorted_top)

        json_dict = {}
        json_dict['start'] = int(start_year)
        json_dict['end'] = int(end_year)
        top_k = len(sorted_top)
        not_null = 0
        for i in range(min(top_n, top_k)):
            if sorted_top[i][0] != 0:
                not_null += 1
        top_k = not_null

        # print(sorted_top)

        if top_k < top_n:
            #logger.warning('not enough data to answer, found %s words out of %s for period "%s,%s"'
            #               , top_k, top_n, start_year, end_year)
            logger.warning("not enough data to answer, found %s words out of %s for period \"%s,%s\"", words_found, top_n, start_year, end_year)
        json_dict['top'] = list(map(lambda c: (c[1], -c[0]), \
                                sorted_top[0:top_k]))
        result = json.dumps(json_dict, ensure_ascii=False)
        print(result)
        return(result)

    def process_all_queries(self, fin):
        """ description """
        result = []
        for line in fin:
            line = line.strip()
            if len(line) == 0:
                continue

            (start_year, end_year, top_n) = list(map(int, line.split(',')))

            # print(start_year)
            # print(end_year)
            # print(top_n)

            result_item = self.process_one_query(start_year, end_year, int(top_n))
            result.append(result_item)
        #logger.info('finish processing queries')
        logger.info("finish processing queries")
        return result


def process_query(quest_file, stop_words_file, queries_file):
    """ description """

    stats = Statistics()
    questions = stats.load_xml(quest_file)
    stats.build_index(stop_words_file, questions)
    stats.process_all_queries(queries_file)


def callback_query(arguments):
    """ callback """

    process_query(arguments.quest_file, arguments.stop_words_file,
                  arguments.queries_file)


def setup_logging():
    """ description """

    with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as file:
        logging.config.dictConfig(yaml.safe_load(file))


# setup_logging()

def setup_parser(parser):
    """ description """

    parser.add_argument('--questions', default=QUESTIONS_FILE_PATH,
                        dest='quest_file', type=EncodedFileType('r', \
                        encoding='utf-8'), \
                        help='path to xml with statistics, default path is %(default)s'
                        )

    parser.add_argument('--stop-words', dest='stop_words_file',
                        default=STOP_WORDS_FILE_PATH,
                        type=EncodedFileType('r', encoding='koi8-r'),
                        help='path to stowords_dataset')

    parser.add_argument('--queries', dest='queries_file',
                        default=QUERIES_FILE_PATH,
                        type=EncodedFileType('r', encoding='utf-8'),
                        help='path to queries csv file')

    parser.set_defaults(callback=callback_query)


def main():
    """ desc """
    setup_logging()
    parser = ArgumentParser(prog='stackoverflow_analytics',
                            description='tool to analyse popularity of questions'
                            ,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    setup_parser(parser)

    arguments = parser.parse_args()

    # print(arguments)

    arguments.callback(arguments)


if __name__ == '__main__':
    main()
