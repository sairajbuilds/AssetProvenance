//SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.2 <0.9.0;

contract AssetProvenance {
    struct ServiceEvent {
        uint date;
        string description;
        address serviceCenter;
    }

    struct Device {
        string model;
        address currentOwner;
        uint warrantyExpiry;
        ServiceEvent[] serviceHistory;
    }

    mapping(string => Device) private devices;

    function registerDevice(string memory serial, string memory _model, uint _warrantyExpiryInSeconds) public {
        require(bytes(devices[serial].model).length == 0, "Device already registered.");
        devices[serial].model = _model;
        devices[serial].currentOwner = msg.sender;
        devices[serial].warrantyExpiry = block.timestamp + _warrantyExpiryInSeconds;
    }

    function transferOwnership(string memory serial, address newOwner) public {
        Device storage device = devices[serial];
        require(device.currentOwner == msg.sender, "Only the owner can transfer ownership.");
        require(block.timestamp < device.warrantyExpiry, "Device warranty expired");
        require((newOwner != address(0)), "Invalid new owner");
        device.currentOwner = newOwner;
    }

    function addServiceEvent(string memory serial, string memory _description) public {
        Device storage device = devices[serial];
        require(device.currentOwner != address(0), "Device not registered");
        device.serviceHistory.push(ServiceEvent({
        date: block.timestamp,
        description: _description,
        serviceCenter: msg.sender
        }));
    }

    function getDevice(string memory serial) public view returns(
        string memory model,
        address currentOwner,
        uint warrantyExpiry,
        uint serviceCount
    ) {
        Device storage device = devices[serial];
        return (
            device.model,
            device.currentOwner,
            device.warrantyExpiry,
            device.serviceHistory.length
        );
    }

    function getServiceEvent(string memory serial, uint index) public view returns (
        uint date,
        string memory description,
        address serviceCenter
        ) {
        Device storage device = devices[serial];
        require(index < device.serviceHistory.length, "Invalid index");
        ServiceEvent storage eventItem = device.serviceHistory[index];
        return (
            eventItem.date,
            eventItem.description,
            eventItem.serviceCenter
        );
    }
}