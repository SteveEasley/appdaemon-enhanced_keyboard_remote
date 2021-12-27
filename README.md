# Enhanced Keyboard Remote

An AppDaemon app that **enhances** the functionality of the Home Assistant [Keyboard Remote](https://www.home-assistant.io/integrations/keyboard_remote) integration by adding the following features:

- Maps key codes to your own logical name for that key. So instead of referring to a key as (for example) `110` in your automations and scripts, you could refer to it as `play`.
- Adds support for long press versions of every key, effectively doubling the number of keys on your remote/keyboard.

A great use case for this app is utilizating a USB RF remote control as a universal remote.

## Prerequisites

- [Home Assistant](https://www.home-assistant.io/)
- [AppDaemon](https://community.home-assistant.io/t/home-assistant-community-add-on-appdaemon-4/163259). A Home Assistant addon that runs this app.
- [Keyboard Remote](https://www.home-assistant.io/integrations/keyboard_remote). The Home Assistant integration that this app enhances. See the Keyboard Remote integration setup section below.

## Installation

After installing all prerequisites, and confirming they work, you can install this app using one of two methods.

### HACS Installation

The preferred method for installing is with [HACS: Home Assistant Community Store](https://hacs.xyz/). To add with HACS you just need to add this app's github repository to your list of custom HACS repositories.

1. Install HACS into Home Assistant if you haven't already done so.
1. Ensure HACS has AppDaemon apps support enabled (its disabled by default). See https://hacs.xyz/docs/categories/appdaemon_apps.
1. Add this app's repository to your HACS Custom Repository list. See https://hacs.xyz/docs/faq/custom_repositories. For the custom repository URL use https://github.com/SteveEasley/appdaemon-enhanced_keyboard_remote, and for Category use AppDaemon.
1. The installation will put the app in your Home Assistant `config/appdaemon/apps` directory.

### Manual Installation

Alternatively, you can download the contents of the [enhanced_keyboard_remote](https://github.com/SteveEasley/appdaemon-enhanced_keyboard_remote/tree/main/apps/enhanced_keyboard_remote) directory from the apps directory to your local Home Assistant `config/appdaemon/apps`.

## Usage

The app works by listening to events the [Keyboard Remote](https://www.home-assistant.io/integrations/keyboard_remote) integration generates. Those events are picked up by this app and matched against the Configuration documented below. A match will generate a new event called `enhanced_keyboard_remote_command_received`, which will contain the same event data as the original Keyboard Remote event, as well as two new parameters:

Name | Example | Description
-- | -- | --
`key_name` | play | The logical name of the key (which you define)
`key_alt` | short | One of `short` or `long`

Example `enhanced_keyboard_remote_command_received` event:

```yaml
key_name: play
key_alt: long
key_code: 107,
type: key_hold,
device_descriptor: /dev/input/event3
device_name: USB Composite Device Keyboard
```

## Configuration

To configure the app, add a new configuration section to `config/appdaemon/apps/apps.yaml`.

```yaml
enhanced_keyboard_remote:
  module: enhanced_keyboard_remote
  class: EnhancedKeyboardRemote
  config:
    - keys:
       ... 
```

Key | Optional | Type | Default | Description
-- | -- | -- | -- | --
`module` | False | string | | The module name of the app (must be `enhanced_keyboard_remote`).
`class` | False | string | | The name of the Class (must be `EnhancedKeyboardRemote`).
`description` | False | string | | A description for the app.
`config` | False | array | [] | A list of one or more device configurations. Each configuration should represent one keyboard/remote. If you only have a single device, for simplicity you can omit the `device_name` / `device_descriptor` keys below.
`config[].device_name` | True | array | [] | An optional list of device names this config must match, allowing support for multiple keyboard/remotes. The values would be the same values used in your `Keyboard Remote` configuration in `configuration.yaml`.<br><br>If omitted (and `config[].device_descriptor` is omitted), the first config in `config[]` will always be chosen.
`config[].device_descriptor` | True | array | [] | An optional list of device descriptors this config must match. Follows the same rules as `config[].device_name`.
`config[].keys` | False | map | {} | A map of key codes to configuration.
`config[].keys.name` | False | string | | The logical name of the key. This will show up as `key_name` in the event.
`config[].keys.repeat` | True | bool | false | An optional flag indicating key hold repeats should be sent. This means a new event will be generated repeatedly as long as the key is held. Useful for functions such as brightness level or volume.

Simple example:
```yaml
enhanced_keyboard_remote:
  module: enhanced_keyboard_remote
  class: EnhancedKeyboardRemote
  description: Enhanced Keyboard Remote
  config:
    - keys:
        116:
          name: power
        115:
          name: volume_up
          repeat: true
        114:
          name: volume_down
          repeat: true
```

### Keyboard Remote integration setup

Its important you have the `Keyboard Remote` configuration in Home Assistant setup correctly for this app to work properly. Namely, for long key presses to be detected `key_hold` events must be enabled.

Example `/config/configuration.yaml` config:

```yaml
keyboard_remote:
  - device_name: USB Composite Device Keyboard
    type:
      - key_up
    emulate_key_hold: true
    emulate_key_hold_delay: 0.5
    emulate_key_hold_repeat: 0.2
```

> Note: Its import to use `key_up` and not `key_down`, otherwise there would be no way to provide a distinct short and long press.

> Note: I recommend not using the type `key_hold` even if your USB device sends them. Using the emulated hold gives you control over the hold timings, which you dont get if you use the native type. In the example config above I am saying I dont want a key press to be a long press till its held for 0.5 seconds, then repeat 5 times a seconds.

## Automation Example

A simple automation to bring all this home. This uses the above example for a short and long version of volume up:

```yaml
- alias: unversal_remote_volume_up_slow
  trigger:
    - platform: event
      event_type: enhanced_keyboard_remote_command_received
      event_data:
        key_name: volume_up
        key_alt: short
  action:
    # slow volume up

- alias: unversal_remote_volume_up_fast
  trigger:
    - platform: event
      event_type: enhanced_keyboard_remote_command_received
      event_data:
        key_name: volume_up
        key_alt: long
  action:
    # fast volume up
```
