import requests


class TwitchAPI:

    def __init__(self, clientId: str, client_secret: str):
        self.headers = None
        self.client_id = clientId
        self.client_secret = client_secret

    def auth(self):
        bearer = self.__fetch_token()
        self.headers = {
            'Authorization': f'Bearer {bearer}',
            'Client-Id': self.client_id,
        }
        return self

    def __fetch_token(self) -> str:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = f'client_id={self.client_id}&client_secret={self.client_secret}&grant_type=client_credentials'

        try:
            response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:  # TODO: throw specific exception
            raise SystemExit(err)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)

        return response.json()['access_token']

    def get_twitch_clips(self,
                         game_id=None,
                         broadcaster_name=None,
                         clip_id=None,
                         started_at=None,
                         ended_at=None,
                         cursor=None,
                         clips_per_page=None):
        url = 'https://api.twitch.tv/helix/clips'
        params = {}
        if game_id is not None:
            params['game_id'] = game_id
        elif broadcaster_name is not None:
            params['broadcaster_id'] = self.get_twitch_user_id_by_login_name(broadcaster_name)
        elif clip_id is not None:
            params['id'] = clip_id
        else:
            raise SystemExit("One must be present")
        if started_at is not None:
            params['started_at'] = started_at.isoformat('T') + "Z"
        if ended_at is not None:
            params['ended_at'] = ended_at.isoformat('T') + "Z"
        if cursor is not None:
            params['after'] = cursor
        if clips_per_page is not None:
            params['first'] = clips_per_page
        return requests.get(url, params=params, headers=self.headers)

    def get_twitch_video(self, video_id=None):
        url = 'https://api.twitch.tv/helix/videos'
        return requests.get(url, params={'id': video_id}, headers=self.headers).json()['data'][0]

    def get_twitch_user_id_by_login_name(self, broadcaster_name):
        url = 'https://api.twitch.tv/helix/users'
        return requests.get(url, params={'login': broadcaster_name}, headers=self.headers).json()['data']['id']

    def get_twitch_game_id_by_game_name(self, game_name):
        url = 'https://api.twitch.tv/helix/games'
        try:
            return requests.get(url, params={'name': game_name}, headers=self.headers).json()['data'][0]["id"]
        except:  # TODO: throw specific exception
            raise SystemExit()
