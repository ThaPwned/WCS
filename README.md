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
* `wcsadmin_raceaccess`: If this is set to `1`, it allows the player access to any race with the `ADMIN` tag in the race's `allowonly` key.
* `vip_raceaccess`: If this is set to `1`, it does the same as with `wcsadmin_raceaccess` above except it uses the `VIP` tag instead.


## Github Management
Warcraft: Source allows you to install certain races and items (which can be found on the [content repository](https://github.com/ThaPwned/WCS-Contents)) directly on the server with a simple click. To enable this, you first have to install [PyGithub](https://github.com/PyGithub/PyGithub) and all of its dependencies. After that, you'll have to edit `cfg/source-python/wcs/github.json`. By default, it'll look like this:
```json
{
    "access_token": null,
    "repositories": []
}
```
As of right now, you can only install races and items by using the official repository, so you can ignore the `repositories` key for now. Getting an `access_token` requires you to have a Github account. To generate one, while being logged in on your Github account, go to **`Settings -> Developer settings -> Personal access tokens`**. From there, you press **`Generate new token`**. Give the token a description, so you can remember what it's used for. You then enable `public_repo` and press the green `Generate token` at the bottom. Copy your newly created token in the `access_token` key. Once you've done this, it'd look something like this (note the single quotes around the token):
```json
{
    "access_token": "1q2w3e4r5tfaketoken6y7u8i9o0p",
    "repositories": []
}
```
When you have done this, add yourself as an wcsadmin by enabling the `wcsadmin` and `wcsadmin_githubaccess` privileges. Restart the server, and you should have access to it.
