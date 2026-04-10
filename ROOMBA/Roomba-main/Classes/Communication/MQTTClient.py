import paho.mqtt.client as mqtt
from Core.CleaningModule import CleaningModule


class MQTTClient:
    """Represents the MQTT client used for robot communication."""

    def __init__(self, cleaning_module: CleaningModule, broker_address: str = "localhost", port: int = 1883, topic_command: str = "roomba/command") -> None:
        self._cleaning_module = cleaning_module
        self._broker_address = broker_address
        self._port = port
        self._topic_command = topic_command
        self._client = mqtt.Client(protocol=mqtt.MQTTv311)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def connect(self) -> bool:
        """Connect to the MQTT broker and start listening."""
        try:
            self._client.connect(self._broker_address, self._port, keepalive=60)
            self._client.loop_start()
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._client.loop_stop()
        self._client.disconnect()

    def subscribe(self) -> bool:
        """Subscribe to the command topic."""
        try:
            self._client.subscribe(self._topic_command)
            return True
        except Exception as e:
            print(f"Failed to subscribe: {e}")
            return False

    def publish_command(self, command: str) -> bool:
        """Publish a command message to the command topic."""
        try:
            self._client.publish(self._topic_command, command)
            return True
        except Exception as e:
            print(f"Failed to publish command: {e}")
            return False

    def handleCommand(self, command: str) -> None:
        """Handle incoming command. If 'start', trigger cleaning."""
        command = command.strip().lower()
        if command == "start":
            self._cleaning_module.startCleaning()

    def _on_connect(self, client, userdata, flags, rc) -> None:
        """MQTT callback: triggered when broker connection established."""
        if rc == 0:
            print("MQTT connected.")
            self.subscribe()
        else:
            print(f"Failed to connect, return code {rc}")

    def _on_message(self, client, userdata, msg) -> None:
        """MQTT callback: triggered when message received."""
        command = msg.payload.decode().strip()
        print(f"MQTT received command: {command}")
        self.handleCommand(command)