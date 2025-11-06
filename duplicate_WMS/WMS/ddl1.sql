-- Select the database to use
USE wms_db;

-- -----------------------------------------------------
-- 1. Insert Roles
-- -----------------------------------------------------
INSERT INTO `Roles` (`role_name`) VALUES
('Administrator'),
('Supervisor'),
('Driver'),
('Client');
-- (These will get role_ids 1, 2, 3, 4 respectively)

-- -----------------------------------------------------
-- 2. Insert Users
-- NOTE: Passwords should be hashed using a strong algorithm
-- (like bcrypt) in your application.
-- 'hashed_password_placeholder' is used here for demonstration.
-- -----------------------------------------------------
INSERT INTO `Users` (`role_id`, `first_name`, `last_name`, `email`, `password_hash`, `phone`)
VALUES
(1, 'Admin', 'User', 'admin124@gmail.com', '$2b$12$n5AVjuVWpagrK0nQi1mm5OBs6DewbSoX5Cj3hoWoJ8L5QIEhjgdeq', '9000000001'),
(2, 'Supriya', 'Patel', 'supriya.pathrik12@gmail.com', '$2b$12$CdPC88JP6jaX7dWen1TdDOZ7Qn6NVXOTq8pMxzoLRMB9xokCyuiGK', '9000000002'),
(3, 'Vijay', 'Kumar', 'vijay.kumar78k@gmail.com', '$2b$12$BiV3HUd2Psk9aY.cAfO.GunWRv1RW9Rjg.rWqECuqV0GNrU2TkMsC', '9000000003'),
(4, 'Ananya', 'Rao', 'ananya.rao5@67@gmail.com', '$2b$12$d6Kfz.vrvBNK99YIihDuTOUjBohZyXNOfx1Iw5zapznfkQxNNZXSK', '9000000004');
-- (These will get user_ids 1, 2, 3, 4 respectively)

-- -----------------------------------------------------
-- 3. Insert Vehicles
-- Assign vehicle 'TS09A1234' to our driver Vijay (user_id 3)
-- -----------------------------------------------------
INSERT INTO `Vehicles` (`license_plate`, `model`, `capacity_kg`, `current_driver_id`)
VALUES
('TS09A1234', 'Tata Ace', 750.00, 3),
('TS09B5678', 'Mahindra Bolero', 1000.00, NULL);
-- (These will get vehicle_ids 1, 2)

-- -----------------------------------------------------
-- 4. Insert Routes
-- Create a route by our supervisor Supriya (user_id 2)
-- -----------------------------------------------------
INSERT INTO `Routes` (`route_name`, `created_by_supervisor_id`)
VALUES
('Morning Route - Sector A', 2);
-- (This will get route_id 1)

-- -----------------------------------------------------
-- 5. Insert Collection Points
-- Create a few general points and one for our client Ananya (user_id 4)
-- -----------------------------------------------------
INSERT INTO `CollectionPoints` (`point_name`, `address`, `latitude`, `longitude`, `client_id`)
VALUES
('Sector A - Community Bin 1', 'Near Sector A Park', 17.4435, 78.3838, NULL),
('Sector A - Community Bin 2', 'Street 5, Sector A', 17.4442, 78.3850, NULL),
('Ananya Rao Residence', 'B-12, Sector B, Hitech City', 17.4500, 78.3900, 4);
-- (These will get point_ids 1, 2, 3)

-- -----------------------------------------------------
-- 6. Insert RouteAssignments
-- Assign the 'Morning Route - Sector A' (route_id 1)
-- to Vijay (driver_id 3) and his vehicle (vehicle_id 1) for today.
-- -----------------------------------------------------
INSERT INTO `RouteAssignments` (`route_id`, `vehicle_id`, `driver_id`, `assigned_date`, `status`)
VALUES
(1, 1, 3, CURDATE(), 'In Progress');
-- (This will get assignment_id 1)

-- -----------------------------------------------------
-- 7. Insert RouteStops
-- Add the two 'Sector A' bins (point_ids 1, 2) to the route assignment (id 1)
-- -----------------------------------------------------
INSERT INTO `RouteStops` (`assignment_id`, `point_id`, `stop_order`, `status`)
VALUES
(1, 1, 1, 'Completed'), -- (Driver already completed the first stop)
(1, 2, 2, 'Pending'); -- (This is the next stop)

-- -----------------------------------------------------
-- 8. Insert VehicleLocations
-- Add a recent GPS ping for Vijay's vehicle (vehicle_id 1)
-- -----------------------------------------------------
INSERT INTO `VehicleLocations` (`vehicle_id`, `latitude`, `longitude`, `timestamp`)
VALUES
(1, 17.4438, 78.3841, NOW());

-- -----------------------------------------------------
-- 9. Insert ServiceBookings
-- Our client Ananya (user_id 4) books a service for her home (point_id 3)
-- -----------------------------------------------------
INSERT INTO `ServiceBookings` (`client_id`, `point_id`, `service_description`, `requested_date`, `status`)
VALUES
(4, 3, 'Requesting pickup for 3 large bags.', CURDATE() + INTERVAL 1 DAY, 'Approved');
-- (This will get booking_id 1)

-- -----------------------------------------------------
-- 10. Insert Payments
-- Ananya (client_id 4) pays for her booking (booking_id 1)
-- -----------------------------------------------------
INSERT INTO `Payments` (`booking_id`, `client_id`, `amount`, `payment_gateway_txn_id`, `status`, `payment_date`)
VALUES
(1, 4, 150.00, 'txn_a9b8c7d6e5f4', 'Succeeded', NOW());
-- (This will get payment_id 1)

-- -----------------------------------------------------
-- 11. Insert Receipts
-- A receipt is generated for the successful payment (payment_id 1)
-- -----------------------------------------------------
INSERT INTO `Receipts` (`payment_id`, `receipt_number`, `generated_at`, `sent_to_email`)
VALUES
(1, 'RCPT-2025-0001', NOW(), 'ananya.rao@client.com');

-- -----------------------------------------------------
-- 12. Insert Communications
-- Driver Vijay (user_id 3) sends a message to Supervisor Supriya (user_id 2)
-- -----------------------------------------------------
INSERT INTO `Communications` (`sender_id`, `recipient_id`, `message_content`, `sent_at`, `is_read`)
VALUES
(3, 2, 'Heavy traffic near Sector A park. Might be 10 minutes late to the next stop.', NOW(), 0);

-- -----------------------------------------------------
-- 13. Insert AuditLogs
-- Log the action of the supervisor (user_id 2) creating the route (route_id 1)
-- -----------------------------------------------------
INSERT INTO `AuditLogs` (`user_id`, `action`, `details`)
VALUES
(2, 'ROUTE_CREATED', 'Supervisor created new route: Morning Route - Sector A (ID: 1)');