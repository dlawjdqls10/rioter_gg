from django.shortcuts import render
import pickle
import pickle
from pprint import pprint
from scipy.spatial import distance
import numpy as np
import requests
import json
import operator
import requests
import json

api_key = "RGAPI-5d4d9788-7f08-485b-86de-c8528dc9baac"


# Create your views here.



def index(request):

    return render(request, 'index.html')

#--------------------------------------------------------------------------------------#



#---------------------------------------------------------------------------------------#



def recommend(request):

    with open('CHALLENGER_LANE.pickle', 'rb') as f:
        challenger_lane = pickle.load(f)

    with open('CHALLENGER_time_vector.pickle', 'rb') as f:
        challenger_time_vector = pickle.load(f)

    with open('PointsDic_CG_1.pickle', 'rb') as f:
        pointsdic_cg = pickle.load(f)

    with open('win_rate_fake.pickle', 'rb') as f:
        winrate_dict = pickle.load(f)

    challenger_lane_dict = { }

    for x in challenger_lane:
        challenger_lane_dict[list(x.keys())[0]] = list(x.values())[0]

    def get_champion_json():

        api_data = requests.get("http://ddragon.leagueoflegends.com/cdn/9.10.1/data/ko_KR/champion.json")

        json_data1 = json.loads(api_data.content.decode("utf-8"))

        champions_info = list(json_data1.values())[3]
        champions_list = list(champions_info.values())
        champion_dict = {}
        en_champion_dict = {}

        for champion in champions_list:
            champion_dict[champion['key']] = champion['name']
            en_champion_dict[champion['key']] = champion['id']

        return [champion_dict, en_champion_dict]

    def get_account_id(summoner_name):

        api_data = requests.get(
            "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{0}?api_key={1}".format(summoner_name,
                                                                                                    api_key))
        json_data2 = json.loads(api_data.content.decode("utf-8"))

        return json_data2['accountId']

    def get_summoner_name(account_id):

        api_data = requests.get(
            "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-account/{0}?api_key={1}".format(account_id,
                                                                                                       api_key))

        json_data3 = json.loads(api_data.content.decode("utf-8"))
        return json_data3['name']

    def find_line(entered_id):
        scores = []
        lines = []
        for key, value in challenger_lane_dict[entered_id].items():
            scores.append(value)
            lines.append(key)

        return lines[scores.index(max(scores))]

    def champ_masteries(entered_id):
        scores = []
        champions = []
        for key, value in pointsdic_cg[entered_id].items():
            scores.append(value)
            champions.append(key)

        return champions[scores.index(max(scores))]

    def duo_line(line):
        if line == "TOP":
            return "JUNGLE"
        elif line == "MID":
            return "JUNGLE"
        elif line == "JUNGLE":
            return "MID"
        elif line == "DUO_CARRY":
            return "DUO_SUPPORT"
        elif line == "DUO_SUPPORT":
            return "DUO_CARRY"
        else:
            return "JUNGLE"

    def line_matching_users(wanted_line):
        users = []
        for acc_key in challenger_lane_dict.keys():
            if find_line(acc_key) == wanted_line:
                users.append(acc_key)
            else:
                pass
        return (users)

    def calculate_euc_dic(entered_id):
        candidates_of_line = line_matching_users(duo_line(find_line(entered_id)))
        euc_dic = {}
        for candidate in candidates_of_line:
            euc_dic[candidate] = distance.euclidean(challenger_time_vector[entered_id],
                                                    challenger_time_vector[candidate]) / np.sqrt(
                len(challenger_time_vector[entered_id]))

        return euc_dic

    def select_duo(entered_id):
        acc_ids = []
        euc_dic = calculate_euc_dic(entered_id)
        for x in list(sorted(euc_dic.items(), key=operator.itemgetter(1), reverse=True))[:3]:
            acc_ids.append(x[0])
        return acc_ids


    # 챔피언 Id를 챔피언 Name으로 바꿔주는 함수 --> 숙련도로 챔피언 뽑아왔을 때 Id로 나오기 때문에 이를 Name으로 바꿔줘야 image를 불러올 수 있다
    champ_dict, en_champ_dict = get_champion_json()
    entered_summoner_name = request.POST.get('summoner_name')
    entered_id = get_account_id(entered_summoner_name)

    my_line = find_line(entered_id)
    print(f"\n        소환사님의 주 포지션 : {my_line}")
    duo_ids = select_duo(entered_id)

    duo_infos = [[], [], []]

    for i, duo_id in enumerate(duo_ids):
        duo_name = get_summoner_name(duo_id)
        duo_line = find_line(duo_id)
        duo_champ = champ_masteries(duo_id)
        champ_en_name = en_champ_dict[str(duo_champ)]
        duo_champ_img = "http://ddragon.leagueoflegends.com/cdn/9.8.1/img/champion/{0}.png".format(champ_en_name)
        duo_infos[i].append(duo_name)
        duo_infos[i].append(duo_line)
        duo_infos[i].append(champ_dict[str(duo_champ)])
        duo_infos[i].append(duo_champ_img)
        duo_infos[i].append(winrate_dict[duo_id])

    context = {
        "Summoner_name" : entered_summoner_name,
        "My_line" : my_line,
        "Duo1" : duo_infos[0],
        "Duo2" : duo_infos[1],
        "Duo3" : duo_infos[2],
    }

    return render(request, 'recommend.html', context=context)



import requests
from PIL import Image
from io import BytesIO
import json

api_key = "RGAPI-5d4d9788-7f08-485b-86de-c8528dc9baac"


# 현영이 api_key

