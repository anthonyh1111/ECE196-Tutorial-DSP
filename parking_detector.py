"""
VL53L1X Smart Parking Spot Detector

What this does:
1. Reads distance data from the ESP32 over USB serial.
2. Rejects bad readings and sudden one-sample spikes.
3. Uses a median filter to reduce noise.
4. Uses an exponential moving average to smooth the signal.
5. Uses debounce logic so a passing car/person does not instantly trigger "occupied".
6. Uses separate occupied/empty thresholds to prevent flickering.

Install:
    pip install pyserial

Run:
    python parking_detector.py --port /dev/cu.usbserial-0001

On Windows, your port may look like:
    COM3

On macOS, your port may look like:
    /dev/cu.usbserial-0001
    /dev/cu.SLAB_USBtoUART
    /dev/cu.usbmodemXXXX
"""

import argparse
import statistics
import time
from collections import deque

import serial


class ParkingDetector:
    def __init__(
        self,
        occupied_threshold_mm=900,
        empty_threshold_mm=1100,
        min_valid_mm=40,
        max_valid_mm=4000,
        median_window=5,
        ema_alpha=0.25,
        outlier_jump_mm=500,
        occupied_confirm_time=2.0,
        empty_confirm_time=3.0,
    ):
        """
        occupied_threshold_mm:
            If filtered distance is below this value, something is close enough
            to possibly be a parked car.

        empty_threshold_mm:
            If filtered distance is above this value, the spot is likely empty.
            This should be larger than occupied_threshold_mm to avoid flicker.

        occupied_confirm_time:
            Distance must stay below occupied_threshold_mm for this long before
            the program says "OCCUPIED". This rejects cars/people passing by.

        empty_confirm_time:
            Distance must stay above empty_threshold_mm for this long before
            the program says "EMPTY". Usually slightly longer for stability.
        """
        self.occupied_threshold_mm = occupied_threshold_mm
        self.empty_threshold_mm = empty_threshold_mm
        self.min_valid_mm = min_valid_mm
        self.max_valid_mm = max_valid_mm
        self.median_window = median_window
        self.ema_alpha = ema_alpha
        self.outlier_jump_mm = outlier_jump_mm
        self.occupied_confirm_time = occupied_confirm_time
        self.empty_confirm_time = empty_confirm_time

        self.recent = deque(maxlen=median_window)
        self.ema = None
        self.last_good = None

        self.state = "UNKNOWN"
        self.candidate_state = None
        self.candidate_since = None

    def valid_reading(self, distance_mm):
        """Reject impossible readings."""
        return self.min_valid_mm <= distance_mm <= self.max_valid_mm

    def reject_outlier(self, distance_mm):
        """
        Reject sudden one-sample jumps.

        Example:
        If normal distance is around 1500 mm and one reading suddenly says
        200 mm, that may be a person/object passing by or a bad sample.
        """
        if self.last_good is None:
            return True

        jump = abs(distance_mm - self.last_good)
        return jump <= self.outlier_jump_mm

    def filter_distance(self, raw_distance_mm):
        """
        Returns filtered distance, or None if this reading should be ignored.
        """
        if not self.valid_reading(raw_distance_mm):
            return None

        if not self.reject_outlier(raw_distance_mm):
            return None

        self.last_good = raw_distance_mm
        self.recent.append(raw_distance_mm)

        median_value = statistics.median(self.recent)

        if self.ema is None:
            self.ema = median_value
        else:
            self.ema = self.ema_alpha * median_value + (1 - self.ema_alpha) * self.ema

        return self.ema

    def raw_decision(self, filtered_distance_mm):
        """
        Uses hysteresis:
        - Below occupied threshold -> possible occupied
        - Above empty threshold -> possible empty
        - Between thresholds -> keep previous state
        """
        if filtered_distance_mm < self.occupied_threshold_mm:
            return "OCCUPIED"

        if filtered_distance_mm > self.empty_threshold_mm:
            return "EMPTY"

        return self.state

    def update_state(self, filtered_distance_mm):
        """
        Debounce the decision so short disturbances do not change state.
        """
        now = time.time()
        decision = self.raw_decision(filtered_distance_mm)

        if decision == self.state:
            self.candidate_state = None
            self.candidate_since = None
            return self.state

        if decision != self.candidate_state:
            self.candidate_state = decision
            self.candidate_since = now
            return self.state

        required_time = (
            self.occupied_confirm_time
            if decision == "OCCUPIED"
            else self.empty_confirm_time
        )

        if now - self.candidate_since >= required_time:
            self.state = decision
            self.candidate_state = None
            self.candidate_since = None

        return self.state

    def process(self, raw_distance_mm):
        """
        Main function:
        raw distance in -> filtered distance and parking state out.
        """
        filtered = self.filter_distance(raw_distance_mm)

        if filtered is None:
            return None, self.state

        state = self.update_state(filtered)
        return filtered, state


def parse_serial_line(line):
    """
    Arduino sends either:
        1234
    or:
        ERR

    This function converts valid numeric lines to int.
    """
    line = line.strip()

    if not line:
        return None

    try:
        return int(line)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port, example: COM3 or /dev/cu.usbserial-0001")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--occupied-threshold", type=int, default=900, help="Distance below this means possible car")
    parser.add_argument("--empty-threshold", type=int, default=1100, help="Distance above this means likely empty")
    args = parser.parse_args()

    detector = ParkingDetector(
        occupied_threshold_mm=args.occupied_threshold,
        empty_threshold_mm=args.empty_threshold,
    )

    print("Opening serial port...")
    print(f"Port: {args.port}")
    print(f"Baud: {args.baud}")
    print()
    print("Press Ctrl+C to stop.")
    print()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        time.sleep(2)  # ESP32 may reset when serial opens

        while True:
            raw_bytes = ser.readline()
            line = raw_bytes.decode(errors="ignore")
            raw_distance = parse_serial_line(line)

            if raw_distance is None:
                continue

            filtered_distance, state = detector.process(raw_distance)

            if filtered_distance is None:
                print(f"Raw: {raw_distance:4d} mm | ignored outlier/bad reading | State: {state}")
            else:
                print(
                    f"Raw: {raw_distance:4d} mm | "
                    f"Filtered: {filtered_distance:7.1f} mm | "
                    f"State: {state}"
                )


if __name__ == "__main__":
    main()