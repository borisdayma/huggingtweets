# HuggingTweets

Train in 5m your own Neural Network on someone's tweets and tweet them back your predictions!

## [Try the demo →](https://colab.research.google.com/github/borisdayma/huggingtweets/blob/master/huggingtweets-demo.ipynb)

## Introduction

This project fine-tunes a pre-trained transformer on a user's tweets using [HuggingFace](https://huggingface.co/).

Training and results are automatically logged on [W&B](https://docs.wandb.com) through the [HuggingFace integration](https://docs.wandb.com/huggingface).

![Huggingface + W&B](https://i.imgur.com/vnejHGh.png)

## Usage

If you just want to test the demo, click on below link and share your predictions on Twitter with `#huggingtweets`!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/borisdayma/huggingtweets/blob/master/huggingtweets-demo.ipynb)

To understand how the model works, check [`huggingtweets-dev.ipynb`](huggingtweets-dev.ipynb) or use the following link.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/borisdayma/huggingtweets/blob/master/huggingtweets-dev.ipynb)

## Results

My favorite sample is definitely on Andrej Karpathy, start of sentence "I don't like":

> I don't like this :) 9:20am: Forget this little low code and preprocessor optimization. Even if it's neat, for top-level projects. 9:27am: Other useful code examples? It's not kind of best code, :) 9:37am: Python drawing bug like crazy, restarts regular web browsing ;) 9:46am: Okay, I don't mind. Maybe I should try that out! I'll investigate it :) 10:00am: I think I should try Shigemitsu's imgur page. Or the minimalist website if you're after 10/10 results :) Also maybe Google ImageNet on "Yelp" instead :) 10:05am: Looking forward to watching it talk!

I had a lot of fun running predictions on other people too!

### [See the live report → ](https://app.wandb.ai/wandb/huggingtweets/reports/Huggingtweets-Generate-Tweets-with-Huggingface--VmlldzoxMTY5MjI)

## Future research

Lot more research to do:

* test training top layers vs bottom layers to see how it affects learning of lexical field (subject of content) vs word predictions, memorization vs creativity ;
* data pre-processing can be optimized (padding, end tokens, definition of one sample…) ;
* augment text data with adversarial approaches ;
* what about hashtags? #ConvNets #iloveGANs ;
* need to test more models and do some fine-tuning ;
* pre-train on large Twitter dataset of many people and fine-tune on single user!
* try few shots learning as we have very limited data per user (there is only a limited number of writing styles)
* implement a pipeline to continuously train the network on new tweets.

## About

*Built by Boris Dayma*

[![Follow](https://img.shields.io/twitter/follow/borisdayma?style=social)](https://twitter.com/borisdayma)

My main goals with this project are:

* to experiment with how to train, deploy and maintain neural networks in production ;
* to make AI accessible to everyone.

To see how the model works, visit the project repository.

[![GitHub stars](https://img.shields.io/github/stars/borisdayma/huggingtweets?style=social)](https://github.com/borisdayma/huggingtweets)

**Disclaimer: this project is not to be used to publish any false generated information but to perform research on Natural Language Generation.**

## FAQ

1. Does this project pose a risk of being used for disinformation?

    Large NLP models can be misused to publish false data. OpenAI performed a [staged release of GPT-2](https://openai.com/blog/gpt-2-6-month-follow-up/) to study any potential misuse of their models.

    I want to ensure latest AI technologies are accessible to everyone to ensure fairness and prevent social inequality.

    Huggingtweets shall not be used for creating innapropriate content, nor for any illicit or unethical purposes. Any generated text from other users tweets must explicitly be referenced as such and cannot be published with the intent of hiding their origin. No generated content can be published against a person unwilling to have their data used as such.

1. Why is the demo in colab instead of being a real web app?

    It actually looks much better with [Voilà](https://github.com/voila-dashboards/voila) as the code cells are hidden and automatically executed. Also we can easily deploy it through for free through [Binder](https://mybinder.org/).

    However training such large neural networks require GPU (not available on Binder) and I wanted to make huggingtweets accessible to everybody. [Google Colab](https://colab.research.google.com/) generously offers free GPU so is the perfect place to host this demo.

## Resources

* [A Step by Step Guide to Tracking Hugging Face Model Performance](https://app.wandb.ai/jxmorris12/huggingface-demo/reports/A-Step-by-Step-Guide-to-Tracking-Hugging-Face-Model-Performance--VmlldzoxMDE2MTU)
* [W&B Forum](http://bit.ly/wandb-forum): If you have any questions, reach out to the slack community

## Acknowledgements

I was able to make the first version of this program in just a few days.

It would not have been possible without these people and these open-source tools:

* [W&B](http://docs.wandb.com/) for the great tracking & visualization tools for ML experiments ;
* [Huggingface](https://huggingface.co/) for providing a great framework for Natural Language Understanding ;
* [Tweepy](https://www.tweepy.org/) for providing a great API to interact with Twitter (used in the dev notebook) ;
* [Chris Van Pelt](https://github.com/vanpelt) for hacking with me on the demo ;
* [Lavanya Shukla](https://github.com/lavanyashukla) for her great feedback on the demo ;
* [Colab](https://colab.research.google.com/) for letting people access free GPU!
