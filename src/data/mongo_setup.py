# import mongoengine

# def global_init():
#     mongoengine.register_connection(alias='core', db='snake_bnb',name='snake_bnb')

from mongoengine import connect


def global_init():
    DB_URI = "mongodb+srv://abhishek_sah:supremeXavi1@cluster0-23kyk.mongodb.net/snake_bnb?retryWrites=true&w=majority"

    connect(host=DB_URI)
