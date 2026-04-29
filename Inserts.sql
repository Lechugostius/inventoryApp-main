-- Insert test data for Roles
INSERT INTO Roles (Name, Description) VALUES ('Desconocido', 'Role for new users');
INSERT INTO Roles (Name, Description) VALUES ('Admin', 'Administrator role');
INSERT INTO Roles (Name, Description) VALUES ('User', 'Standard user role');
INSERT INTO Roles (Name, Description) VALUES ('Manager', 'Managerial role with additional privileges');

-- Insert test data for Users
INSERT INTO Users (Name, Email, RoleID, AzureUserID) VALUES ('Pablo Arce', 'pgarro@tacobell.cr', 1, '787dbfc8-9824-42f3-83be-087b97b96cb2');
INSERT INTO Users (Name, Email, RoleID, AzureUserID) VALUES ('Jane Smith', 'janesmith@example.com', 3, 'azure-67890');
INSERT INTO Users (Name, Email, RoleID, AzureUserID) VALUES ('Alice Johnson', 'alicej@example.com', 2, 'azure-54321');

-- Insertar datos de Categorías
INSERT INTO Categories (Name) VALUES ('Monitores');
INSERT INTO Categories (Name) VALUES ('Mouse');
INSERT INTO Categories (Name) VALUES ('Impresoras');
INSERT INTO Categories (Name) VALUES ('Nuc');
INSERT INTO Categories (Name) VALUES ('Laptops');
INSERT INTO Categories (Name) VALUES ('Cajones');
INSERT INTO Categories (Name) VALUES ('Teclados');
INSERT INTO Categories (Name) VALUES ('Huellas');
INSERT INTO Categories (Name) VALUES ('DVR');
INSERT INTO Categories (Name) VALUES ('Camaras');
INSERT INTO Categories (Name) VALUES ('UPS');
INSERT INTO Categories (Name) VALUES ('Discos Duros');
INSERT INTO Categories (Name) VALUES ('Tablets');
INSERT INTO Categories (Name) VALUES ('Lectores QR');
INSERT INTO Categories (Name) VALUES ('Brazos');
INSERT INTO Categories (Name) VALUES ('Kioskos');

-- Insertar datos de Estados
INSERT INTO Statuses (Name, Description) VALUES ('Disponible', 'Equipo disponible para asignación');
INSERT INTO Statuses (Name, Description) VALUES ('Reservado', 'Equipo actualmente asignado');
INSERT INTO Statuses (Name, Description) VALUES ('Devuelto', 'Equipo ha sido devuelto');

-- Insertar datos de Proveedores
INSERT INTO Suppliers (Name) VALUES ('CabySis');
INSERT INTO Suppliers (Name) VALUES ('ADN');
INSERT INTO Suppliers (Name) VALUES ('Intelec');
INSERT INTO Suppliers (Name) VALUES ('POS');

-- Insert test data for ItemOwners
INSERT INTO ItemOwners (Name, Description) VALUES ('IT Department', 'Responsible for IT assets');
INSERT INTO ItemOwners (Name, Description) VALUES ('Marketing Department', 'Responsible for marketing assets');
INSERT INTO ItemOwners (Name, Description) VALUES ('HR Department', 'Responsible for office furniture and general items');

-- Insert test data for Items
INSERT INTO Items (Name, Description, CategoryID, UniqueIdentifier, SupplierID, StatusID, Location, Stock, OwnerID) 
VALUES ('Dell Laptop', 'High performance laptop', 1, 'DL-001', 1, 1, 'Office A', 2, 1);
INSERT INTO Items (Name, Description, CategoryID, UniqueIdentifier, SupplierID, StatusID, Location, Stock, OwnerID) 
VALUES ('Wireless Mouse', 'Ergonomic wireless mouse', 2, 'WM-002', 2, 1, 'Office B', 3, 2);
INSERT INTO Items (Name, Description, CategoryID, UniqueIdentifier, SupplierID, StatusID, Location, Stock, OwnerID) 
VALUES ('Office Chair', 'Ergonomic office chair', 3, 'CH-003', 3, 1, 'Office C', 4, 3);

-- Insertar datos de Tipos de Movimiento
INSERT INTO MovementTypes (Name, Description) VALUES ('Cambio', 'Cambio de equipo');
INSERT INTO MovementTypes (Name, Description) VALUES ('Apertura Restaurante', 'Equipo asignado para apertura de restaurante');
INSERT INTO MovementTypes (Name, Description) VALUES ('Otro', 'Otros tipos de movimientos');
INSERT INTO MovementTypes (Name, Description) VALUES ('Entrada', 'Ingreso de equipos al inventario');

-- Insert test data for Movements
INSERT INTO Movements (ItemID, MovementTypeID, Quantity, OriginUserID, ResponsibleUserID, Destination, Notes)
VALUES (1, 1, 1, 1, 2, 'Remote Work', 'Checked out for remote work');
INSERT INTO Movements (ItemID, MovementTypeID, Quantity, OriginUserID, ResponsibleUserID, Destination, Notes)
VALUES (2, 2, 1, 2, 1, 'Office Storage', 'Returned after use');
INSERT INTO Movements (ItemID, MovementTypeID, Quantity, OriginUserID, ResponsibleUserID, Destination, Notes)
VALUES (3, 3, 1, 3, 1, 'Meeting Room', 'Chair moved to meeting room');

-- Insert test data for Files
INSERT INTO Files (ItemID, URL, Type) VALUES (1, 'https://example.com/dell-laptop.png', 'Image');
INSERT INTO Files (ItemID, URL, Type) VALUES (2, 'https://example.com/wireless-mouse.png', 'Image');
INSERT INTO Files (ItemID, URL, Type) VALUES (3, 'https://example.com/office-chair.png', 'Image');

-- Insert test data for ChangeHistory
INSERT INTO ChangeHistory (ItemID, ModifiedField, PreviousValue, NewValue, Date, UserID) 
VALUES (1, 'Location', 'Office A', 'Office B', GETDATE(), 1);
INSERT INTO ChangeHistory (ItemID, ModifiedField, PreviousValue, NewValue, Date, UserID) 
VALUES (2, 'StatusID', '1', '2', GETDATE(), 2);
INSERT INTO ChangeHistory (ItemID, ModifiedField, PreviousValue, NewValue, Date, UserID) 
VALUES (3, 'OwnerID', '2', '3', GETDATE(), 3);
GO
.