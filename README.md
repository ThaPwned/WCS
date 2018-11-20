# WCS

## Introduction
Warcraft: Source is a modification for Counter-Strike: Source and Counter-Strike: Global Offensive running on [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python). It changes the gameplay, where each player have a race with unique skills and abilities to that specific race, as well as having a shop to further change the playing field.

* The official website can be found [here](http://warcraft-source.com/board/).
* The content repository can be found [here](https://github.com/ThaPwned/WCS-Contents).


## Installation
1. Install Source.Python by following the guide [here](http://wiki.sourcepython.com/general/installation.html).
2. Download and extract Warcraft: Source in your server's game folder.
3. Write `sp plugin load wcs` in the `cfg/autoexec.cfg` file (create it if it doesn't exist).
4. The necessary files will be created on the first load under `cfg/source-python/wcs/`.


## Administrator
You can make yourself an administrator by editing `cfg/source-python/wcs/privileges.json` and adding your steamid there. By default, it'll look like this:
```json
{
    "players": {
        "dummy": {
            "wcsadmin": 1,
            "wcsadmin_githubaccess": 1,
            "wcsadmin_managementaccess": 1,
            "wcsadmin_playersmanagement": 1,
            "wcsadmin_raceaccess": 1,
            "vip_raceaccess": 1
        }
    }
}
```
Replace `dummy` with your steamid to gain full access.

### A breakdown of what each privilege is and what it does:
* `wcsadmin`: If this is set to `1`, it allows the player to open the wcsadmin menu.
* `wcsadmin_githubaccess`: If this is set to `1`, it allows the player to install races and items directly on the server (learn more of how this is done [here](#github-management)).
* `wcsadmin_managementaccess`: If this is set to `1`, it allows the player to manage the `races.json` file. You can change the order and if it's loaded or not.
* `wcsadmin_playersmanagement`: If this is set to `1`, it allows the player to give xp/levels to the other players.
* `wcsadmin_raceaccess`: If this is set to `1`, it allows the player access to any race with the `ADMIN` tag in the race's `allowonly` key.
* `vip_raceaccess`: If this is set to `1`, it does the same as with `wcsadmin_raceaccess` above except it uses the `VIP` tag instead.

## Adding new style races and items
Races and items are located in the folders `wcs/modules/races` and `wcs/modules/items` if they're written using Source.Python (the `config.json` and `strings.ini` files are _always_ located here). Races and items, which are written in either ESS or ESP, are located under `es_emulator/eventscripts/wcs/modules/races` and `es_emulator/eventscripts/wcs/modules/items`.
If the race or item you want on your server is available on the [content repository](https://github.com/ThaPwned/WCS-Contents), you have the option to install it directly from your server. To set this up, just follow the [guide below](#github-management).
If you add the race or item directly (without using Github), you also have to add them to either `races.json` or `items.json` located in `cfg/source-python/wcs/`. By default, it'll look like this (this is the `races.json` file but it looks like the `items.json` file except it has `items` instead of `races`):
```json
{
    "categories": {},
    "races": []
}
```
To add it directly to the menu, simply add it to the `races` (or `items` for items) key. If you want to add it to a category, add the category (if it's not already present) in the `categories` key with the race or item name as a sub-key. Below is an example for adding both Undead Scourge and Human Alliance:
```json
{
    "categories": {
        "standard": [
            "undead_scourge",
            "human_alliance"
        ]
    },
    "races": [
        "undead_scourge",
        "human_alliance"
    ]
}
```
As they were added in a new category, you also have to edit `resource/source-python/translations/wcs/categories_strings_server.ini`, and add the translated category:
```ini
[standard]
    en = "Standard"
```

## Adding old style races and items
* WCS 0.78 (often referred to as `ini-style`): Are located in the files `cfg/source-python/wcs/races.ini` and `cfg/source-python/wcs/items.ini`.
* WCS 0.77 and prior (often referred to as `keygroup-style`): Are located in the files `cfg/source-python/wcs/es_WCSraces_db.txt` and `cfg/source-python/wcs/es_WCSshop_db.txt`.

Note: If you're using races or items from 0.78 or 0.77 and prior, it's a good idea to also get the `strings.ini` (from 0.78) or `es_WCSlanguage_db.txt` (from 0.77 and prior) as well (should be placed in the `cfg/source-python/wcs/` folder), as you can run into the possibility of the messages not being translated properly.
Items from 0.77 and prior will also need the `es_WCSshop_cat_db.txt` file (should be placed in the `cfg/source-python/wcs/` folder), as you won't be able to use categories otherwise.

## Github Management
Warcraft: Source allows you to install certain races and items (which can be found on the [content repository](https://github.com/ThaPwned/WCS-Contents)) directly on the server with a simple click. To enable this, you have to install [PyGithub](https://github.com/PyGithub/PyGithub) and all of its dependencies. Once you've installed PyGithub properly, you can start using the functionality. However, as there's a limit ([60 for unauthenticated and 5000 for authenticated](https://developer.github.com/v3/#rate-limiting)) to the amount of requests, that gets reset once an hour, it is therefore recommended to use it while being authenticated. To do so, you'll have to edit `cfg/source-python/wcs/github.json`. By default, it'll look like this:
```json
{
    "username": null,
    "password": null,
    "access_token": null,
    "repositories": []
}
```
You can use either `username` and `password` or `access_token` to enable the Github functionality. Either method requires you to have a Github account. Your `username` and `password` is just the username and password you use to login to Github. To generate an access token, while being logged in on your Github account, go to **`Settings -> Developer settings -> Personal access tokens`**. From there, you press **`Generate new token`**. Give the token a description, so you can remember what it's used for. You then enable `public_repo` and press the green `Generate token` at the bottom. Copy your newly created token in the `access_token` key. Once you've done one of these steps, it'd look something like this (note the single quotes around the newly added text):
```json
{
    "username": "myusername",
    "password": "mypassword",
    "access_token": "1q2w3e4r5tfaketoken6y7u8i9o0p",
    "repositories": []
}
```
When you have done this, add yourself as an wcsadmin by enabling the `wcsadmin` and `wcsadmin_githubaccess` privileges. Restart the server, and you should have access to it.
`repositories` is used if you have a separate repository with races or items you want to use together with the default. As an example on how to add repositories, we use the default one, which is located at github.com/ThaPwned/WCS-Contents:
```json
    "repositories": ["ThaPwned/WCS-Contents"]
```
And that is it. If you were to add multiple repositories, remember to add a comma (`,`) after each new repository you're going to add except the last one:
```json
    "repositories": ["ThaPwned/WCS-Contents", "MyImaginary/Repository", "NotRealRepository/Hopefully"]
```
