import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = '6945108849:AAFYOMuzl_zcfer-ayEUK6cf1pD03g5sGwE'
TMDB_API_KEY = '8dda7f3ce30ee223fbe021932609e9ea'

user_ratings = {}
user_watchlist = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your Telegram Bot.')


def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Display this help message\n"
        "/rate [movie title] [rating] - Rate a movie\n"
        "/watchlist - View your watchlist\n"
        "/findmovies [movie title] - Find movies similar to a given title\n"
        "/reviews [movie title] - View reviews for a movie\n"
        "/actorinfo [actor name] - Get information about an actor\n"
        "/details [movie title] - Get details about a movie"
    )
    update.message.reply_text(help_text)



def rate_movie(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) >= 2:
        movie_title = " ".join(args[:-1])
        rating = args[-1]
        user_ratings[movie_title] = rating
        reply_text = f"Your rating for {movie_title} has been saved."
    else:
        reply_text = "Invalid command format. Use /rate [movie title] [rating]."

    update.message.reply_text(reply_text)

def watchlist(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in user_watchlist and user_watchlist[user_id]:
        watchlist_items = "\n".join(user_watchlist[user_id])
        reply_text = f"Your watchlist:\n{watchlist_items}"
    else:
        reply_text = "Your watchlist is empty."

    update.message.reply_text(reply_text)

def find_movies(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        movie_title = " ".join(args)
        genre_ids = get_movie_genre(movie_title)
        if genre_ids:
            movies = get_movies_by_genre(genre_ids[0])
            if movies:
                reply_text = "\n".join(f"{title}: {url}" for title, url in movies)
            else:
                reply_text = "Sorry, I couldn't find any movies of the same genre."
        else:
            reply_text = "Sorry, I couldn't find that movie."
    else:
        reply_text = "Invalid command format. Use /findmovies [movie title]."

    update.message.reply_text(reply_text)

def reviews(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        movie_title = " ".join(args)
        movie_id = get_movie_id(movie_title)
        if movie_id is not None:
            reviews = get_movie_reviews(movie_id)
            if reviews:
                reply_text = "\n\n".join(reviews)
            else:
                reply_text = "Sorry, I couldn't find any reviews for that movie."
        else:
            reply_text = "Sorry, I couldn't find that movie."
    else:
        reply_text = "Invalid command format. Use /reviews [movie title]."

    update.message.reply_text(reply_text)

def actor_info(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        actor_name = " ".join(args)
        reply_text = get_actor_info(actor_name)
    else:
        reply_text = "Invalid command format. Use /actorinfo [actor name]."

    update.message.reply_text(reply_text)

def movie_details(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        movie_title = " ".join(args)
        reply_text = get_movie_details(movie_title)
    else:
        reply_text = "Invalid command format. Use /details [movie title]."

    update.message.reply_text(reply_text)

def get_movie_genre(movie_title):
    response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}')
    data = response.json()
    if data and 'results' in data and data['results']:
        return data['results'][0]['genre_ids']
    else:
        return []

def get_movies_by_genre(genre_id):
    response = requests.get(f'https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}')
    data = response.json()
    if data and 'results' in data:
        return [(movie['title'], f"https://www.themoviedb.org/movie/{movie['id']}") for movie in data['results'][:5]]
    else:
        return []

def get_movie_id(movie_title):
    response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}')
    data = response.json()
    if data and 'results' in data and data['results']:
        return data['results'][0]['id']
    else:
        return None

def get_movie_reviews(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}')
    data = response.json()
    if data and 'results' in data:
        return [review['content'] for review in data['results'][:5]]
    else:
        return []

def get_actor_info(actor_name):
    response = requests.get(f'https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={actor_name}')
    data = response.json()
    if data and 'results' in data and data['results']:
        actor = data['results'][0]
        return f"Name: {actor['name']}\nKnown for: {', '.join(movie['title'] for movie in actor['known_for'])}"
    else:
        return "Sorry, I couldn't find that actor."

def get_movie_details(movie_title):
    response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}')
    data = response.json()
    if data and 'results' in data and data['results']:
        movie = data['results'][0]
        return f"Title: {movie['title']}\nRelease date: {movie['release_date']}\nOverview: {movie['overview']}"
    else:
        return "Sorry, I couldn't find that movie."

def echo(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.lower()

    if message_text.startswith("rate "):
        parts = message_text.split(" ")
        if len(parts) >= 3:
            movie_title = " ".join(parts[1:-1])
            rating = parts[-1]
            user_ratings[movie_title] = rating
            reply_text = f"Your rating for {movie_title} has been saved."
        else:
            reply_text = "Sorry, I didn't understand that. Try rating a movie like this: 'Rate [movie title] [rating]'."
    elif message_text.startswith("add to watchlist "):
        movie_title = message_text[17:].strip()
        user_id = update.message.from_user.id
        if user_id not in user_watchlist:
            user_watchlist[user_id] = []
        user_watchlist[user_id].append(movie_title)
        reply_text = f"{movie_title} has been added to your watchlist."
    elif message_text.startswith("find movies like"):
        movie_title = message_text[17:].strip()
        genre_ids = get_movie_genre(movie_title)
        if genre_ids:
            movies = get_movies_by_genre(genre_ids[0])
            if movies:
                reply_text = "\n".join(f"{title}: {url}" for title, url in movies)
            else:
                reply_text = "Sorry, I couldn't find any movies of the same genre."
        else:
            reply_text = "Sorry, I couldn't find that movie."
    elif message_text.startswith("reviews for "):
        movie_title = message_text[12:].strip()
        movie_id = get_movie_id(movie_title)
        if movie_id is not None:
            reviews = get_movie_reviews(movie_id)
            if reviews:
                reply_text = "\n\n".join(reviews)
            else:
                reply_text = "Sorry, I couldn't find any reviews for that movie."
        else:
            reply_text = "Sorry, I couldn't find that movie."
    elif message_text.startswith("actor info for "):
        actor_name = message_text[15:].strip()
        reply_text = get_actor_info(actor_name)
    elif message_text.startswith("details for "):
        movie_title = message_text[12:].strip()
        reply_text = get_movie_details(movie_title)
    else:
        reply_text = "Sorry, I didn't understand that. Please provide a valid command."

    update.message.reply_text(reply_text)

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("rate", rate_movie, pass_args=True))
    dp.add_handler(CommandHandler("watchlist", watchlist))
    dp.add_handler(CommandHandler("findmovies", find_movies, pass_args=True))
    dp.add_handler(CommandHandler("reviews", reviews, pass_args=True))
    dp.add_handler(CommandHandler("actorinfo", actor_info, pass_args=True))
    dp.add_handler(CommandHandler("details", movie_details, pass_args=True))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
