# WCS

## Introduction
Warcraft: Source is a modification for Counter-Strike: Source and Counter-Strike: Global Offensive running on [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python). It changes the gameplay, where each player have a race with unique skills and abilities to that specific race, as well as having a shop to further change the playing field.

* The official Source.Python forum thread can be found [here](https://forums.sourcepython.com/viewtopic.php?f=7&t=1925).
* The official website can be found [here](http://warcraft-source.com/board/).
* The content repository can be found [here](https://github.com/ThaPwned/WCS-Contents).


## Installation
1. Install Source.Python by following the guide [here](http://wiki.sourcepython.com/general/installation.html).
2. Download and extract Warcraft: Source in your server's game folder.
3. Write `sp plugin load wcs` in the `cfg/autoexec.cfg` file (create it if it doesn't exist).
4. The necessary files will be created on the first load under `cfg/source-python/wcs/`.

If you're going to use races or items from 0.77 (and prior) or 0.78, you also have to install [EventScripts Emulator](https://github.com/Ayuto/EventScripts-Emulator). This have to be loaded before WCS, otherwise your races and items will not be loaded.


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

## Troubleshooting
If you encounter any of the following exceptions this may save you a bit of time figuring out what's wrong. If you encounter issues not listed below, feel free to make an issue [here](https://github.com/ThaPwned/WCS/issues) or post it on the [thread](https://forums.sourcepython.com/viewtopic.php?f=7&t=1925).


#### json.decoder.JSONDecodeError: Expecting value: line 2 column 17 (char 18)
It can mean you're missing a double quote (`"`) or some value in one of your JSON files on line 2 at character position 18. Example:
```json
{
    "username": "a,
    "password": null,
    "access_token": "",
    "repositories": []
}
```

#### json.decoder.JSONDecodeError: Expecting ',' delimiter: line 3 column 5 (char 27)
It means you're missing a delimiter (in this case, it's a comma (`,`)) in one of your JSON files on line 3 at character position 27 (for this, check the prior line as well and see if there's a missing delimiter). Example:
```json
{
    "username": null
    "password": null,
    "access_token": "",
    "repositories": []
}
```

#### json.decoder.JSONDecodeError: Expecting ':' delimiter: line 2 column 16 (char 17)
It means you're missing a delimiter (in this case, it's a colon (`:`)) in one of your JSON files on line 2 at character position 17. Example:
```json
{
    "username" null,
    "password": null,
    "access_token": "",
    "repositories": []
}
```

#### json.decoder.JSONDecodeError: Expecting ',' delimiter: line 5 column 28 (char 137)
It means you're missing a delimiter (in this case, it's a comma (`,`)) in one of your JSON files on line 5 at character position 137. Example:
```json
{
    "username": null,
    "password": null,
    "access_token": "",
    "repositories": ["one" "two"]
}
```

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

## Understanding the races' config.json file
`config.json` is the main configuration file for races, where you can make the race suit your server preferences. Below is the most basic `config.json` file with standard values:
```json
{
    "required": 0,
    "maximum": 0,
    "restrictbot": 0,
    "restrictmap": [],
    "restrictitem": [],
    "restrictweapon": [],
    "restrictteam": 0,
    "teamlimit": 0,
    "author": "",
    "allowonly": [],
    "skills": {}
}
```
* `required` is the minimum global level required before you can use this race.
* `maximum` is the maximum level you can get on this race (you can still play it, just not gain any more levels on it). If this value is set to `0`, there's no maximum level.
* `restrictbot` prevents bots from using this race if it is set to `1`.
* `restrictmap` contains a list of maps this race is unable to be used on. If the value is `[]`, it can be played on all maps.
* `restrictitem` contains a list of items this race is unable to purchase and use. If the value is `[]`, all items are purchasable and usable.
* `restrictweapon` contains a list of weapons this race is unable to use. If the value is `[]`, all weapons are usable.
* `restrictteam` is the team this race can be used on. If the value is set to `0`, any team can use it.
* `teamlimit` is the maximum total allowed players on each team that can use this race. If the value is `0`, there's no team limit.
* `author` is the person who have made this race.
* `allowonly` is a list containing steamids of players (or `ADMIN` for wcsadmins or `VIP` for VIP players) who's allowed to use this race. If the value is `[]`, all players can use it.
* `skills` is a dict containing all the skills and skill configurations. If the value is `{}`, the race will have no skills.

Skills can then be added under a `skills` key using the following format:
```json
        "skill name": {
            "event": "",
            "required": 0,
            "cooldown": 0,
            "variables": {
                "variable name": [0]
            }
        }
```

* `skill name` have to be an all-lowercase value with spaces replaced with an underscore (`_`).
* `event` is the event of which the skill is executed. It can be any of the available [events](#available-events). Races written in new style Python do not required this key, and can set the event directly in the skill.
* `required` is the minimum race level required before the skill can be leveled.
* `cooldown` is only available for skills with the event `player_ability` and `player_ultimate` (`player_ultimate` will be removed in a future release, so best to use `player_ability`). It can be a single value or a list. If it is a list, try to make sure it matches with the other lists for this skill.
* `variables` is for unique variables the skill uses, so we'll have to take a look at its keys instead.
* `variable name` is the name of the unique variable the skill uses, and that variable's values. It must be a list containing the values, and the length of the list is the skill's maximum level, so try to make all the lists for this skill the same.

A race can also depend on certain things for different games, that may not be available in all games (eg. game models). This is primarily used for effect models, as they may not be available in the supported games. The format is as follows:
```json
    "games": {
        "game name": {
            "identifier": ""
        }
    }
```
* `games` is just to show this is for game specific elements.
* `game name` is the game name (or `default` for the default behavior).
* `identifier` is a unique name for this key, and are used by the race. The value of this key is just the prefered value used by this game.

To further make a race unique, there can then be added effects under the `effects` key (these are to implemented by the race to function). The format looks like this (note: As there's many types of effects and different keys to set for each type of effect, this is only a rough example on how it can look):
```json
    "effects": {
        "identifier": {
            "type": "effect type",
            "args": {
                "key": 0,
            }
        }
    }
```
* `effects` is just to show this is used for effects.
* `identifier` is a unique name for this key, so the race can reference to it.
* `type` is the effect type used and varies greatly in what they do.
* `args` contains the key and values that the effect `type` requires.
* `key` is the key that should be set on this specific effect `type`. The value of this key is the value that is set (note: Certain keys that requires a string value can reference back to game specific values using the following format: `$games.GAME_NAME.key`).

To sum things up, using a simplified version of Human Alliance as an example, it'll look like this:
```json
{
    "required": 0,
    "maximum": 0,
    "restrictmap": [],
    "restrictitem": [],
    "restrictweapon": [],
    "restrictteam": 0,
    "teamlimit": 0,
    "author": "Tha Pwned (original: Kryptonite)",
    "allowonly": [],
    "skills": {
        "teleport": {
            "required": 8,
            "cooldown": [10, 9, 8, 7, 6, 5, 4, 3],
            "variables": {
                "range": [600, 660, 720, 780, 840, 920, 1000, 1000]
            }
        }
    },
    "games": {
        "default": {
            "spawncmd_model": "sprites/cbbl_smoke.vmt"
        }
    },
    "effects": {
        "spawncmd": {
            "type": "effect10",
            "args": {
                "halo": "$games.GAME_NAME.spawncmd_model",
                "model": "$games.GAME_NAME.spawncmd_model",
                "center": null,
                "start_radius": null,
                "end_radius": null,
                "life_time": 1.5,
                "start_width": 10,
                "end_width": 10,
                "fade_length": 10,
                "amplitude": 0,
                "red": 255,
                "green": 255,
                "blue": 255,
                "alpha": 255,
                "speed": null
            }
        }
    }
}
```

## Understanding the items' config.json file
`config.json` is the main configuration file for items, where you can make the item suit your server preferences. Below is the most basic `config.json` file with standard values:
```json
{
    "cost": 0,
    "required": 0,
    "dab": 0,
    "duration": 0,
    "count": 0,
    "event": ""
}

```
* `cost` is the price of the item.
* `required` is the minimum total required level before you can purchase the item.
* `dab` (or Dead Alive Both) is the player state that's required before they can purchase it. If the value is set to `0`, `1` or `2`, it defines the behavior as alive players, dead players or either, respectively.
* `duration` is for how long the player should keep the item. If the value is set to `0` or `1`, it defines the behavior as a single round or until death, respectively.
* `count` is the maximum amount purchasable of the item.
* `event` is the event of which the item is executed. It can be any of the available [events](#available-events).

### Available events
Global events:
* pre_player_attacker
* player_attacker
* player_death
* pre_player_hurt
* player_hurt
* player_kill
* player_say
* player_spawn
* post_player_spawn
* pre_player_victim
* player_victim
