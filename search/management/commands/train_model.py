import os
from pathlib import Path

import torch
from django.core.management import BaseCommand
from sentence_transformers import InputExample, datasets, models, losses
from tqdm import tqdm
from tqdm.auto import tqdm
from transformers import MT5ForConditionalGeneration, MT5Tokenizer, T5Tokenizer, T5ForConditionalGeneration, pipeline, \
    AutoModelForSeq2SeqLM

from articles.es_documents import ArticleDocument
from search.constants import trained_model_name, get_encoder

def write_to_files(passages):
    tokenizer = MT5Tokenizer.from_pretrained('google/mt5-large', add_prefix_space=False)
    models = [MT5ForConditionalGeneration.from_pretrained('SGaleshchuk/mT5-sum-news-ua'),
              MT5ForConditionalGeneration.from_pretrained('csebuetnlp/mT5_multilingual_XLSum'),
              MT5ForConditionalGeneration.from_pretrained('spursyy/mT5_multilingual_XLSum_rust')]
    for model in models:
        model.eval()
        # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # model.to(device)
    summarizers = [pipeline("summarization", model=model, tokenizer=tokenizer, framework="pt") for model in models]
    pairs = []
    file_count = 0
    # loop through each passage individually
    for p in tqdm(passages):
        p = p.replace('\t', ' ')
        # create input tokens
        # input_ids = tokenizer.encode(p, return_tensors='pt')
        # input_ids = input_ids.to(device)
        # generate output tokens (query generation)
        outputs = []
        for summ in summarizers:
            # outputss = model.generate(
            #     input_ids=input_ids,
            #     max_length=64,
            #     do_sample=True,
            #     top_p=0.95,
            #     num_return_sequences=2
            # )
            summary = summ(p, max_length=16, min_length=3, do_sample=True)[0]
            outputs.append(summary['summary_text'])
        # outputs.append(paraphrase_base(p))
        # decode output tokens to human-readable language
        for output in outputs:
            # append (query, passage) pair to pairs list, separate by \t
            pairs.append(output.replace('\t', ' ') + '\t' + p)

        # once we have 256 pairs write to file
        if len(pairs) > 256:
            with open(f'data/pairs_{file_count}.tsv', 'w+', encoding='utf-8') as fp:
                fp.write('\n'.join(pairs))
            file_count += 1
            pairs = []

    if pairs is not None:
        # save the final, smaller than 1024 batch
        with open(f'data/pairs_{file_count}.tsv', 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(pairs))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("mode", type=str)

    def handle(self, *args, **options):
        if not os.path.exists('data'):
            os.makedirs('data')

        documents = ArticleDocument().search().query('match_all').scan()

        passages = set()
        for doc in documents:
            try:
                passages.add(doc.abstract)
            except:
                continue
        passages = list(passages)

        if 'w' in options['mode']:
            write_to_files(passages)
        if 't' in options['mode']:
            # The next step is to fine-tune a model using MNR loss. We do this easily with the sentence-transformers library.
            #
            # We start by loading the pairs dataset we created into a list of InputExample objects.
            paths = [str(path) for path in Path('data').glob('*.tsv')]

            pairs = []
            for path in tqdm(paths):
                with open(path, 'r', encoding='utf-8') as fp:
                    lines = fp.read().split('\n')
                    for line in lines:
                        if '\t' not in line:
                            continue
                        else:
                            q, p = line.split('\t')
                            pairs.append(InputExample(
                                texts=[q, p]
                            ))
            # Next, we load the pairs into a NoDuplicatesDataLoader. We use the no duplicates data loader to avoid
            # placing duplicate passages in the same batch, as this will confuse the ranking mechanism of MNR loss.
            # torch.cuda.empty_cache()

            batch_size = 3

            loader = datasets.NoDuplicatesDataLoader(
                pairs, batch_size=batch_size
            )
            model = get_encoder('cpu')

            loss = losses.MultipleNegativesRankingLoss(model)
            epochs = 3
            warmup_steps = int(len(loader) * epochs * 0.1)

            model.fit(
                train_objectives=[(loader, loss)],
                epochs=epochs,
                warmup_steps=warmup_steps,
                output_path=trained_model_name,
                show_progress_bar=True,
            )
