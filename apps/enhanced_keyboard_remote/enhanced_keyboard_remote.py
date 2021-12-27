import appdaemon.plugins.hass.hassapi as hass

IN_EVENT_NAME = "keyboard_remote_command_received"
OUT_EVENT_NAME = "enhanced_keyboard_remote_command_received"


class EnhancedKeyboardRemote(hass.Hass):
    def initialize(self):
        self.listen_event(self.key_press, IN_EVENT_NAME)
        self.config = self.args["config"]
        self.key_alt = "short"
        self.key_count = 0

    def key_press(self, event, data, kwargs):
        config = self.get_config(data)

        if config is None:
            return
        
        if data["key_code"] not in config["keys"]:
            return

        if data["type"] == "key_up":
            if self.key_alt == "short":
                self.key_count = 1
                self.send(config, data, "short", self.key_count)
            self.key_alt = "short"
            self.key_count = 0

        elif data["type"] == "key_hold":
            self.key_alt = "long"
            self.key_count = self.key_count + 1
            self.send(config, data, "long", self.key_count)
    
    def get_config(self, data):
        if "device_name" not in self.config[0] and "device_descriptor" not in self.config[0]:
            return self.config[0]

        for config in self.config:
            for param in ["device_name", "device_descriptor"]:
                if param in config and data[param] in config[param]:
                    return config

    def send(self, config, data, key_alt, key_count):
        key = config["keys"][data["key_code"]]

        if key_alt == "long":
            if "repeat" in key and not key["repeat"] and key_count > 1:
                return

        del data["metadata"]
        data.update({
            "key_name": key["name"],
            "key_alt": key_alt,
            "key_count": key_count
        })

        self.fire_event(OUT_EVENT_NAME, **data)

        self.log(data)
