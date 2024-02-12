##################################################################################################
###                                                                                            ###
###                                 DropTracker Event Bot                                      ###
###                                     + Quart API                                            ###
###                           This bot was written by @joelhalen                               ###
###                                     joelhalen.net                                          ###
###                              https://www.droptracker.io                                    ###
###                                                                                            ###
###                             Copyright DropTracker.io 2024                                  ###
###                                 All Rights Reserved.                                       ###
###                                                                                            ###
###     Please maintain the above copyright notice in redistributions or modifications.        ###
##################################################################################################
import interactions
import ssl
import aiohttp
import yaml
from hypercorn import Config
from hypercorn.asyncio import serve
from interactions import Overwrite, Permissions, GuildMember, ComponentType
from interactions.ext.tasks import IntervalTrigger, create_task

import json
from datetime import datetime
import asyncio

from quart import Quart, jsonify, url_for, session, redirect, render_template, request, send_from_directory

from authlib.integrations.httpx_client import AsyncOAuth2Client

from utils.db.database import Database
from utils.fs.FileSystemSessionInterface import FileSystemSessionInterface
from utils.fs.logging import this_logger

with open('cfg/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
    bot_token = config['bot_token']

intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.ALL
bot = interactions.Client(token=bot_token,
                          intents=intents)
# Attach database class
database = Database()

def create_app(bot):
    # Creates the web server app while passing the
    # bot instance to the routes
    app = Quart(__name__)
    app.config['SESSION_FILE_DIR'] = 'K:/data/sessions'
    app.config['SESSION_COOKIE_DOMAIN'] = '.droptracker.io'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    ## Initialize the database
    database.init_database()

    app.session_interface = FileSystemSessionInterface(app.config['SESSION_FILE_DIR'])
    #Blueprints for listeners later
    #app.register_blueprint(routes_blueprint, url_prefix='/')
    #app.register_blueprint(api_blueprint, url_prefix='/api')

    return app


app = create_app(bot)
app.secret_key = '1234!!5678@@'
# secret_key is not actually used for anything


@app.template_filter('length')
def length_filter(s):
    return len(s)


app.jinja_env.filters['length'] = length_filter


## on_ready event for Discord bot

@bot.event
async def on_ready():
    this_logger(f"Logged in as {bot.me.name} with ID: {bot.me.id}", "debug")
    await bot.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(name=f"events.droptracker.io",
                                              type=interactions.PresenceActivityType.WATCHING)
            ]
        )
    )

## QUART APP ENDPOINTS


@app.route('/')
async def index_page():
    user = session.get('user', None)
    return await render_template('index.html',
                                 user=user)

@app.route('/img/<path:filename>')
async def serve_img(filename):
    return await send_from_directory('static/img', filename)


@app.errorhandler(404)
async def page_not_found(e):
    user = session.get('user', None)
    return await render_template('errors/404.html',
                                 user=user)


@app.errorhandler(500)
async def internal_error(e):
    user = session.get('user', None)
    return await render_template('errors/500.html',
                                 user=user)


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/certificate.crt',
                            'ssl/private.key')

config = Config()
config.bind = ["0.0.0.0:3845"]
config.ssl = ssl_context

loop = asyncio.get_event_loop()
loop.create_task(serve(app, config))
loop.run_until_complete(bot.start())
bot.start()
