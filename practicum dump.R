library(RODBC)
library(ggplot2)
library(tidyverse)
library(RMySQL)
library(dplyr)
library(DBI)
library(scale)

install.packages("quanteda")
library(quanteda)
install.packages("topicmodels")
require(topicmodels)

data <- read.csv("/Users/imget/Desktop/grant.csv", sep = ";", encoding = "UTF-8", header=TRUE)
data.frame(data)

install.packages("stopwords")
library(stopwords)
stopwords(language = "en", source = "snowball")

#sotu_corpus <- corpus(textdata$text, docnames = textdata$doc_id)

# Build a dictionary of lemmas #supposed to be a different file 
#lemma_data <- read.csv("/Users/imget/Desktop/grant.csv", encoding = "UTF-8")

# extended stopword list
#stopwords_extended <- readLines("resources/stopwords_en.txt", encoding = "UTF-8")

# Create a DTM (may take a while)
# corpus_tokens <- sotu_corpus %>% 
#   tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>% 
#   tokens_tolower() %>% 
#   tokens_replace(lemma_data$inflected_form, lemma_data$lemma, valuetype = "fixed") %>% 
#   tokens_remove(pattern = stopwords_extended, padding = T)
# 
# sotu_collocations <- textstat_collocations(corpus_tokens, min_count = 25)
# sotu_collocations <- sotu_collocations[1:250, ]
# 
# corpus_tokens <- tokens_compound(corpus_tokens, sotu_collocations)
install.packages("tidytext")
library(tidytext)
# set a seed so that the output of the model is predictable
ap_lda <- LDA(data, k = 2, control = list(seed = 1234))
ap_lda
## A LDA_VEM topic model with 2 topics.

#word topic probabilities 
library(tidytext)

ap_topics <- tidy(ap_lda, matrix = "beta")
ap_topics

library(ggplot2)
library(dplyr)

ap_top_terms <- ap_topics %>%
  group_by(topic) %>%
  top_n(10, beta) %>%
  ungroup() %>%
  arrange(topic, -beta)

ap_top_terms %>%
  mutate(term = reorder_within(term, beta, topic)) %>%
  ggplot(aes(term, beta, fill = factor(topic))) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ topic, scales = "free") +
  coord_flip() +
  scale_x_reordered()

library(tidyr)

beta_spread <- ap_topics %>%
  mutate(topic = paste0("topic", topic)) %>%
  spread(topic, beta) %>%
  filter(topic1 > .001 | topic2 > .001) %>%
  mutate(log_ratio = log2(topic2 / topic1))

beta_spread


#document topic probabilities
ap_documents <- tidy(ap_lda, matrix = "gamma")
ap_documents

tidy(AssociatedPress) %>%
  filter(document == 6) %>%
  arrange(desc(count))

#example
install.packages("gutenbergr")
library(gutenbergr)
titles <- c("Twenty Thousand Leagues under the Sea", "The War of the Worlds",
            "Pride and Prejudice", "Great Expectations")
books <- gutenberg_works(title %in% titles) %>%
  gutenberg_download(meta_fields = "title")
library(stringr)

# divide into documents, each representing one chapter
by_chapter <- books %>%
  group_by(title) %>%
  mutate(chapter = cumsum(str_detect(text, regex("^chapter ", ignore_case = TRUE)))) %>%
  ungroup() %>%
  filter(chapter > 0) %>%
  unite(document, title, chapter)

# split into words
by_chapter_word <- by_chapter %>%
  unnest_tokens(word, text)

# find document-word counts
word_counts <- by_chapter_word %>%
  anti_join(stop_words) %>%
  count(document, word, sort = TRUE) %>%
  ungroup()

word_counts

chapters_dtm <- word_counts %>%
  cast_dtm(document, word, n)

chapters_dtm

library(topicmodels)
## A LDA_VEM topic model with 4 topics.
chapters_lda <- LDA(chapters_dtm, k = 4, control = list(seed = 1234))
chapters_lda
chapter_topics <- tidy(chapters_lda, matrix = "beta")
chapter_topics

top_terms <- chapter_topics %>%
  group_by(topic) %>%
  top_n(5, beta) %>%
  ungroup() %>%
  arrange(topic, -beta)

top_terms


library(ggplot2)

top_terms %>%
  mutate(term = reorder_within(term, beta, topic)) %>%
  ggplot(aes(term, beta, fill = factor(topic))) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ topic, scales = "free") +
  coord_flip() +
  scale_x_reordered()

#per document classification

chapters_gamma <- tidy(chapters_lda, matrix = "gamma")
chapters_gamma


chapters_gamma <- chapters_gamma %>%
  separate(document, c("title", "chapter"), sep = "_", convert = TRUE)

chapters_gamma

# reorder titles in order of topic 1, topic 2, etc before plotting
chapters_gamma %>%
  mutate(title = reorder(title, gamma * topic)) %>%
  ggplot(aes(factor(topic), gamma)) +
  geom_boxplot() +
  facet_wrap(~ title)


chapter_classifications <- chapters_gamma %>%
  group_by(title, chapter) %>%
  top_n(1, gamma) %>%
  ungroup()

chapter_classifications


book_topics <- chapter_classifications %>%
  count(title, topic) %>%
  group_by(title) %>%
  top_n(1, n) %>%
  ungroup() %>%
  transmute(consensus = title, topic)

chapter_classifications %>%
  inner_join(book_topics, by = "topic") %>%
  filter(title != consensus)

#by word assignments 
assignments <- augment(chapters_lda, data = chapters_dtm)
assignments


assignments <- assignments %>%
  separate(document, c("title", "chapter"), sep = "_", convert = TRUE) %>%
  inner_join(book_topics, by = c(".topic" = "topic"))

assignments


library(scales)

assignments %>%
  count(title, consensus, wt = count) %>%
  group_by(title) %>%
  mutate(percent = n / sum(n)) %>%
  ggplot(aes(consensus, title, fill = percent)) +
  geom_tile() +
  scale_fill_gradient2(high = "red", label = percent_format()) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1),
        panel.grid = element_blank()) +
  labs(x = "Book words were assigned to",
       y = "Book words came from",
       fill = "% of assignments")
#commonly mistaken words

wrong_words <- assignments %>%
  filter(title != consensus)

wrong_words


wrong_words %>%
  count(title, consensus, term, wt = count) %>%
  ungroup() %>%
  arrange(desc(n))


word_counts %>%
  filter(word == "flopson")

install.packages("mallet")
library(mallet)

# create a vector with one string per chapter
collapsed <- by_chapter_word %>%
  anti_join(stop_words, by = "word") %>%
  mutate(word = str_replace(word, "'", "")) %>%
  group_by(document) %>%
  summarize(text = paste(word, collapse = " "))

# create an empty file of "stopwords"
file.create(empty_file <- tempfile())
docs <- mallet.import(collapsed$document, collapsed$text, empty_file)

mallet_model <- MalletLDA(num.topics = 4)
mallet_model$loadDocuments(docs)
mallet_model$train(100)

# word-topic pairs
tidy(mallet_model)

# document-topic pairs
tidy(mallet_model, matrix = "gamma")

# column needs to be named "term" for "augment"
term_counts <- rename(word_counts, term = word)
augment(mallet_model, term_counts)

