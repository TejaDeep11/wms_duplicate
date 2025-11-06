-- Drop the database if it already exists to start fresh
DROP DATABASE IF EXISTS wms_db;

-- Create the new database
CREATE DATABASE wms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Select the database to use
USE wms_db;

-- -----------------------------------------------------
-- Table `Roles`
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
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `role_id` INT NULL,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  INDEX `idx_email` (`email`),
  CONSTRAINT `fk_users_role`
    FOREIGN KEY (`role_id`)
    REFERENCES `Roles` (`role_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Vehicles` (Cleaned: removed current_driver_id)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Vehicles` (
  `vehicle_id` INT NOT NULL AUTO_INCREMENT,
  `license_plate` VARCHAR(20) NOT NULL UNIQUE,
  `model` VARCHAR(100) NULL,
  `capacity_kg` DECIMAL(10, 2) NULL,
  PRIMARY KEY (`vehicle_id`)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Routes`
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
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `CollectionPoints`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `CollectionPoints` (
  `point_id` INT NOT NULL AUTO_INCREMENT,
  `point_name` VARCHAR(255) NOT NULL,
  `address` TEXT NULL,
  `latitude` DECIMAL(10, 8) NOT NULL,
  `longitude` DECIMAL(11, 8) NOT NULL,
  `client_id` INT NULL,
  PRIMARY KEY (`point_id`),
  CONSTRAINT `fk_point_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `ServiceBookings` (Cleaned: simplified status)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ServiceBookings` (
  `booking_id` INT NOT NULL AUTO_INCREMENT,
  `client_id` INT NOT NULL,
  `point_id` INT NOT NULL,
  `requested_date` DATE NOT NULL,
  `status` ENUM('Approved', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Approved',
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
-- Table `RouteAssignments` (Cleaned: simplified status)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `RouteAssignments` (
  `assignment_id` INT NOT NULL AUTO_INCREMENT,
  `route_id` INT NOT NULL,
  `vehicle_id` INT NOT NULL,
  `driver_id` INT NOT NULL,
  `assigned_date` DATE NOT NULL,
  `status` ENUM('Pending', 'In Progress', 'Completed') NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (`assignment_id`),
  INDEX `idx_assignment_date` (`assigned_date`),
  CONSTRAINT `fk_assignment_route`
    FOREIGN KEY (`route_id`)
    REFERENCES `Routes` (`route_id`),
  CONSTRAINT `fk_assignment_vehicle`
    FOREIGN KEY (`vehicle_id`)
    REFERENCES `Vehicles` (`vehicle_id`),
  CONSTRAINT `fk_assignment_driver`
    FOREIGN KEY (`driver_id`)
    REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `RouteStops` (Cleaned: booking_id included)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `RouteStops` (
  `route_stop_id` INT NOT NULL AUTO_INCREMENT,
  `assignment_id` INT NOT NULL,
  `point_id` INT NOT NULL,
  `booking_id` INT NULL,
  `stop_order` INT NOT NULL,
  `status` ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending',
  `completed_at` TIMESTAMP NULL,
  `verification_gps_lat` DECIMAL(10, 8) NULL,
  `verification_gps_lon` DECIMAL(11, 8) NULL,
  `collected_volume_kg` DECIMAL(10, 2) NULL,
  PRIMARY KEY (`route_stop_id`),
  CONSTRAINT `fk_stop_assignment`
    FOREIGN KEY (`assignment_id`)
    REFERENCES `RouteAssignments` (`assignment_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_stop_point`
    FOREIGN KEY (`point_id`)
    REFERENCES `CollectionPoints` (`point_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_stop_booking`
    FOREIGN KEY (`booking_id`)
    REFERENCES `ServiceBookings` (`booking_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `VehicleLocations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `VehicleLocations` (
  `location_id` BIGINT NOT NULL AUTO_INCREMENT,
  `vehicle_id` INT NOT NULL,
  `latitude` DECIMAL(10, 8) NOT NULL,
  `longitude` DECIMAL(11, 8) NOT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`location_id`),
  INDEX `idx_vehicle_timestamp` (`vehicle_id`, `timestamp` DESC),
  CONSTRAINT `fk_location_vehicle`
    FOREIGN KEY (`vehicle_id`)
    REFERENCES `Vehicles` (`vehicle_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Payments` (Cleaned: simplified status)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Payments` (
  `payment_id` INT NOT NULL AUTO_INCREMENT,
  `booking_id` INT NOT NULL,
  `client_id` INT NOT NULL,
  `amount` DECIMAL(10, 2) NOT NULL,
  `payment_gateway_txn_id` VARCHAR(255) NULL,
  `status` ENUM('Succeeded', 'Failed') NOT NULL DEFAULT 'Succeeded',
  `payment_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  CONSTRAINT `fk_payment_booking`
    FOREIGN KEY (`booking_id`)
    REFERENCES `ServiceBookings` (`booking_id`),
  CONSTRAINT `fk_payment_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `Receipts`
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
-- Table `AuditLogs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AuditLogs` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL,
  `action` VARCHAR(255) NOT NULL,
  `details` TEXT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  CONSTRAINT `fk_audit_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `GroupChatMessages` (Epic 4)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `GroupChatMessages` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT NOT NULL,
  `message_content` TEXT NOT NULL,
  `sent_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`message_id`),
  CONSTRAINT `fk_chat_sender`
    FOREIGN KEY (`sender_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `ClientFeedback` (Epic 4)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ClientFeedback` (
  `feedback_id` INT NOT NULL AUTO_INCREMENT,
  `client_id` INT NOT NULL,
  `booking_id` INT NULL,
  `rating` INT NOT NULL,
  `comment` TEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`feedback_id`),
  CONSTRAINT `fk_feedback_client`
    FOREIGN KEY (`client_id`)
    REFERENCES `Users` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_feedback_booking`
    FOREIGN KEY (`booking_id`)
    REFERENCES `ServiceBookings` (`booking_id`)
    ON DELETE SET NULL
) ENGINE=InnoDB;