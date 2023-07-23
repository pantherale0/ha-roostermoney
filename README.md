# Natwest Rooster Money

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

Integration to integrate with Natwest Rooster Money.

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show basic info from the family account and all child accounts.
`calendar` | Shows a calendar of previous and current jobs for each child account.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `rooster_money`.
1. Download _all_ the files from the `custom_components/rooster_money/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Natwest Rooster Money"

## Configuration is done in the UI

<!---->

## Future plans
- Add `switch` platform to allow approving jobs for a child
- Listen to events raised by `pyroostermoney`
- Service call to add / remove money from a pot
- Service call for advanced job actions (skip etc.)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-roostermoney.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-roostermoney/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-roostermoney.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-roostermoney.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-roostermoney/releases
