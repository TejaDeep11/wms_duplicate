-- Drop the database if it already exists to start fresh
DROP DATABASE IF EXISTS wms_db;

-- Create the new database
CREATE DATABASE wms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Select the database to use
USE wms_db;

-- -----------------------------------------------------
-- Table `Roles`
[cite_start]-- Stores the different user types (Supervisor, Driver, Client, Admin) [cite: 316, 317, 318, 320]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Roles` (
  `role_id` INT NOT NULL AUTO_INCREMENT,
  `role_name` VARCHAR(50) NOT NULL UNIQUE,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB;

-- Insert the basic roles
INSERT INTO `Roles` (`role_name`) VALUES
('Administrator'),
('Supervisor'),
('Driver'),
('Client');

-- -----------------------------------------------------
-- Table `Users`
-- Stores login and profile information for all system actors
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `role_id` INT NULL,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL, -- Store hashed passwords, not plain text
  `phone` VARCHAR(20) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  INDEX `idx_email` (`email`),
  CONSTRAINT `fk_users_role`
    FOREIGN KEY (`role_id`)
    REFERENCES `Roles` (`role_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Vehicles`
[cite_start]-- Stores information about the waste collection fleet [cite: 309]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Vehicles` (
  `vehicle_id` INT NOT NULL AUTO_INCREMENT,
  `license_plate` VARCHAR(20) NOT NULL UNIQUE,
  `model` VARCHAR(100) NULL,
  `capacity_kg` DECIMAL(10, 2) NULL,
  `current_driver_id` INT NULL, -- The driver currently assigned to this vehicle
  PRIMARY KEY (`vehicle_id`),
  CONSTRAINT `fk_vehicle_driver`
    FOREIGN KEY (`current_driver_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Routes`
[cite_start]-- Stores the master templates for routes created by supervisors (US 1.1) [cite: 343]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Routes` (
  `route_id` INT NOT NULL AUTO_INCREMENT,
  `route_name` VARCHAR(255) NOT NULL,
  `created_by_supervisor_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`route_id`),
  CONSTRAINT `fk_route_supervisor`
    FOREIGN KEY (`created_by_supervisor_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `CollectionPoints`
-- Stores predefined locations for waste collection (e.g., client addresses, bins)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `CollectionPoints` (
  `point_id` INT NOT NULL AUTO_INCREMENT,
  `point_name` VARCHAR(255) NOT NULL,
  `address` TEXT NULL,
  `latitude` DECIMAL(10, 8) NOT NULL,
  `longitude` DECIMAL(11, 8) NOT NULL,
  `client_id` INT NULL, -- Link to a specific client if it's a private address
  PRIMARY KEY (`point_id`),
  CONSTRAINT `fk_point_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `RouteAssignments`
-- Stores a specific instance of a route assigned to a driver/vehicle for a day
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `RouteAssignments` (
  `assignment_id` INT NOT NULL AUTO_INCREMENT,
  `route_id` INT NOT NULL,
  `vehicle_id` INT NOT NULL,
  `driver_id` INT NOT NULL,
  `assigned_date` DATE NOT NULL,
  `status` ENUM('Pending', 'In Progress', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
  `optimized_at` TIMESTAMP NULL, -- Timestamp for when US 1.2 (Optimization) was run
  PRIMARY KEY (`assignment_id`),
  INDEX `idx_assignment_date` (`assigned_date`),
  CONSTRAINT `fk_assignment_route`
    FOREIGN KEY (`route_id`)
    REFERENCES `Routes` (`route_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_assignment_vehicle`
    FOREIGN KEY (`vehicle_id`)
    REFERENCES `Vehicles` (`vehicle_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_assignment_driver`
    FOREIGN KEY (`driver_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `RouteStops`
-- Junction table mapping collection points to a specific route assignment, with order
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `RouteStops` (
  `route_stop_id` INT NOT NULL AUTO_INCREMENT,
  `assignment_id` INT NOT NULL,
  `point_id` INT NOT NULL,
  `stop_order` INT NOT NULL, -- Defines the optimized path (US 1.2)
  `status` ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending',
  `completed_at` TIMESTAMP NULL, -- When the driver confirmed collection (US 2.3)
  `verification_gps_lat` DECIMAL(10, 8) NULL, -- GPS data for verification (US 2.4)
  `verification_gps_lon` DECIMAL(11, 8) NULL,
  `collected_volume_kg` DECIMAL(10, 2) NULL, -- For Waste Volume Reporting (US 4.1)
  PRIMARY KEY (`route_stop_id`),
  CONSTRAINT `fk_stop_assignment`
    FOREIGN KEY (`assignment_id`)
    REFERENCES `RouteAssignments` (`assignment_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_stop_point`
    FOREIGN KEY (`point_id`)
    REFERENCES `CollectionPoints` (`point_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `VehicleLocations`
[cite_start]-- Stores real-time and historical GPS data (US 2.1, US 2.2) [cite: 70]
-- NOTE: This table will grow very large. [cite_start]A time-series DB is recommended[cite: 77],
-- but this is the MySQL equivalent.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `VehicleLocations` (
  `location_id` BIGINT NOT NULL AUTO_INCREMENT,
  `vehicle_id` INT NOT NULL,
  `latitude` DECIMAL(10, 8) NOT NULL,
  `longitude` DECIMAL(11, 8) NOT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`location_id`),
  INDEX `idx_vehicle_timestamp` (`vehicle_id`, `timestamp` DESC), -- For fast history lookups
  CONSTRAINT `fk_location_vehicle`
    FOREIGN KEY (`vehicle_id`)
    REFERENCES `Vehicles` (`vehicle_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `ServiceBookings`
-- Stores client requests for service (US 3.1)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ServiceBookings` (
  `booking_id` INT NOT NULL AUTO_INCREMENT,
  `client_id` INT NOT NULL,
  `point_id` INT NOT NULL, -- The location for the service
  `service_description` TEXT NULL,
  `requested_date` DATE NOT NULL,
  `status` ENUM('Pending', 'Approved', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (`booking_id`),
  CONSTRAINT `fk_booking_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_booking_point`
    FOREIGN KEY (`point_id`)
    REFERENCES `CollectionPoints` (`point_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Payments`
[cite_start]-- Stores payment records (US 3.2) [cite: 71, 347]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Payments` (
  `payment_id` INT NOT NULL AUTO_INCREMENT,
  `booking_id` INT NULL, -- Can be linked to a specific booking
  `client_id` INT NOT NULL,
  `amount` DECIMAL(10, 2) NOT NULL,
  `payment_gateway_txn_id` VARCHAR(255) NULL, -- ID from the external gateway
  `status` ENUM('Pending', 'Succeeded', 'Failed') NOT NULL DEFAULT 'Pending',
  `payment_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  CONSTRAINT `fk_payment_booking`
    FOREIGN KEY (`booking_id`)
    REFERENCES `ServiceBookings` (`booking_id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_payment_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Receipts`
[cite_start]-- Stores generated payment receipts (US 3.3) [cite: 347]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Receipts` (
  `receipt_id` INT NOT NULL AUTO_INCREMENT,
  `payment_id` INT NOT NULL,
  `receipt_number` VARCHAR(100) NOT NULL UNIQUE,
  `generated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sent_to_email` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`receipt_id`),
  CONSTRAINT `fk_receipt_payment`
    FOREIGN KEY (`payment_id`)
    REFERENCES `Payments` (`payment_id`)
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Communications`
[cite_start]-- Stores messages between drivers and supervisors (US 5.1, US 5.2) [cite: 354]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Communications` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT NOT NULL,
  `recipient_id` INT NOT NULL,
  `message_content` TEXT NOT NULL,
  `sent_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`message_id`),
  CONSTRAINT `fk_comm_sender`
    FOREIGN KEY (`sender_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_comm_recipient`
    FOREIGN KEY (`recipient_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `AuditLogs`
[cite_start]-- Logs critical system events for auditing (US 5.2, WMS-NF-004) [cite: 356]
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AuditLogs` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL, -- User who performed the action (NULL if system)
  `action` VARCHAR(255) NOT NULL, -- e.g., 'LOGIN_FAILED', 'ROUTE_CREATED', 'PAYMENT_PROCESSED'
  `details` TEXT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  CONSTRAINT `fk_audit_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;