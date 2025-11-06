ALTER TABLE RouteStops ADD COLUMN booking_id INT NULL;
ALTER TABLE RouteStops ADD CONSTRAINT fk_stop_booking FOREIGN KEY (booking_id) REFERENCES ServiceBookings(booking_id);