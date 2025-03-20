from django.shortcuts import get_object_or_404
from typing import List
from ninja import NinjaAPI
from ninja import Field, ModelSchema
from ninja.security import APIKeyHeader
import os
from .models import Card, Game, GameLog, GamePlayer, GamePlayerImpendingWithEnergy, Presence, Spirit

api = NinjaAPI()

class SpiritSchema(ModelSchema):
    class Config:
        model = Spirit
        model_fields = ['id', 'name']

class CardSchema(ModelSchema):
    class Config:
        model = Card
        model_fields = ['id', 'name']

class ImpendingSchema(ModelSchema):
    card: CardSchema = None
    class Config:
        model = GamePlayerImpendingWithEnergy
        model_fields = ['energy', 'in_play', 'this_turn']

class PresenceSchema(ModelSchema):
    class Config:
        model = Presence
        model_fields = ['opacity', 'energy', 'elements']

class GamePlayerSchema(ModelSchema):
    spirit: SpiritSchema = None
    hand: List[CardSchema] = []
    discard: List[CardSchema] = []
    play: List[CardSchema] = []
    selection: List[CardSchema] = []
    days: List[CardSchema] = []
    healing: List[CardSchema] = []
    impending: List[ImpendingSchema] = Field([], alias="gameplayerimpendingwithenergy_set")
    presence: List[PresenceSchema] = Field([], alias="presence_set")
    class Config:
        model = GamePlayer
        model_fields = [
                'name', 'ready', 'paid_this_turn', 'gained_this_turn', 'energy', 'color', 'aspect',
                'temporary_sun', 'temporary_moon', 'temporary_fire', 'temporary_air', 'temporary_water', 'temporary_earth', 'temporary_plant', 'temporary_animal',
                'permanent_sun', 'permanent_moon', 'permanent_fire', 'permanent_air', 'permanent_water', 'permanent_earth', 'permanent_plant', 'permanent_animal',
                'spirit_specific_resource', 'spirit_specific_per_turn_flags',
                ]

class GameSchema(ModelSchema):
    class Config:
        model = Game
        model_fields = ['id', 'name', 'discord_channel', 'scenario']

class GameDetailSchema(ModelSchema):
    players: List[GamePlayerSchema] = Field([], alias="gameplayer_set")
    minor_deck: List[CardSchema] = []
    major_deck: List[CardSchema] = []
    discard_pile: List[CardSchema] = []
    class Config:
        model = Game
        # we've not exported the screenshots, because it's not obvious how we would do it.
        model_fields = ['id', 'name', 'discord_channel', 'scenario']

class GameLogSchema(ModelSchema):
    class Config:
        model = GameLog
        model_fields = ['id', 'date', 'text', 'images']

def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META["HTTP_X_FORWARDED_FOR"]
    else:
        return request.META["REMOTE_ADDR"]

class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"
    def authenticate(self, request, key):
        secret = os.getenv('CUSTOM_API_KEY', None)
        if secret is None:
            return False
        if key == secret:
            return key

header_key = ApiKey()

def ip_whitelist(request):
    ip = str(os.getenv('OWN_IP', '127.0.0.1'))
    if get_ip(request) == ip:
        return ip

@api.get("/ip", auth=ip_whitelist)
def ip(request):
    return f"Authenticated client, IP = {request.auth}"

@api.post("/game/{game_id}/link/{channel_id}", auth=[ip_whitelist, header_key])
def game_link(request, game_id, channel_id):
    game = get_object_or_404(Game, pk=game_id)
    Game.objects.filter(discord_channel=channel_id).update(discord_channel='')
    game.discord_channel = channel_id
    game.save()
    return "ok"

@api.get("/game", response=List[GameSchema])
def game(request):
    return Game.objects.all()

@api.get("/game/{game_id}", response=GameDetailSchema)
def game(request, game_id):
    return get_object_or_404(Game, pk=game_id)

@api.get("/game/{game_id}/log", response=List[GameLogSchema])
def gamelogs(request, game_id, after: int = None):
    game = get_object_or_404(Game, pk=game_id)
    if after is None:
        return game.gamelog_set.all()
    else:
        return game.gamelog_set.filter(pk__gt=after)
