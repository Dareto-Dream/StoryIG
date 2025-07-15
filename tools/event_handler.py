class EventHandler:
    def __init__(self, events, conductor=None):
        """
        events: List of [timestamp_ms, [[type, param1, param2], ...]]
        conductor: Optional reference for triggering engine actions.
        """
        self.events = sorted(events, key=lambda e: e[0])
        self.event_index = 0
        self.conductor = conductor

    def update(self, song_time):
        """
        Triggers all events whose timestamp has passed since last update.
        """
        while (self.event_index < len(self.events) and
               song_time >= self.events[self.event_index][0]):
            timestamp, event_list = self.events[self.event_index]
            for event in event_list:
                self.handle_event(event, timestamp)
            self.event_index += 1

    def handle_event(self, event, timestamp):
        event_type = event[0]
        if event_type == "Change Scroll Speed":
            speed = float(event[1])
            lane = int(event[2]) if event[2] else None
            print(f"[EVENT] Change Scroll Speed to {speed} (lane {lane})")
            if self.conductor:
                self.conductor.set_scroll_speed(speed, lane)
        elif event_type == "vid":
            vid_path = event[1] or "assets/video/default.mp4"
            print(f"[EVENT] Play video: {vid_path}")
            if self.conductor:
                self.conductor.play_video(vid_path)
        else:
            print(f"[EVENT] Unknown event: {event}")

    def reset(self):
        self.event_index = 0
