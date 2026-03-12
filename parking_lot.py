from datetime import datetime
from enum import Enum


# ---------------- ENUMS ---------------- #

class VehicleType(Enum):
    BIKE = 1
    CAR = 2
    TRUCK = 3


class TicketStatus(Enum):
    DUE = 1
    PAID = 2


class SpotType(Enum):
    BIKE = 1
    COMPACT = 2
    LARGE = 3


# ---------------- VEHICLE ---------------- #

class VehicleDetail:

    def __init__(self, number_plate: str, vehicle_type: VehicleType):
        self.number_plate = number_plate
        self.vehicle_type = vehicle_type

    def __str__(self):
        return f"{self.number_plate} ({self.vehicle_type.name})"


# ---------------- PARKING SPOT ---------------- #

class ParkingSpot:

    def __init__(self, spot_id: int, spot_type: SpotType):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.vehicle = None

    def is_spot_available(self):
        return self.vehicle is None

    def park_vehicle(self, vehicle: VehicleDetail):

        if not self.is_spot_available():
            raise Exception(f"Spot {self.spot_id} is already occupied.")

        self.vehicle = vehicle

    def vacant_spot(self):

        if self.vehicle is None:
            raise Exception("Spot already empty.")

        vehicle = self.vehicle
        self.vehicle = None

        return f"{vehicle} removed from spot {self.spot_id}"


# ---------------- PARKING FLOOR ---------------- #

class ParkingFloor:

    def __init__(self, floor_id: int):
        self.floor_id = floor_id
        self.spots = []

    def add_spot(self, spot: ParkingSpot):
        self.spots.append(spot)

    def get_free_spot(self, vehicle_type: VehicleType):

        for spot in self.spots:
            if spot.is_spot_available() and self._can_fit(vehicle_type, spot.spot_type):
                return spot

        return None

    def _can_fit(self, vehicle_type, spot_type):

        mapping = {
            VehicleType.BIKE: [SpotType.BIKE, SpotType.COMPACT, SpotType.LARGE],
            VehicleType.CAR: [SpotType.COMPACT, SpotType.LARGE],
            VehicleType.TRUCK: [SpotType.LARGE],
        }

        return spot_type in mapping[vehicle_type]


# ---------------- TICKET ---------------- #

class Ticket:

    def __init__(self, ticket_id: int, vehicle: VehicleDetail, spot: ParkingSpot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time = None
        self.status = TicketStatus.DUE

    def close_ticket(self):
        self.exit_time = datetime.now()
        self.status = TicketStatus.PAID
    
    def calculate_fee(self):

        if not self.exit_time:
            raise Exception("Vehicle not exited yet")

        duration = self.exit_time - self.entry_time
        hours = duration.total_seconds() / 3600

        rate_per_hour = {
            VehicleType.BIKE: 10,
            VehicleType.CAR: 20,
            VehicleType.TRUCK: 30
        }

        return round(hours * rate_per_hour[self.vehicle.vehicle_type], 2)


# ---------------- PARKING LOT ---------------- #

class ParkingLot:

    def __init__(self):
        self.floors = []
        self.active_tickets = {}
        self.ticket_counter = 1

    def add_floor(self, floor: ParkingFloor):
        self.floors.append(floor)

    def park_vehicle(self, vehicle: VehicleDetail):

        for floor in self.floors:

            spot = floor.get_free_spot(vehicle.vehicle_type)

            if spot:
                spot.park_vehicle(vehicle)

                ticket = Ticket(
                    self.ticket_counter,
                    vehicle,
                    spot
                )

                self.active_tickets[self.ticket_counter] = ticket
                self.ticket_counter += 1

                print(
                    f"Vehicle {vehicle} parked at "
                    f"Spot {spot.spot_id} on Floor {floor.floor_id}"
                )

                return ticket

        raise Exception("Parking Lot Full")

    def exit_vehicle(self, ticket_id: int):

        ticket = self.active_tickets.get(ticket_id)

        if not ticket:
            raise Exception("Invalid Ticket")

        print(ticket.spot.vacant_spot())

        ticket.close_ticket()
        print(ticket.calculate_fee())

        del self.active_tickets[ticket_id]

        print(f"Ticket {ticket_id} closed.")

        return ticket


# ---------------- DEMO ---------------- #

def main():

    parking_lot = ParkingLot()

    # Create floor
    floor1 = ParkingFloor(1)

    # Add spots
    floor1.add_spot(ParkingSpot(1, SpotType.BIKE))
    floor1.add_spot(ParkingSpot(2, SpotType.COMPACT))
    floor1.add_spot(ParkingSpot(3, SpotType.LARGE))

    parking_lot.add_floor(floor1)

    # Create vehicle
    vehicle = VehicleDetail("KA01AB1234", VehicleType.CAR)

    # Park vehicle
    ticket = parking_lot.park_vehicle(vehicle)

    print("Ticket ID:", ticket.ticket_id)

    # Exit vehicle
    input("\nPress Enter to simulate exit...\n")
    parking_lot.exit_vehicle(ticket.ticket_id)


if __name__ == "__main__":
    main()