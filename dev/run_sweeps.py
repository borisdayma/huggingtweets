import tweepy
import random, re, pathlib, os
import torch
import wandb

# <--- Enter your credentials (don't share with anyone) --->
consumer_key = 'biaSWTG7Febg0ALoKyWz6EjAH'
consumer_secret = 'NZO7V8Idp8B3FiYy8ifO2DgZn6MgbdCXrCxP8zwasAekSroKjQ'

# hyperparameters
hyperparameter_defaults = dict(
    handle = 'l2k',
    epochs = 1,
    lr_scheduler = 'constant',
    percent_warmup_steps = 0,
    learning_rate = 5e-5,
    gradient_accumulation_steps = 1)
wandb.init(config=hyperparameter_defaults)
config = wandb.config

# authenticate
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

def dl_tweets(handle):
    # Adapted from https://gist.github.com/onmyeoin/62c72a7d61fc840b2689b2cf106f583c

    # initialize a list to hold all the tweepy Tweets & list with no retweets
    alltweets = []
    n_requests = 0

    # make initial request for most recent tweets with extended mode enabled to get full tweets
    for _ in range(3):
        new_tweets = api.user_timeline(
            screen_name=handle, tweet_mode='extended', count=200)
        n_requests += 1
        if new_tweets: break

    if new_tweets:
        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        # check we cannot get more tweets
        no_tweet_count = 0

        # keep grabbing tweets until the api limit is reached
        while True:
            # all subsequent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(
                screen_name=handle, tweet_mode='extended', count=200, max_id=oldest)
            n_requests += 1
            
            # stop if no more tweets (try a few times as they sometimes eventually come)
            if not new_tweets:
                no_tweet_count +=1
            else:
                no_tweet_count = 0
            if no_tweet_count > 5: break

            # save most recent tweets
            alltweets.extend(new_tweets)

            # update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

            print("...%i tweets downloaded so far" %
                (len(alltweets)))

    n_tweets = len(alltweets)

    print("Grabbed %i tweets after %i requests and %i retries" %
        (n_tweets, n_requests, no_tweet_count))
    
    # get text and remove RT
    my_tweets = [tweet.full_text for tweet in alltweets if not hasattr(tweet, 'retweeted_status')]

    print("Found %i tweets, including %i RT, keeping %i" %
        (n_tweets, n_tweets - len(my_tweets), len(my_tweets)))

    print("Rate limit: ", api.rate_limit_status()['resources']['statuses']['/statuses/user_timeline'])

    return my_tweets

def fix_text(text):
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    return text

def clean_tweet(tweet, allow_new_lines = False):
    bad_start = ['http:', 'https:']
    for w in bad_start:
        tweet = re.sub(f" {w}\\S+", "", tweet)      # removes white space before url
        tweet = re.sub(f"{w}\\S+ ", "", tweet)      # in case a tweet starts with a url
        tweet = re.sub(f"\n{w}\\S+ ", "", tweet)    # in case the url is on a new line
        tweet = re.sub(f"\n{w}\\S+", "", tweet)     # in case the url is alone on a new line
        tweet = re.sub(f"{w}\\S+", "", tweet)       # any other case?
    tweet = re.sub(' +', ' ', tweet)                # replace multiple spaces with one space
    if not allow_new_lines:                         # TODO: predictions seem better without new lines
        tweet = ' '.join(tweet.split())
    return tweet.strip()

def boring_tweet(tweet):
    "Check if this is a boring tweet"
    boring_stuff = ['http', '@', '#']
    not_boring_words = len([None for w in tweet.split() if all(bs not in w.lower() for bs in boring_stuff)])
    return not_boring_words < 3

def make_dataset(dataset, epochs):
    total_text = '<|endoftext|>'
    tweets = [t for t in dataset]
    for _ in range(epochs):
        random.shuffle(tweets)
        total_text += '<|endoftext|>'.join(tweets) + '<|endoftext|>'
    return total_text

def main(config):
    # get relevant tweets
    my_tweets = dl_tweets(config.handle)
    curated_tweets = [fix_text(tweet) for tweet in my_tweets]
    clean_tweets = [clean_tweet(tweet) for tweet in curated_tweets]
    cool_tweets = [tweet for tweet in clean_tweets if not boring_tweet(tweet)]

    # split train/validation sets
    random.shuffle(cool_tweets)
    split_train_valid = 0.9
    train_size = int(split_train_valid * len(cool_tweets))
    valid_size = len(cool_tweets) - train_size
    train_dataset, valid_dataset = torch.utils.data.random_split(cool_tweets, [train_size, valid_size])

    # make data files
    with open('data_{}_train.txt'.format(config.handle), 'w') as f:
        data = make_dataset(train_dataset, config.epochs)
        f.write(data)
    with open('data_{}_valid.txt'.format(config.handle), 'w') as f:
        data = make_dataset(valid_dataset, 1)
        f.write(data)
    
    # Set up training parameters
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    block_size = tokenizer.max_len
    train_dataset = TextDataset(tokenizer=tokenizer, file_path=f'data_{config.handle}_train.txt', block_size=block_size, overwrite_cache=True)
    valid_dataset = TextDataset(tokenizer=tokenizer, file_path=f'data_{config.handle}_valid.txt', block_size=block_size, overwrite_cache=True)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    seed = random.randint(0,2**32-1)
    training_args = TrainingArguments(
        output_dir=f'output/{config.handle}',
        overwrite_output_dir=True,
        do_train=True,
        do_eval=True,
        evaluate_during_training=True,
        num_train_epochs=1,
        per_device_train_batch_size=1,
        logging_steps=5,
        eval_steps=5,
        save_steps=0,
        learning_rate=config.learning_rate,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        seed=seed)
    os.environ['WANDB_WATCH'] = 'false' # used in Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        prediction_loss_only=True)
    
    # Update lr scheduler
    train_dataloader = trainer.get_train_dataloader()
    num_train_steps = int(len(train_dataloader) // config.gradient_accumulation_steps)
    optimizer, _ = trainer.get_optimizers(num_train_steps)
    if config.lr_scheduler == 'constant':
        scheduler = get_constant_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(config.percent_warmup_steps * num_train_steps))
    elif config.lr_scheduler == 'linear':
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(config.percent_warmup_steps * num_train_steps),
            num_training_steps=num_train_steps)
    elif config.lr_scheduler == 'cosine':
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(config.percent_warmup_steps * num_train_steps),
            num_training_steps=num_train_steps)
    
    # Train & evaluate
    trainer.train()
    trainer.evaluate()

from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments, get_constant_schedule_with_warmup, get_cosine_schedule_with_warmup, get_linear_schedule_with_warmup)

if __name__ == '__main__':
    main(config)