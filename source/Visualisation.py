import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
from scipy.interpolate import make_interp_spline


def extract_data_from_json_files(directory):
    all_data = {}
    for filename in os.listdir(directory):
        if filename.endswith("_stats.json"):
            year = filename.split('_')[0]
            with open(os.path.join(directory, filename), 'r') as file:
                year_data = json.load(file)
                all_data[year] = year_data
    return all_data





def aggregate_sentiments_by_year_and_song(data):
    aggregated_data = {}
    for year, songs in data.items():
        year_aggregated = {}
        for song_name, stats in songs.items():
            sentiment_scores = stats['sentiment_transformer'][0]
            # Define positive and negative emotion labels
            positive_emotions = ['joy', 'approval', 'optimism', 'excitement', 'amusement', 'love', 'admiration', 'gratitude']
            negative_emotions = ['anger', 'disapproval', 'annoyance', 'disappointment', 'sadness', 'fear', 'grief', 'disgust', 'remorse', 'embarrassment']
            
            # Initialize aggregation
            positive_score, negative_score = 0, 0

            # Aggregate scores
            for sentiment in sentiment_scores:
                if sentiment['label'] in positive_emotions:
                    positive_score += sentiment['score']
                elif sentiment['label'] in negative_emotions:
                    negative_score += sentiment['score']

            # Calculate final value (positive - negative)
            final_value = positive_score - negative_score
            year_aggregated[song_name] = {'positive': positive_score, 'negative': negative_score, 'final_value': final_value}

        aggregated_data[year] = year_aggregated

    return aggregated_data

def get_top_emotions(data):
    top_emotions = {}
    for year, songs in data.items():
        year_emotions = {}
        for song_data in songs.values():
            for emotion_info in song_data["sentiment_transformer"][0]:
                emotion = emotion_info['label']
                if emotion == 'neutral':
                    continue
                score = emotion_info['score']
                year_emotions[emotion] = year_emotions.get(emotion, 0) + score

        sorted_emotions = sorted(year_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        top_emotions[year] = sorted_emotions
    return top_emotions




# Function to smooth the data
def smooth_line(X, Y):
    X_smooth = np.linspace(min(X), max(X), 300)  # Increase the number of points for smoothness
    spline = make_interp_spline(X, Y, k=3)  # k=3 for cubic spline
    Y_smooth = spline(X_smooth)
    return X_smooth, Y_smooth


def normalise(value, min_value, max_value):
    normalized = 2 * ((value - min_value) / (max_value - min_value)) - 1
    return max(-1, min(normalized, 1))





def plot_avg_sentiment_with_range(data, aggregated_data):
    # Obtain top emotions for each year
    unique_emotions = set()

    # Iterate through all songs in the year "1990" and collect unique emotion labels
    for song_data in data["1990"].values():
        for emotion_info in song_data["sentiment_transformer"][0]:
            unique_emotions.add(emotion_info["label"])



    # Define a colormap that has a large number of unique colors
    colormap = plt.cm.get_cmap('gist_ncar', len(unique_emotions))

    # Create label_colours dictionary with a distinct color for each emotion from the colormap
    label_colours = {emotion: mcolors.rgb2hex(colormap(i)) for i, emotion in enumerate(unique_emotions)}

    
    print(label_colours)


    # Prepare data for plotting
    avg_sentiment_per_year = []
    min_sentiment_per_year = []
    max_sentiment_per_year = []
    years = sorted(data.keys())

    for year in years:
        sentiments = []
        for song, stats in data[year].items():
            lexicon_sentiment = stats.get('sentiment_lexicon', {}).get('compound', 0)
            final_sentiment = aggregated_data[year].get(song, {}).get('final_value', 0)
            # Check if the final polarity is agreed upon by both methods
            if (lexicon_sentiment >= 0 and final_sentiment >= 0) or (lexicon_sentiment < 0 and final_sentiment < 0):
                sentiments.append(final_sentiment)

        if sentiments:  # Ensure there are sentiment values to calculate
            avg_sentiment = sum(sentiments) / len(sentiments)
            avg_sentiment_per_year.append(avg_sentiment)
            min_sentiment_per_year.append(min(sentiments))
            max_sentiment_per_year.append(max(sentiments))
        else:
            print("in here")
            avg_sentiment_per_year.append(0)
            min_sentiment_per_year.append(0)
            max_sentiment_per_year.append(0)
    
    # Find the global minimum and maximum across all years
    global_min = min(min(min_sentiment_per_year), min(avg_sentiment_per_year), min(max_sentiment_per_year))
    global_max = max(max(max_sentiment_per_year), max(avg_sentiment_per_year), max(min_sentiment_per_year))


    avg_sentiment_per_year = [normalise(val, global_min, global_max) for val in avg_sentiment_per_year]
    min_sentiment_per_year = [normalise(val, global_min, global_max) for val in min_sentiment_per_year]
    max_sentiment_per_year = [normalise(val, global_min, global_max) for val in max_sentiment_per_year]


    # Convert years to numerical values for interpolation
    numerical_years = [int(year) for year in years]

    # Apply smoothing
    years_s, avg_s = smooth_line(numerical_years, avg_sentiment_per_year)
    _, min_s = smooth_line(numerical_years, min_sentiment_per_year)
    _, max_s = smooth_line(numerical_years, max_sentiment_per_year)


    # Plotting
    plt.figure(figsize=(12, 6))

    top_emotions_per_year = get_top_emotions(data) 
    used_emotions = set()

    # Add background color for top emotions
    for i, year in enumerate(years):
        print(year)
        base_height = -1
        total_score = sum(score for _, score in top_emotions_per_year[str(year)])
        for emotion, score in top_emotions_per_year[str(year)]:
            used_emotions.add(emotion)
            height = 2 * (score / total_score)  # Normalize height
            color = label_colours.get(emotion, 'grey')  # Default grey if not found
            rect = mpatches.Rectangle((int(year) - 0.4, base_height), 0.8, height, color=color, alpha=0.3)
            plt.gca().add_patch(rect)
            base_height += height



    plt.plot(years_s, avg_s, label='Average Sentiment')
    plt.plot(years_s, min_s, 'r--', label='Min Sentiment', alpha=0.5)  # Dotted line for min sentiment
    plt.plot(years_s, max_s, 'g--', label='Max Sentiment', alpha=0.5)  # Dotted line for max sentiment
    plt.title('Average Sentiment per Year with Most Common Emotions Highlighted')
    plt.xlabel('Year')
    plt.ylabel('Sentiment')
    plt.xticks(rotation=45)  # Rotate year markers by 45 degrees
    plt.ylim(-1, 1)  # Set Y-axis scale from -1 to 1
    # Plot the sentiment lines and capture the first legend
    line_legend = plt.legend(loc='upper right')

    plt.grid(True)

    # Create a list of patches with the unique colors and labels for the legend
    patches = [mpatches.Patch(color=label_colours[emotion], label=emotion) for emotion in used_emotions]

    # Shrink current axis by 20%
    box = plt.gca().get_position()
    plt.gca().set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Place a legend to the right of this axis
    plt.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5))
    # Add the first legend back in place
    plt.gca().add_artist(line_legend)
    plt.show()



def plot_lexical_richness(data):
    # Prepare data for plotting
    avg_lexical_richness_per_year = []
    male_ratios = []
    female_ratios = []
    years = sorted(data.keys())

    for year in years:
        lexical_richness_values = [song_data['lexical_richness'] for song_data in data[year].values()]
        gender_counts = [song_data['gender_subject_analysis'] for song_data in data[year].values()]

        avg_lexical_richness = sum(lexical_richness_values) / len(lexical_richness_values)
        avg_lexical_richness_per_year.append(avg_lexical_richness)

        # Sum gender counts for each year and calculate ratio
        total_male = sum(gender_count[0] for gender_count in gender_counts)
        total_female = sum(gender_count[1] for gender_count in gender_counts)
        total_gender_counts = total_male + total_female
        male_ratio = total_male / total_gender_counts if total_gender_counts > 0 else 0
        female_ratio = total_female / total_gender_counts if total_gender_counts > 0 else 0
        male_ratios.append(male_ratio)
        female_ratios.append(female_ratio)
        print(f"male to female ratio is {male_ratio}:{female_ratio} in {year}")

    # Apply smoothing
    numerical_years = [int(year) for year in years]
    years_s, avg_s = smooth_line(numerical_years, avg_lexical_richness_per_year)

    # Convert the years to integers if they are not already
    years_int = [int(year) for year in years]
    # Get the width of each bar based on the range of years to cover the intervals correctly
    if len(years) > 1:
        width = (max(years_int) - min(years_int)) / (len(years_int) - 1) * 0.8
    else:
        width = 0.8  # default width if only one year

    # Plotting
    plt.figure(figsize=(12, 6))

    # Add stacked bars for gender ratios
    plt.bar(years_int, female_ratios, color='pink', edgecolor='black', width=width, label='Female Subject Ratio', alpha=0.5)
    plt.bar(years_int, male_ratios, bottom=female_ratios, color='blue', edgecolor='black', width=width, label='Male Subject Ratio', alpha=0.5)


    plt.plot(years_s, avg_s, label='Average Lexical Richness', color='orange')
    plt.title('Average Lexical Richness per Year with Gender Subject Ratios Highlighted')
    plt.xlabel('Year')
    plt.ylabel('Lexical Richness')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.show()






directory = 'finished_data/'
extracted_data = extract_data_from_json_files(directory)
print(len(extracted_data["1990"]))
# Assuming `extracted_data` contains the data extracted from JSON files
aggregated_sentiments = aggregate_sentiments_by_year_and_song(extracted_data)
#print(aggregated_sentiments)










# Assuming `aggregated_sentiments` contains the aggregated data
plot_avg_sentiment_with_range(extracted_data, aggregated_sentiments)


#plot_lexical_richness(extracted_data)


