import json
import re
import os

#sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline


#nltk - text transformation
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Download required resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')

# Function to convert nltk tag to wordnet tag
def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:          
        return None

def lemmatize_sentence(sentence):
    # Tokenize the sentence and find the POS tag for each token
    nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))  
    # Tuple of (token, wordnet_tag)
    wordnet_tagged = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
    lemmatized_sentence = []
    # Initialize lemmatizer
    lemmatizer = WordNetLemmatizer()
    for word, tag in wordnet_tagged:
        if tag is None:
            # if there is no available tag, append the token as is
            lemmatized_sentence.append(word)
        else:        
            # else use the tag to lemmatize the token
            lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
    return " ".join(lemmatized_sentence)




#-----------------------------------------------Song class-----------------------------------------------#
class Song:
    def __init__(self, song_name, song_lyrics):
        self.song_name = song_name
        self.song_lyrics = song_lyrics
        self.song_lyrics_lines = self.split_into_sentences(song_lyrics)


    def split_into_sentences(song_lyrics):
        # Split based on capital letters, keeping the capital letter at the start of each new sentence
        sentences = re.split(r'(?<!\A)(?=[A-Z])', song_lyrics)
        return [sentence.strip() for sentence in sentences if sentence.strip()]
    


class Text_Analysis:
    def __init__(self):
        self.songs = []
        self.classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

        self.male_terms = set(['he', 'him', 'his', 'man', 'boy', 'brother', 'father', 'son', 'mr', 'sir', 'uncle', 'nephew', 'husband', 'king', 'prince', 'boyfriend'])
        self.female_terms = set(['she', 'her', 'hers', 'woman', 'girl', 'sister', 'mother', 'daughter', 'mrs', 'madam', 'aunt', 'niece', 'wife', 'queen', 'princess', 'girlfriend'])





    #-----------------------------------------------READ AND PROCESS-----------------------------------------------#
    
    def read_song_from_json(self, song_path):
        with open(song_path, 'r') as file:
            song_lyrics = json.load(file)
        return song_lyrics  # This returns the entire JSON object, not indexed by the file name

    

    def get_word_count(self, song_lyrics):
        return len(song_lyrics.split())
    

    def get_unique_words(self, song_lyrics):
        return len(set(song_lyrics.split()))
    

    def sanitise_filename(self, name):
        return "".join([c for c in name if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(' ', '_')



    def get_song(self, song, year, month):
        #assign the song name
        song_name = song
        #construct the filename
        filename = f"data_songs//{year}//{month}//{self.sanitise_filename(song)}.json"
        # get the song from json file
        with open(filename, 'r') as file:
            song_lyrics = json.load(file)
        #create instance of song class, automatically creates a version split into lines
        song = Song(song_name, song_lyrics)
        
        
        #clean data using ntlk
        def clean_song_lyrics(self, song_lyrics):
            pass


#-----------------------------------------------ANALYSIS-----------------------------------------------#
    #sentiment analysis methods
    def sentiment_analysis_lexicon(self, song_lyrics, line_by_line=False):
        analyzer = SentimentIntensityAnalyzer()
        if line_by_line:
            sentiment = [analyzer.polarity_scores(line) for line in song_lyrics]
        else:
            sentiment = analyzer.polarity_scores(song_lyrics)
        return sentiment


    def sentiment_analysis_transformer_28labels(self, song_lyrics):
        model_output = self.classifier(song_lyrics)

        # combine elements to a positive score and a negative score.

        return model_output


    #word count
    def word_count(self, song_lyrics):
        return len(song_lyrics.split())
    

    #unique word count
    def unique_word_count(self, song_lyrics):
        return len(set(song_lyrics.split()))
    

    #lexical richness
    def lexical_richness(self, song_lyrics):
        return self.unique_word_count(song_lyrics) / self.word_count(song_lyrics)



    # gender subject analysis
    def gender_subject_analysis(self, song_lyrics):
        tokens = word_tokenize(song_lyrics.lower())
        male_count = sum(token in self.male_terms for token in tokens)
        female_count = sum(token in self.female_terms for token in tokens)
        return male_count, female_count

        




def find_json_files_in_years_and_months(start_year=1961, end_year=2000):
    base_directory = os.path.join(os.getcwd(), 'data_songs')
    yearly_json_files = {}  # Stores the paths of all JSON files found, organized by year

    for year in range(start_year, end_year + 1):
        year_str = str(year)
        yearly_json_files[year_str] = []

        for month in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
            month_dir = os.path.join(base_directory, year_str, month)

            if os.path.exists(month_dir) and os.path.isdir(month_dir):
                for file in os.listdir(month_dir):
                    if file.endswith(".json"):
                        yearly_json_files[year_str].append(os.path.join(month_dir, file))

    return yearly_json_files



#Dividing the number of words used with the vocabulary gives us a measure of the lexical richness of each artist
bangla = '''[Verse]
My friend came to me
With sadness in his eyes
He told me that he wanted help
Before his country dies
Although I couldn't feel the pain
I knew I had to try
Now I'm asking all of you
To help us save some lives

[Chorus]
Bangladesh, Bangladesh
Where so many people are dying fast
And it sure looks like a mess
I've never seen such distress
Now won't you lend your hand, try to understand?
Relieve the people of Bangladesh

[Chorus]
Bangladesh, Bangladesh
Such a great disaster, I don't understand
But it sure looks like a mess
I've never known such distress
Now please don't turn away, I wanna hear you say
Relieve the people of Bangladesh
Relieve the people of Bangladesh

[Chorus]
Bangladesh, Bangladesh
Now it may seem so far from where we all are
It's something we can't reject
It's something I can't neglect
Now won't you give some bread? Get the starving fed?
We've got to relieve Bangladesh
Relieve the people of Bangladesh
We've got to relieve Bangladesh

[Outro]
Now won't you lend your hand and understand?
Relieve the people of Bangladesh'''






def main():
    all_files = find_json_files_in_years_and_months()
    years = [str(year) for year in range(1961, 2001)]

    # Dictionary to hold all stats
    all_stats = {}

    # Create class instance
    TA = Text_Analysis()

    # Loop through all years
    for year in years:
        print(f"Processing year: {year}")
        year_stats = {}
        songs_processed = 0

        # Check if there are files for the year
        if year in all_files:
            for song_file_name in all_files[year]:
                try:
                    # Read song lyrics from JSON file
                    song_lyrics = TA.read_song_from_json(song_file_name)
                    song_name = os.path.basename(song_file_name)

                    # Gather stats for the song
                    song_stats = {
                        'word_count': TA.get_word_count(song_lyrics),
                        'unique_words': TA.get_unique_words(song_lyrics),
                        'sentiment_lexicon': TA.sentiment_analysis_lexicon(song_lyrics),
                        'sentiment_transformer': TA.sentiment_analysis_transformer_28labels(song_lyrics),
                        'lexical_richness': TA.lexical_richness(song_lyrics),
                        'gender_subject_analysis': TA.gender_subject_analysis(song_lyrics)
                    }

                    # Add the stats to the year_stats dictionary with the song name as the key
                    year_stats[song_name] = song_stats
                    songs_processed += 1

                    # Termination criteria: Stop after processing 100 songs
                    if songs_processed >= 100:
                        break

                except Exception as e:
                    print(f"Error processing {song_file_name}: {e}")
                    continue  # Skip to the next song

        # After all songs for the year are processed or termination criteria is met,
        # add the year's stats to the all_stats dictionary
        all_stats[year] = year_stats

        # Save the yearly stats to a file
        save_year_stats_to_file(year_stats, year)
        print(f"year {year} complete")

    # All processing is finished
    print("finished")
    return all_stats  # You can return it if you want to use the data elsewhere



def save_year_stats_to_file(year_stats, year):
    # Create a directory for finished data if it doesn't exist
    finished_data_directory = os.path.join(os.getcwd(), 'finished_data')
    os.makedirs(finished_data_directory, exist_ok=True)
    
    # Define the filename for the year's stats
    file_path = os.path.join(finished_data_directory, f"{year}_stats.json")
    
    # Save the year's stats to a JSON file
    with open(file_path, 'w') as file:
        json.dump(year_stats, file, indent=4)
        
    print(f"Saved stats for year {year} to {file_path}")


# Call the main function
main_stats = main()

# If you want to do something with the collected stats after main runs:
# for example, print them, you can iterate over main_stats here.



if __name__ == '__main__':
    main()

