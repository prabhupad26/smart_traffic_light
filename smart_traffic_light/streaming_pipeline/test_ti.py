import threading as th
import time


class TrafficInspector:
    final_dict = {}
    ttl_sim_time = 60
    check_traffic = False
    lock = th.Lock()
    instances = set()

    def __init__(self, stl_name, signal_value, time_remaining=30, terminate=False):
        self.stl_name = stl_name
        self.signal_value = signal_value
        self.time_remaining = time_remaining
        self.default_time = time_remaining
        self._terminate = terminate
        self.sim_counter = 0
        self.timer_adjustment = 10
        if self not in TrafficInspector.instances:
            TrafficInspector.instances.add(self)

    def run(self):
        while True:
            print(f"Time remaining for {self.stl_name} is : {self.time_remaining}")
            if self.time_remaining >= 1:
                time.sleep(1)
            else:
                self.get_traffic_details()
            # check traffic
            self.time_remaining -= 1

            self.update_results()

            if self.sim_counter >= TrafficInspector.ttl_sim_time:
                break

    def update_results(self):
        if self.sim_counter < TrafficInspector.ttl_sim_time:
            TrafficInspector.final_dict[self.sim_counter][self.stl_name] = {
                "status": self.signal_value,
                "time_remaining": self.time_remaining}
        self.sim_counter += 1

    def get_traffic_details(self):
        # add safety
        self.time_remaining = self.default_time - self.timer_adjustment
        if self.signal_value == 'green':
            self.signal_value = "red"
        else:
            self.signal_value = "green"


if __name__ == '__main__':
    ttl_timer = 60
    lane_1 = "stl_1"
    lane_2 = "stl_2"

    TrafficInspector.final_dict = {i: {lane_1: {}, lane_2: {}} for i in range(ttl_timer+1)}

    ti_lane1 = TrafficInspector("stl_1", "green")
    ti_lane2 = TrafficInspector("stl_2", "red")

    th1 = th.Thread(target=ti_lane1.run)
    th2 = th.Thread(target=ti_lane2.run)

    th1.start()
    th2.start()

    threads = [th1, th2]

    for thread in threads:
        thread.join()

    print(TrafficInspector.final_dict)

