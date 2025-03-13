# Descenders Modkit

[![Release ModLoaderSolution](https://github.com/nohumanman/descenders-modkit/actions/workflows/dotnet-release.yml/badge.svg)](https://github.com/nohumanman/descenders-modkit/actions/workflows/dotnet-release.yml)
[![License: GPL v3][gpg-license-svg-url]][gpg-license-url]

[python-application-svg-url]: https://github.com/nohumanman/descenders-modkit/actions/workflows/python-app.yml/badge.svg 
[python-application-url]: https://github.com/nohumanman/descenders-modkit/actions/workflows/python-app.yml/badge.svg 
[gpg-license-svg-url]: https://img.shields.io/badge/License-GPLv3-blue.svg
[gpg-license-url]: https://www.gnu.org/licenses/gpl-3.0


> Scripts for modding Descenders and a split timer system

A Modkit for the game Descenders that accurately records and displays split times for a track, display on leaderboard, as well as many other [quality of life improvements]().

## Installation

### For players
**To load the Descenders Modkit onto your map** (without adding scripts into unity)

- Open a [map that loads the Descenders Modkit](#implementations)
- Leave the map back to the mod menu
- Open your map
- The Modkit should be loaded

Once you open a map that loads the modkit, the **modkit is loaded for the rest of the time your game is open** (most features are disabled in career). The **Modkit will completely unload when you quit the game**, it used to load forever but [this caused issues for some players](https://discord.com/channels/336514640202956800/373438418044190737/1085152905511845930). Any problems let me know.

### For modders
- Download the latest [Descenders Modding Toolkit Release](https://github.com/nohumanman/descenders-split-timer/releases/tag/main-release)
- or [Download Assets Directly](/unity-project/Assets/)

Please [see the wiki]() for information on how to use features in this toolkit.

### For contributors
Please refer to the [Contributor's Guide]() that contains information about system architecture, containers, deployment.

## Implementations
- **[Igloo Bike Park](https://mod.io/g/descenders/m/igloo-bike-park)** by *[antgrass](https://mod.io/g/descenders/u/antgrass)*
- **[Montcerf](https://mod.io/g/descenders/m/montcerf)** by *[antgrass](https://mod.io/g/descenders/u/antgrass)*
- **[Hedgecock](https://mod.io/g/descenders/m/hedgecock)** by *[antgrass](https://mod.io/g/descenders/u/antgrass)*
- **[4x Dobrany](https://mod.io/g/descenders/m/4x-dobrany)** by *[BBB1711](https://mod.io/g/descenders/u/bbb1711)*
- **[Snowbird Island](https://mod.io/g/descenders/m/snowbird-island)** by *[antgrass](https://mod.io/g/descenders/u/antgrass)*
- **[MTB Paradise](https://mod.io/g/descenders/m/mtb-paradise)** by *[KAMUS](https://mod.io/g/descenders/u/kamus)*
- **[Red Bull Hardline 2021](https://mod.io/g/descenders/m/rbhl21)** by *[
BI0S0CK](https://mod.io/g/descenders/u/bi0s0ck)*
- **[MTR BMX Track](https://mod.io/g/descenders/m/mtr-bmx-track)** by *[dragonkiller37](https://mod.io/g/descenders/u/dragonkiller37)*
- **[Fort William 4x](https://mod.io/g/descenders/m/fort-william-4x)** by *[BBB171](https://mod.io/g/descenders/u/bbb1711)*
- **[50to01 Line](https://mod.io/g/descenders/m/50to01-line)** by *[antgrass](https://mod.io/g/descenders/u/antgrass)*
- **[Alpine DH](https://mod.io/g/descenders/m/alpine-dh)** by *[flysix](https://mod.io/g/descenders/u/flysix)*
- **[Dyfi Bikepark](https://mod.io/g/descenders/m/dyfi-bikepark)** by *[wiking2888](https://mod.io/g/descenders/u/wiking2888)*
- **[BC Bikepark](https://mod.io/g/descenders/m/bc-bikepark)** by *[linus1005](https://mod.io/g/descenders/u/linus1005)*

Some maps don't have timers and only use the modkit for features it provides (e.g. bike switcher).

## Contributor Guide
### Systems Architecture
<img src="docs/assets/system-architecture.svg">

