---
layout: post
title: How to Get Team Fortress 2 Item Store Prices Using the Steam API
date: 2016-02-27 04:04:28 +0100
---

I'm currently working on a webapp related to TF2 trading. It displays prices in various currencies, ingame and real world ones. As a link between the two economies I'm using the [Mann Co. Supply Crate Key], which is the standard ingame currency for higher value items. Because of constantly changing exchange rates its price can't be hardcoded without becoming inaccurate every week. Reading source code of [OPTF2] and [Steamodd] I figured out the API endpoint they use is called `ISteamEconomy/GetAssetPrices`. It requires an appid parameter, for TF2 that's 440. The full url looks like this:

    https://api.steampowered.com/ISteamEconomy/GetAssetPrices/v1/?format=json&appid=440&key=YOUR_API_KEY

The result contains an object for each item with a few attributes, we'll focus on name and prices. Name seems to always be the defindex, so you can use that if you're too lazy to deal with the class properties. Prices has pairs of currency and price. You need to divide the price by 100 to get the real value, for example `"EUR": 220` means 220 / 100 = 2.20€. There isn't really much more to say about this, if you're confused about defindexes check out the [WebAPI wiki page], especially [GetSchema].

[Mann Co. Supply Crate Key]: https://wiki.teamfortress.com/wiki/Mann_Co._Supply_Crate_Key
[OPTF2]: http://optf2.com/
[Steamodd]: https://github.com/Lagg/steamodd
[WebAPI wiki page]: https://wiki.teamfortress.com/wiki/WebAPI
[GetSchema]: https://wiki.teamfortress.com/wiki/WebAPI

