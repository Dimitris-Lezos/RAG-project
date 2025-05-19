import os
import openai

# Define the OpenAI account to use
os.environ["OPENAI_API_KEY"] = ""

####################################################################################
# Use OpenAI to parse the Query and rephrase it                                    #
####################################################################################
def split(query: str) -> (str, str):
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant and you give a single answer. People generally ask about text and books."},
            {"role": "user",
             "content": "Can you split the following query into two queries?"},
            {"role": "user",
             "content": "Make sure you return two separate queries!"},
            {"role": "user",
             "content": "Here is the Query: " + query},
        ],
        temperature=0
    )
    query_1_index = chat_completion.choices[0].message.content.find("Query 1:")
    query_2_index = chat_completion.choices[0].message.content.find("Query 2:")
    return (chat_completion.choices[0].message.content[query_1_index + 8:query_2_index-3],
            chat_completion.choices[0].message.content[query_2_index + 8:])

####################################################################################
# Use OpenAI to parse the Query and rephrase it                                    #
####################################################################################
def rephrase(query: str) -> str:
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant and you give a single answer. People generally ask about text and books."},
            {"role": "user",
             "content": "Can you rephrase the following query?"},
            {"role": "user",
             "content": "Here is the Query: " + query},
        ],
        temperature=0
    )
    return chat_completion.choices[0].message.content

####################################################################################
# Use OpenAI to parse the Query and extract Author                                 #
####################################################################################
def getAuthor(query: str) -> str:
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant and you give a single answer. People generally ask about text and books."},
            {"role": "user",
             "content": "Now, about this following query, does the user identify any authors?"},
            {"role": "user",
             "content": "Please respond only with the author's name"},
            {"role": "user",
             "content": "Please respond with 'Unspecified' if the user does not specify an author."},
            {"role": "user",
             "content": "Please base your answer only on the provided query and nothing else!"},
            {"role": "user",
             "content": "Here is the Query: " + query},
        ],
        temperature=0
    )
    return chat_completion.choices[0].message.content

####################################################################################
# Use OpenAI to parse the Query and extract Genre from provided list               #
####################################################################################

categories = ['Cookbooks', 'Fiction', 'Classics', 'Nonfiction', 'Humor', 'Horror', 'Fantasy', 'Novels', 'Biography', 'Literary Fiction', 'Mystery Thriller', 'Historical', 'Historical Fiction', 'Contemporary Romance', 'Food']
categories_str = "'Cookbooks', 'Fiction', 'Classics', 'Nonfiction', 'Humor', 'Horror', 'Fantasy', 'Novels', 'Biography', 'Literary Fiction', 'Mystery Thriller', 'Historical', 'Historical Fiction', 'Contemporary Romance', 'Food', 'Unspecified' "

def getGenre(query: str) -> str:
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant and you give a single answer. People generally ask about text and books."},
            {"role": "user",
             "content": "Now, about this following query, provide which of the following categories the user asks about."},
            {"role": "user",
             "content": "Please respond only with one of the following categories: "+categories_str},
            {"role": "user",
             "content": "Please base your answer only on the provided query and nothing else!"},
            {"role": "user",
             "content": "Here is the Query:" + query},
        ],
        temperature=0
    )
    for category in categories:
        if chat_completion.choices[0].message.content.find(category) > -1:
            return category
    return "Unspecified"


####################################################################################
# Use OpenAI to select one of the provided books matching the Query                #
####################################################################################
def selectBook(books: [], query: str):
    example_content = "Provide most relevant title based on the following texts about a book for kids: " + """[
        {
            "text": "The Forest Feast for Kids includes the most kid-friendly vegetarian favorites from Erin Gleeson",
            "title": "The Forest Feast"
        },
        {
            "text": "Foods I would love to try but I am pretty sure the kids i know wouldn't eat most of these.",
            "title": "Funcy Meals"
        },
        {
            "text": "A beginner can start with something as simple as beverages before moving into knives and heating units.",
            "title": "Learning to Cook"
        },
        {
            "text": "A triple murder in a Moscow amusement center: three corpses found frozen in the snow, faces and fingers missing.",
            "title": "Gorgy Park"
        },
    ]"""
    example_response = "The Forest Feast is a good book for kids."
    content = "["
    for book in books:
        content = content + "\n    {\n    \"text\": \"" + book['content'] + "\"\n    \"title\": \"" + book['title'] + "\"\n    },"
    content = content + "\n]"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant and you give a single answer. People generally ask about text and books."},
            {"role": "user", "content": example_content},
            {"role": "assistant", "content": example_response},
            {"role": "user",
             "content": "Provide most relevant title and author based on the following texts about " + query + " and explain why this is a good choice for the user: " + content}
        ],
        temperature=0
    )
    return chat_completion

####################################################################################
# Use OpenAI check if the selected book is a good match to the Query               #
####################################################################################
def checkRecomendation(title, author, query: str, content):
    chat_completion = openai.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a bookstore assistant and people ask you to verify that the book they have selected fits their expectations."},
            {"role": "user", "content": query},
            {"role": "user", "content": "I selected the book \""+title+"\" by \""+author+"\" based on the following review: "+content},
            {"role": "user",
             "content": "Dear assistant answer with 'yes' or 'no', is the above book a good recommendation for me?"},
        ],
        temperature=0,
        timeout=10,
    )
    return chat_completion
