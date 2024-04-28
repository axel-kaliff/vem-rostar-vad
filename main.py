# script for making get requests to the API
# and saving the data to a csv file
#%%
import requests
import json
from enum import Enum

class Utformat(Enum):
    HTML = 'HTML'
    JSON = 'JSON'
    XML = 'XML'
    CSV = 'CSV'
    EMPTY = ''

class Gruppering(Enum):
    PARTI = 'parti'
    VOTERING = 'votering'
    BESLUT = 'beslut'
    VOTE = 'vote'
    DECISION = 'decision'
    EMPTY = ''

class Rost(Enum):
    JA = 'Ja'
    NEJ = 'Nej'
    AVSTÅR = 'Avstår'
    FRÅNVARANDE = 'Frånvarande'
    EMPTY = ''

class Source(Enum):
    VOTERINGSLISTA = 'voteringlista'
    DOKUMENTLISTA = 'dokumentlista'

class PartyColor(Enum):
    S = '#E43235' # red
    M = '#52BDEC' # blue
    SD = '#DDDD00' # yellow
    C = '#3D8238' 
    V = '#DF0D69' 
    KD = '#000077'
    L = '#006AB3'
    MP = '#92BD2F'
    FI = '#000000'
    ÖVR = '#808080'
    EMPTY = ''

def get_url(source):
    url = 'https://data.riksdagen.se/' + source.value + '/?'
    return url[:-1]

def make_request(url, params):
    response = requests.get(url, params=params)
    data = response.json()
    return data

def form_params(utformat, gruppering, rost):
    params = {}
    params['utformat'] = utformat.value
    params['gruppering'] = gruppering.value
    params['rost'] = rost.value
    params['sz'] = '500'
    params['iid'] = ''
    params['punkt'] = ''
    params['valkrets'] = ''
    params['bet'] = ''
    return params


def get_data():
    params = form_params(Utformat.JSON, Gruppering.EMPTY, Rost.EMPTY)
    url = get_url(Source.VOTERINGSLISTA)
    data = make_request(url, params)
    return data

def save_data(data):
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def get_party_votes(data):
    vote_counts = {}
    party_votes = {}

    for vote in data['voteringlista']['votering']:
        votering_id = vote['votering_id']
        rost = vote['rost']
        parti = vote['parti']

        if votering_id not in vote_counts:
            vote_counts[votering_id] = {'Ja': 0, 'Nej': 0, 'Avstår': 0, 'Frånvarande': 0}

        vote_counts[votering_id][rost] += 1

        if votering_id not in party_votes:
            party_votes[votering_id] = {}

        if parti not in party_votes[votering_id]:
            party_votes[votering_id][parti] = {'Ja': 0, 'Nej': 0, 'Avstår': 0, 'Frånvarande': 0}

        party_votes[votering_id][parti][rost] += 1

    return party_votes

def get_party_percentages_single_instance(party_votes, votering_id):
    total_votes = {'Ja': 0, 'Nej': 0, 'Avstår': 0, 'Frånvarande': 0}
    for parti in party_votes[votering_id]:
        for rost in party_votes[votering_id][parti]:
            total_votes[rost] += party_votes[votering_id][parti][rost]

    party_percentages = {}
    for rost in total_votes:
        party_percentages[rost] = {}
        for parti in party_votes[votering_id]:
            if total_votes[rost] == 0:
                party_percentages[rost][parti] = 0
            else:
                party_percentages[rost][parti] = party_votes[votering_id][parti][rost] / total_votes[rost]

    return party_percentages

# TODO get information about the votering
def get_votering(votering_id):
    params = form_params(Utformat.JSON, Gruppering.VOTERING, Rost.EMPTY)
    params['votering_id'] = votering_id
    url = get_url(Source.VOTERINGSLISTA)
    data = make_request(url, params)
    return data
#%%

data = get_data()
save_data(data)

party_votes = get_party_votes(data)

import pandas as pd
import matplotlib.pyplot as plt

#%%
for votering_id in party_votes:

    # plot votes
    df = pd.DataFrame.from_dict(party_votes[votering_id])
    df.rename(columns={'-': 'ÖVR'}, inplace=True)

    df.plot(kind='bar', stacked=True, color=[PartyColor[party].value for party in df.columns])
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.title(votering_id)
    plt.show()

    #%%
    # get data about the votering
    votering = get_votering(votering_id)
    print(votering)
    #%%
    

    # plot percentages
    party_percentages = get_party_percentages_single_instance(party_votes, votering_id)
    df = pd.DataFrame.from_dict(party_percentages)
    df = df.transpose()
    df.rename(columns={'-': 'ÖVR'}, inplace=True)
    df.plot(kind='bar', stacked=True, color=[PartyColor[party].value for party in df.columns])
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.title(votering_id)
    plt.show()

    #%%



