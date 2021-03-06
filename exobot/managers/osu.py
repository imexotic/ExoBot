import aiohttp
from exobot.models.osu import User



# NOTE: Simple Osu API wrapper
#       Change CLIENT_ID and CLIENT_SECRET in exobot/config/.env


class Osu():

    def __init__(self, client_id, client_secret):
        if not client_id or not client_secret:
            raise Exception('Set your CLIENT_ID and CLIENT_SECRET in exobot/config/.env')

        self.API_URL = 'https://osu.ppy.sh/api/v2'
        self.TOKEN_URL = 'https://osu.ppy.sh/oauth/token'
        self._client_id = client_id
        self._client_secret = client_secret


    @staticmethod
    def clean_data(data):

        if (isinstance(data, list)):
            return [Osu.clean_data(d) for d in data]
        elif (isinstance(data, dict)):
            return {key: Osu.clean_data(value) for key, value in data.items() if value is not None}

        return data


    async def get_token(self, scope = 'public'):
        data = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials',
            'scope': scope
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.TOKEN_URL, data=data) as response:
                results = await response.json()

                return results['access_token']


    async def _get_data(self, url):
        token = await self.get_token()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    results = await response.json()
                    data = self.clean_data(results)

                    return data
                  
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))


    async def get_user(self, user_id):
        return User(
            await self._get_data(f'{self.API_URL}/users/{user_id}'),
        )