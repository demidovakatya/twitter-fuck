import os
import re

datadir = "data"
datafiles = os.listdir(datadir)
# datafiles = [ '500000.txt' ]

VALID_CHARS = "абвгдеёжзииклмнопрстуфхцчшщьыъэюя "
# LEN = 100
LEN = 25

raws = [line for df in datafiles for line 
                    in open(os.path.join(datadir, df)).read().splitlines()]
# texts = [res['text'] for res in results]


def process_text(raw_text):
    processed_chars = [ch for ch in re.sub(r'\.|\-', " ", raw_text.lower()) if ch in VALID_CHARS]
    processed_text  = re.sub(r'\s+', ' ', "".join(processed_chars)).strip()
    return processed_text

texts = [process_text(r) for r in raws if process_text(r)]

# lengths = [len(res) for res in results]

def count_simple_blyas(text):
    words = text.split(' ')
    return words.count('бля')

text_2_counts_simple = [(text, count_simple_blyas(text)) for text in texts]
counts_simple = [i[1] for i in text_2_counts_simple]


def count_blyaas(text, blyaas, counts, counts_all):
    for idx, b in enumerate(blyaas):
        words = text.split(' ')
        count = words.count(b)
        counts_all[idx] += count
        counts[idx] += bool(count)
    return counts, counts_all


def all_count_blyaas(texts, blyaas):
    counts = [ 0 ] * LEN
    counts_all = [ 0 ] * LEN

    for text in texts:
        counts, counts_all = count_blyaas(text, blyaas, counts, counts_all)

    result = [ (blyaas[i], counts[i], counts_all[i]) for i in range(LEN)]
    return result


blyaas = ['бля' + 'я' * z for z in range(LEN)]
woah = all_count_blyaas(texts, blyaas)

print(woah)