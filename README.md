# Enhanced Keyboard Remote for AppDaemon

An AppDaemon app that **enhances** the functionality of the Home Assistant [Keyboard Remote](https://www.home-assistant.io/integrations/keyboard_remote) integration by adding the following features:

- Maps key codes to your own logical name for that key. So instead of referring to a key as (for example) `110` in your automations and scripts, you could refer to it as `play`.
- Adds support for long press versions of every key, effectively doubling the number of keys on your remote/keyboard.

A great use case for this app is utilizating a USB RF remote control as a universal remote.

## Prerequisites

- [Home Assistant](https://www.home-assistant.io/)
- [AppDaemon](https://community.home-assistant.io/t/home-assistant-community-add-on-appdaemon-4/163259). A Home Assistant addon that runs this app.
- [Keyboard Remote](https://www.home-assistant.io/integrations/keyboard_remote). The Home Assistant integration that this app enhances.

## Installation

After installing all prerequisites, and confirming they work, you can install this app using one of two methods.

### HACS Installation

The preferred method for installing is with [HACS](https://hacs.xyz/).

### Manual Installation

Alternatively, you can download the contents of the `enhanced_keyboard_remote` directory from the apps directory to your local AppDaemon apps directory.

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
`config` | False | array | [] | A list of one or more device configurations. Each configuration should represent one keyboard/remote. If you only have a single device, for simplicity you can omit the `device_name` / `device_descriptor` keys below.
`config[].device_name` | True | array | [] | An optional list of device names this config must match, allowing support for multiple keyboard/remotes. The values would be the same values used in your `Keyboard Remote` configuration in `configuration.yaml`.<br><br>If omited (and `config[].device_descriptor` is omitted), the first config in `config[]` will always be chosen.
`config[].device_descriptor` | True | array | [] | An optional list of device descriptors this config must match. Follows the same rules as `config[].device_name`.
`config[].keys` | False | map | {} | A map of key codes to configuration.
`config[].keys.name` | False | string | | The logical name of the key. This will show up as `key_name` in the event. For long presses, the `key_name` will show up with the suffix `-long` (e.g. play-long).
`config[].keys.repeat` | True | bool | false | An optional flag indicating key hold repeats should be sent. This means a new event will be generated repeatedly as long as the key is held. Useful for functions such as brightness level or volume.

Simple example:
```yaml
enhanced_keyboard_remote:
  module: enhanced_keyboard_remote
  class: EnhancedKeyboardRemote
  config:
    - keys:
        116:
          name: power
          repeat: single
        115:
          name: volume_up
          repeat: true
        114:
          name: volume_down
          repeat: true
```

A simple automation using the above example for a short and long version of volume up might looks like this:

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