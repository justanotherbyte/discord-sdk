import json

a = {'version': 1, 'type': 2, 'token': 'aW50ZXJhY3Rpb246ODg4NDkzNDE5ODU1NDk1MTc4OlJtV1JEQVN4NFZpdUdDcDkwQkc4UjhydW5tNWF2bDVsZkVDV3BwbHZVVHVHMkgxdkVHckNmWHIwTjVnbEdnOGQ2VnVJOWpSVEZLUnYyTHFlRFJVQ0VuS1ZVc0Z0UlhQUWVzR0I3VXpPanMxTEZxQkpuQ2g1SE9uejBGZUNaVTVJ', 'member': {'user': {'username': 'moanie', 'public_flags': 256, 'id': '691406006277898302', 'discriminator': '9112', 'avatar': 'c54cb7a881281bacd407825a5ff8972d'}, 'roles': ['888088444306354227'], 'premium_since': None, 'permissions': '1099511627775', 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2021-09-16T18:34:46.780000+00:00', 'is_pending': False, 'deaf': False, 'avatar': None}, 'id': '888493419855495178', 'guild_id': '888086119693033493', 'data': {'type': 1, 'name': 'tanjiro', 'id': '888485056094548008'}, 'channel_id': '888086120171180095', 'application_id': '856587279690891265'}



with open("debug.json", "w") as f:
    json.dump(a, f, indent = 4)