# Sentiment-Analysis-of-British-Top-of-the-Pops
This study applies sentiment analysis to British Top of the Pops lyrics from 1961 to 2000, exploring music’s emotional trajectory and its relation to societal changes. Using Natural Language Processing (NLP) techniques, the project investigates how British music reflects and influences its cultural context, providing insights into sentiment trends, gender representation, and lexical diversity across four decades.

Objectives and Motivation
The study seeks to quantify shifts in music sentiment within British pop and rock, hypothesizing that lyrics mirror historical and social moods. Focusing on British music fills a research gap, as previous sentiment studies often cover broader genres or regions. This study’s objective is to correlate sentiment trends with historical events and changes in cultural dynamics, examining how music serves as a reflection of the zeitgeist.

Methodology
Data Acquisition:

Source: Lyrics from British top songs were collected from 1961 to 2000, a period marked by significant cultural and musical changes. Data was sourced through web scraping from the Official Charts, Spotify, and Genius APIs.
Data Processing: Lyrics were cleaned and pre-processed, including punctuation removal, stop word elimination, and case normalization, ensuring the data was ready for analysis.
Sentiment Analysis:

Lexicon-Based Analysis: VADER was used for its effectiveness in handling informal text, making it suitable for song lyrics. VADER assigned sentiment scores, categorizing lyrics as positive, negative, or neutral.
Transformer-Based Analysis: The project also used a transformer model, “SamLowe/roberta-base-go emotions,” to detect nuanced emotional categories. This approach captured a broader spectrum of emotions like love, sadness, and joy, providing a deeper analysis of sentiment.
Gender Representation:

Gender analysis used specific terms to examine how the representation of male and female subjects evolved, tracking shifts in gender portrayal across decades.
Lexical Richness:

Lexical richness, calculated as the ratio of unique words to total words, assessed the diversity and complexity of lyrics, offering insights into artistic trends and creativity over time.
Results
Sentiment Trends:

A general decline in positive sentiment was observed, with prominent emotions being love and sadness, aligning with common music themes. Political and cultural events correlated with sentiment changes; for example, sentiment drops during Thatcher’s tenure or peaks in 1969 related to the moon landing.
Lexical Richness and Gender Dynamics:

Lexical richness was high in the 1970s, possibly reflecting the rise of expressive genres like disco. Gender analysis revealed an increased presence of female subjects in lyrics during the women’s liberation era, though this declined post-1980, perhaps indicating shifting cultural themes.
Conclusion
This project reveals that British music sentiment, gender portrayal, and lexical richness mirror broader societal trends. Future studies could expand the dataset, apply advanced NLP for sarcasm detection, and extend the analysis to current music to understand how sentiment trends continue to evolve.
